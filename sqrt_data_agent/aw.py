# [[file:../org/aw.org::*Saving (Desktop)][Saving (Desktop):1]]
import socket
import argparse
import json
import logging
import os
from collections import deque
from datetime import datetime

import pandas as pd
import requests
import furl

from sqrt_data_agent.api import settings
# Saving (Desktop):1 ends here

# [[file:../org/aw.org::*Saving (Desktop)][Saving (Desktop):2]]
def get_last_updated():
    data = {}
    if os.path.exists(os.path.expanduser(settings['aw']['last_updated'])):
        with open(os.path.expanduser(settings['aw']['last_updated']), 'r') as f:
            data = json.load(f)
    # return data.get(f'last_updated-{get_hostname()}', None)
    return data


def save_last_updated(data):
    os.makedirs(
        os.path.dirname(os.path.expanduser(settings['aw']['last_updated'])),
        exist_ok=True
    )
    hostname = socket.gethostname()
    data[f'last_updated-{hostname}'] = datetime.now().isoformat()
    with open(os.path.expanduser(settings['aw']['last_updated']), 'w') as f:
        json.dump(data, f)
# Saving (Desktop):2 ends here

# [[file:../org/aw.org::*Saving (Desktop)][Saving (Desktop):3]]
def get_data(bucket_id, last_updated=None):
    params = {}
    api = settings['aw']['api']
    if last_updated:
        params['start'] = last_updated
    r = requests.get(f'{api}/0/buckets/{bucket_id}')
    bucket = r.json()
    r = requests.get(f'{api}/0/buckets/{bucket_id}/events', params=params)
    data = deque()
    for event in r.json():
        hostname = bucket['hostname']
        if hostname == 'unknown':
            hostname = socket.gethostname()
        data.append(
            {
                'id': f"{bucket_id}-{event['id']}",
                'bucket_id': bucket['id'],
                'hostname': bucket['hostname'],
                'duration': event['duration'],
                'timestamp': pd.Timestamp(event['timestamp']),
                **event['data']
            }
        )
    if len(data) > 0:
        df = pd.DataFrame(data)
        df = df.set_index('id')
        return df
    return None
# Saving (Desktop):3 ends here

# [[file:../org/aw.org::*Saving (Desktop)][Saving (Desktop):4]]
def save_buckets(force=False):
    last_updated = get_last_updated()
    hostname = socket.gethostname()
    last_updated_time = last_updated.get(f'last_updated-{hostname}', None)
    if last_updated_time is not None:
        last_updated_date = datetime.fromisoformat(last_updated_time).date()
        if (datetime.now().date() == last_updated_date and not force):
            logging.info('Already loaded AW today')
            return
    r = requests.get(f'{settings["aw"]["api"]}/0/buckets')
    buckets = r.json()

    os.makedirs(
        os.path.expanduser(settings['aw']['logs_folder']), exist_ok=True
    )
    for bucket in buckets.values():
        if not bucket['type'] in settings['aw']['types']:
            continue
        if 'aw-watcher-web' in bucket['id']:
            last_updated_id = f'{bucket["id"]}-{socket.gethostname()}'
        else:
            last_updated_id = bucket['id']
        if bucket['last_updated'] == last_updated.get(last_updated_id, None):
            logging.info('Bucket %s already saved', bucket['id'])
            continue
        df = get_data(bucket['id'], last_updated.get(last_updated_id, None))
        last_updated[last_updated_id] = bucket['last_updated']
        if df is None:
            logging.info('Bucket %s is empty', bucket['id'])
            continue
        bucket_type = bucket['type'].replace('.', '_')
        hostname = bucket['hostname']
        if hostname == 'unknown':
            hostname = socket.gethostname()
        filename = os.path.join(
            os.path.expanduser(settings['aw']['logs_folder']),
            f"{bucket_type}-{hostname}-{bucket['last_updated']}.csv"
        )
        df.to_csv(filename)
        logging.info('Saved %s with %s events', filename, len(df))
    save_last_updated(last_updated)
# Saving (Desktop):4 ends here

# [[file:../org/aw.org::*Saving (Desktop)][Saving (Desktop):5]]
def main():
    parser = argparse.ArgumentParser(
        prog='sqrt_data_agent.aw'
    )
    parser.add_argument('-f', '--force', action='store_true')
    args = parser.parse_args()
    save_buckets(args.force)

if __name__ == '__main__':
    main()
# Saving (Desktop):5 ends here
