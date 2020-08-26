import json
import logging
import os
from collections import deque

import pandas as pd
import requests

from api import Config

__all__ = ['get_buckets']

API = 'http://localhost:5600/api'

def get_last_updated():
    data = {}
    if os.path.exists(os.path.expanduser(Config.AW_LAST_UPDATED)):
        with open(os.path.expanduser(Config.AW_LAST_UPDATED), 'r') as f:
            data = json.load(f)
    return data

def save_last_updated(data):
    os.makedirs(os.path.dirname(os.path.expanduser(Config.AW_LAST_UPDATED)), exist_ok=True)
    with open(os.path.expanduser(Config.AW_LAST_UPDATED), 'w') as f:
        json.dump(data, f)

def get_data(bucket_id, last_updated=None):
    params = {}
    if last_updated:
        params['start'] = last_updated
    r = requests.get(f'{API}/0/buckets/{bucket_id}')
    bucket = r.json()
    r = requests.get(f'{API}/0/buckets/{bucket_id}/events', params=params)
    data = deque()
    for event in r.json():
        data.append({
            'id': event['id'],
            'bucket_id': bucket['id'],
            'hostname': bucket['hostname'],
            'duration': event['duration'],
            'timestamp': pd.Timestamp(event['timestamp']),
            **event['data']
        })
    if len(data) > 0:
        df = pd.DataFrame(data)
        df = df.set_index('id')
        return df
    return None


def get_buckets():
    r = requests.get(f'{API}/0/buckets')
    buckets = r.json()
    last_updated = get_last_updated()
    os.makedirs(os.path.expanduser(Config.AW_LOGS_FOLDER), exist_ok=True)
    for bucket in buckets.values():
        if not bucket['type'] in Config.AW_TYPES:
            continue
        if bucket['last_updated'] == last_updated.get(bucket['id'], None):
            logging.info('Bucket %s already saved', bucket['id'])
            continue
        df = get_data(bucket['id'], last_updated.get(bucket['id'], None))
        last_updated[bucket['id']] = bucket['last_updated']
        if df is None:
            logging.info('Bucket %s is empty', bucket['id'])
            continue
        filename = os.path.join(
            os.path.expanduser(Config.AW_LOGS_FOLDER),
            f"{bucket['type']}-{bucket['hostname']}-{bucket['last_updated']}.csv"
        )
        df.to_csv(filename)
        logging.info('Saved %s with %s events', filename, len(df))
    save_last_updated(last_updated)
