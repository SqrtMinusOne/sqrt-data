import logging
import glob
import json
import os
from collections import deque

import pandas as pd
from tqdm import tqdm

from smo_data.api import Config, DBConn, is_updated, save_hash

SCHEMA = 'wakatime'

__all__ = ['load']


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
                    data_deque.append({
                        "date": date,
                        "project": name,
                        **date_data
                    })
                else:
                    for datum in date_data:
                        data_deque.append({
                            "date": date,
                            "project": name,
                            **datum
                        })

    dfs = {name: pd.DataFrame(data) for name, data in deques.items()}
    for name, df in dfs.items():
        df['total_minutes'] = df['total_seconds'] / 60
        df['date'] = pd.to_datetime(df['date'])
        # df['date'] = df['date'].apply(lambda dt: dt.date())
        df = df.drop(['total_seconds'], axis=1)
        dfs[name] = df
    return dfs


def get_dump_file():
    files = glob.glob(
        f'{os.path.expanduser(Config.TEMP_DATA_FOLDER)}/wakatime*.json'
    )
    if len(files) == 0:
        logging.info('No WakaTime dumps found')
        return None

    files = sorted(files)

    dump = files[-1]
    if not is_updated(dump):
        logging.info('Dump already loaded')
        return None
    return dump

def load():
    DBConn()
    DBConn.engine.execute(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA}')

    dump = get_dump_file()
    if dump is None:
        return

    with open(dump, 'r') as f:
        data = json.load(f)

    dfs = get_dfs(data)

    for name, df in tqdm(dfs.items()):
        df.to_sql(name, schema=SCHEMA, con=DBConn.engine, if_exists='replace')
        print(df)
    save_hash(dump)
