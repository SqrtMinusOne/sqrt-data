import glob
import pandas as pd
import os
import re
from tqdm import tqdm

from api import Config, DBConn, is_updated, save_hash


SCHEMA = 'aw'

__all__ = ['load_data']

def load_data():
    files = glob.glob(
        f'{os.path.expanduser(Config.AW_LOGS_FOLDER)}/*.csv'
    )
    dfs_by_type = {}
    for f in files:
        if not is_updated(f):
            continue
        df = pd.read_csv(f)
        type_ = re.search(r'^\w+', os.path.basename(f)).group(0)
        try:
            dfs_by_type[type_].append(df)
        except KeyError:
            dfs_by_type[type_]= [df]
        save_hash(f)

    DBConn()
    for type_, dfs in tqdm(dfs_by_type.items()):
        for df in dfs:
            df.to_sql(type_, schema=SCHEMA, con=DBConn.engine, if_exists='append')
