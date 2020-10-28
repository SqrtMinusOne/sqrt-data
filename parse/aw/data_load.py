import glob
import pandas as pd
import os
import re
from tqdm import tqdm
import logging

from api import Config, DBConn, is_updated, save_hash


SCHEMA = 'aw'

__all__ = ['load_data']


def load_data(dry_run=False):
    files = glob.glob(
        f'{os.path.expanduser(Config.AW_LOGS_FOLDER)}/*.csv'
    )
    dfs_by_type = {}
    for f in files:
        if not is_updated(f):
            continue
        try:
            df = pd.read_csv(f, lineterminator='\n', index_col=False)
        except pd.errors.ParserError:
            if dry_run:
                print(f'Error parsing file: {f}')
            else:
                logging.error(f'Error parsing file: {f}')
            continue
        type_ = re.search(r'^\w+', os.path.basename(f)).group(0)
        try:
            dfs_by_type[type_].append(df)
        except KeyError:
            dfs_by_type[type_] = [df]
        if not dry_run:
            save_hash(f)
        else:
            print(f'Read: {f}')

    if not dry_run:
        DBConn()
        for type_, dfs in tqdm(dfs_by_type.items()):
            for df in dfs:
                df.to_sql(
                    type_,
                    schema=SCHEMA,
                    con=DBConn.engine,
                    if_exists='append',
                    index=False
                )
