# [[file:../../../org/wakatime.org::*Flow][Flow:1]]
import base64
import os
import requests
import pandas as pd
import json
import logging
from collections import deque
from tqdm import tqdm

from sqrt_data_service.api import settings, DBConn, FileHasher
from sqrt_data_service.common.projects import (
    ProjectMatcher,
    fix_project_name,
    get_project_id,
)
# Flow:1 ends here

# [[file:../../../org/wakatime.org::*Flow][Flow:2]]
__all__ = ['wakatime', 'wakatime_file']
# Flow:2 ends here

# [[file:../../../org/wakatime.org::*Download dump][Download dump:1]]
def download_wakatime_dump():
    key = base64.b64encode(str.encode(settings["waka"]["api_key"])
                          ).decode('utf-8')
    headers = {'Authorization': f'Basic {key}'}
    r = requests.get(
        f'{settings["waka"]["api_url"]}/users/current/datadumps',
        headers=headers
    )
    data = r.json()['data']
    if len(data) == 0:
        logging.info('No WakaTime dumps found')
        return None

    dump_data = data[0]
    if dump_data['status'] != 'Completed':
        logging.info('Dump not completed')
        return None

    filename = f'wakatime-{dump_data["created_at"]}.json'
    path = os.path.join(
        os.path.expanduser(settings['general']['temp_data_folder']), filename
    )
    if os.path.exists(path):
        logging.info('File already downloaded')
        return path
    os.makedirs(
        os.path.expanduser(settings['general']['temp_data_folder']),
        exist_ok=True
    )

    dump = requests.get(dump_data['download_url'])
    with open(path, 'wb') as f:
        f.write(dump.content)
    logging.info('WakaTime dump downloaded to %s', filename)
    return path
# Download dump:1 ends here

# [[file:../../../org/wakatime.org::*Parse dump][Parse dump:1]]
def parse_wakatime_dump(data):
    deques = {}

    matcher = ProjectMatcher()
    for day in tqdm(data['days']):
        date = day['date']
        for project in day['projects']:
            name = fix_project_name(project['name'])
            root_project = matcher.get_project(name) or "unknown"

            for key, date_data in project.items():
                if key == 'name':
                    continue
                try:
                    data_deque = deques[key]
                except KeyError:
                    data_deque = deque()
                    deques[key] = data_deque
                if key == 'grand_total':
                    data_deque.append(
                        {
                            "date": date,
                            "project": name,
                            "root_project": root_project,
                            **date_data
                        }
                    )
                else:
                    for datum in date_data:
                        data_deque.append(
                            {
                                "date": date,
                                "project": name,
                                "root_project": root_project,
                                **datum
                            }
                        )

    dfs = {name: pd.DataFrame(data) for name, data in deques.items()}
    for name, df in dfs.items():
        df['total_minutes'] = df['total_seconds'] / 60
        df['date'] = pd.to_datetime(df['date'])
        # df['date'] = df['date'].apply(lambda dt: dt.date())
        df = df.drop(['total_seconds'], axis=1)
        dfs[name] = df
    return dfs
# Parse dump:1 ends here

# [[file:../../../org/wakatime.org::*Parse dump][Parse dump:2]]
def get_tree_df(df):
    matcher = ProjectMatcher()
    tree_data = {}
    levels_per_item = {}
    for datum in df.itertuples(index=False):
        name = fix_project_name(datum.project)
        path = matcher.get_path(name)
        if path is None:
            path = ["00 Unknown"]
        for level, item in enumerate(path):
            date = datum.date
            levels_per_item[item] = level
            try:
                tree_data[item][date] += datum.total_minutes
            except KeyError:
                try:
                    tree_data[item][date] = datum.total_minutes
                except KeyError:
                    tree_data[item] = {date: datum.total_minutes}
    tree_list = []
    for item, dates in tree_data.items():
        for date, minutes in dates.items():
            tree_list.append(
                {
                    "name": item,
                    "date": date,
                    "total_minutes": minutes,
                    "level": levels_per_item[item],
                    "is_project": matcher.get_is_project(item),
                    "project_id": get_project_id(item)
                }
            )
    return pd.DataFrame(tree_list)
# Parse dump:2 ends here

# [[file:../../../org/wakatime.org::*Store dump][Store dump:1]]
def store_wakatime_dump(dfs):
    DBConn.create_schema(settings['waka']['schema'])
    for name, df in tqdm(dfs.items()):
        df.to_sql(
            name,
            schema=settings['waka']['schema'],
            con=DBConn.engine,
            if_exists='replace'
        )
        print(df)
    logging.info('WakaTime data stored')
# Store dump:1 ends here

# [[file:../../../org/wakatime.org::*Store dump][Store dump:2]]
def wakatime():
    DBConn()
    hasher = FileHasher()

    dump_file = download_wakatime_dump()
    if dump_file is None:
        return

    if hasher.is_updated(dump_file) is False:
        logging.info('Dump already processed')
        return

    with open(dump_file, 'r') as f:
        data = json.load(f)

    dfs = parse_wakatime_dump(data)
    tree_df = get_tree_df(df['grand_total'])
    dfs['tree'] = tree_df
    store_wakatime_dump(dfs)
    hasher.save_hash(dump_file)
# Store dump:2 ends here

# [[file:../../../org/wakatime.org::*Store dump][Store dump:3]]
def wakatime_file(dump_file):
    DBConn()
    with open(dump_file, 'r') as f:
        data = json.load(f)

    dfs = parse_wakatime_dump(data)
    tree_df = get_tree_df(dfs['grand_total'])
    dfs['tree'] = tree_df
    store_wakatime_dump(dfs)
# Store dump:3 ends here
