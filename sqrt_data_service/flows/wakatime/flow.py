# [[file:../../../org/wakatime.org::*Flow][Flow:1]]
import base64
import os
import requests
import pandas as pd
import json
from collections import deque
from prefect import task, flow, get_run_logger
from tqdm import tqdm

from sqrt_data_service.api import settings, DBConn, FileHasher
# Flow:1 ends here

# [[file:../../../org/wakatime.org::*Download dump][Download dump:1]]
@task
def download_wakatime_dump():
    logger = get_run_logger()
    key = base64.b64encode(str.encode(settings["waka"]["api_key"])
                          ).decode('utf-8')
    headers = {'Authorization': f'Basic {key}'}
    r = requests.get(
        f'{settings["waka"]["api_url"]}/users/current/datadumps',
        headers=headers
    )
    data = r.json()['data']
    if len(data) == 0:
        logger.info('No WakaTime dumps found')
        return None

    dump_data = data[0]
    if dump_data['status'] != 'Completed':
        logger.info('Dump not completed')
        return None

    filename = f'wakatime-{dump_data["created_at"]}.json'
    path = os.path.join(
        os.path.expanduser(settings['general']['temp_data_folder']), filename
    )
    if os.path.exists(path):
        logger.info('File already downloaded')
        return path
    os.makedirs(
        os.path.expanduser(settings['general']['temp_data_folder']),
        exist_ok=True
    )

    dump = requests.get(dump_data['download_url'])
    with open(path, 'wb') as f:
        f.write(dump.content)
    logger.info('WakaTime dump downloaded to %s', filename)
    return path
# Download dump:1 ends here

# [[file:../../../org/wakatime.org::*Parse dump][Parse dump:1]]
@task
def parse_wakatime_dump(data):
    deques = {}

    for day in tqdm(data['days']):
        date = day['date']
        for project in day['projects']:
            name = project['name']
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
                            **date_data
                        }
                    )
                else:
                    for datum in date_data:
                        data_deque.append(
                            {
                                "date": date,
                                "project": name,
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

# [[file:../../../org/wakatime.org::*Store dump][Store dump:1]]
@task
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
# Store dump:1 ends here

# [[file:../../../org/wakatime.org::*Store dump][Store dump:2]]
@flow
def wakatime():
    DBConn()
    hasher = FileHasher()
    logger = get_run_logger()

    dump_file = download_wakatime_dump()
    if dump_file is None:
        return

    if hasher.is_updated(dump_file) is False:
        logger.info('Dump already processed')
        return

    with open(dump_file, 'r') as f:
        data = json.load(f)

    dfs = parse_wakatime_dump(data)
    store_wakatime_dump(dfs)
    hasher.save_hash(dump_file)
# Store dump:2 ends here

# [[file:../../../org/wakatime.org::*Store dump][Store dump:3]]
if __name__ == '__main__':
    wakatime()
# Store dump:3 ends here
