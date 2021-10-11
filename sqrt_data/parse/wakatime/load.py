# [[file:../../../org/wakatime.org::*Parse the data][Parse the data:1]]
import logging
import glob
import json
import os
from collections import deque

import pandas as pd
from tqdm import tqdm

from sqrt_data.api import settings, DBConn, HashDict
# Parse the data:1 ends here

# [[file:../../../org/wakatime.org::*Parse the data][Parse the data:2]]
__all__ = ['load']
# Parse the data:2 ends here

# [[file:../../../org/wakatime.org::*Parse the data][Parse the data:3]]
def get_dump_file():
    files = glob.glob(
        f'{os.path.expanduser(settings["general"]["temp_data_folder"])}/wakatime*.json'
    )
    if len(files) == 0:
        logging.info('No WakaTime dumps found')
        return None

    files = sorted(files)
    hashes = HashDict()

    dump = files[-1]
    if not hashes.is_updated(dump):
        logging.info('Dump already loaded')
        return None
    return dump
# Parse the data:3 ends here

# [[file:../../../org/wakatime.org::*Parse the data][Parse the data:4]]
def get_dfs(data):
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
# Parse the data:4 ends here

# [[file:../../../org/wakatime.org::*Parse the data][Parse the data:5]]
def load():
    DBConn()
    DBConn.create_schema(settings['waka']['schema'])

    dump = get_dump_file()
    if dump is None:
        return

    with open(dump, 'r') as f:
        data = json.load(f)

    dfs = get_dfs(data)

    with HashDict() as h:
        for name, df in tqdm(dfs.items()):
            df.to_sql(
                name,
                schema=settings['waka']['schema'],
                con=DBConn.engine,
                if_exists='replace'
            )
            print(df)
        h.save_hash(dump)
        h.commit()
# Parse the data:5 ends here
