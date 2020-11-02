import pandas as pd
from datetime import timedelta
from urllib.parse import urlparse, parse_qs
import re
import os

from api import DBConn, Config


SOURCE = os.path.expanduser(Config.ANDROID_FILE)
SCHEMA = 'android'


__all__ = ['load_android']


def fix_time(time):
    # TODO
    time = time + timedelta(hours=3)
    return time


def get_app_id(datum):
    try:
        if pd.notna(datum['titleUrl']):
            q = parse_qs(urlparse(datum['titleUrl']).query)
            return q['id'][0]
    except KeyError:
        pass
    try:
        if datum['title'].startswith('Used'):
            return ' '.join(datum['title'].split(' ')[1:])
    except KeyError:
        pass
    return datum['header']


def fix_name(name):
    if name.startswith('com.'):
        tokens = name.split('.')
        return ' '.join([t[0].upper() + t[1:] for t in tokens[1:]])
    name = re.sub(r'(:|-|—|–).*$', '', name)
    name = re.sub(r'\(.*\)', '', name)
    name = name.strip()
    return name


def align_time(time):
    time = time.replace(minute=time.minute // 30 * 30, second=0, microsecond=0)
    return time


def parse_android():
    df = pd.read_json(SOURCE)
    df = df.drop(['products', 'details'], axis=1)

    df.time = pd.to_datetime(df.time)
    df.time = df.time.apply(fix_time)

    df['app_id'] = df.apply(get_app_id, axis=1)

    app_names = {
        app_name: fix_name(group.iloc[0]['header'])
        for app_name, group in df.groupby('app_id')
    }
    df['app_name'] = df.app_id.apply(lambda id_: app_names[id_])
    df.time = df.time.apply(align_time)

    dfg = df.groupby(['app_name', 'time']) \
            .agg(lambda x: x.iloc[0]) \
            .reset_index() \
            .sort_values('time', ascending=False) \
            .reset_index(drop=True)
    dfg = dfg.drop(['title', 'titleUrl'], axis=1)
    return dfg


def load_android():
    df = parse_android()
    DBConn()
    DBConn.engine.execute(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA}')

    df.to_sql('Usage', schema=SCHEMA, con=DBConn.engine, if_exists='replace')