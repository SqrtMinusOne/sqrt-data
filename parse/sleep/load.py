import pandas as pd
import copy
import re
import os
from dateutil import parser
from datetime import datetime, timedelta, time
from collections import deque
import logging

from api import is_updated, save_hash, DBConn, Config

__all__ = ['load']

KEY_SEQ = 'Id'
NUM_COLS = set([
    'Id', 'Hours', 'Rating', 'Framerate', 'Snore', 'Noise', 'Cycles',
    'DeepSleep', 'LenAdjust'
])
DATE = '%d. %m. %Y %H:%M'
SCHEMA = 'sleep'

FILE = os.path.expanduser(Config.SLEEP_FILE)
GEOS = Config.SLEEP_GEOS


def get_tags(comment):
    tags = re.findall('#\S+', comment)
    for i, tag in enumerate(tags):
        comment = comment.replace(tag, '')
        tags[i] = tag[1:]
    comment = comment.strip()
    return tags, comment


def parse_event(event):
    values = event.split('-')
    return {
        'kind': values[0],
        'timestamp': int(values[1]),
        'time': datetime.utcfromtimestamp(int(values[1]) / 1000),
        'data': values[2:]
    }


def parse_csv_dict(lines):
    keys = None
    result = []
    for line in lines:
        if line.endswith('\n'):
            line = line[:-1]
        if keys is None:
            if line.startswith(KEY_SEQ):
                keys = line.split(',')
            else:
                continue
        else:
            row = {}
            events = []
            times = {}
            data = line.split(',')
            for key, datum in zip(keys, data):
                if datum.startswith('"'):
                    datum = datum[1:-1]
                if key.startswith('"'):
                    key = key[1:-1]
                if key == 'Event':
                    events.append(parse_event(datum))
                elif re.fullmatch(r'^\d+:\d+$', key):
                    times[key] = float(datum)
                elif key == 'From' or key == 'To' or key == 'Sched':
                    row[key] = datetime.strptime(datum, DATE)
                elif key == 'Id':
                    row['Id'] = int(datum)
                elif key in NUM_COLS:
                    row[key] = float(datum)
                elif key == 'Comment':
                    tags, comment = get_tags(datum)
                    row[key] = comment
                    row['tags'] = tags
                elif key == 'Geo':
                    row[key] = GEOS.get(datum, datum)
                else:
                    row[key] = datum
            row['events'] = sorted(events, key=lambda evt: evt['timestamp'])
            row['times'] = times
            keys = None
            result.append(row)
    result = sorted(result, key=lambda datum: datum['From'])
    return result


def merge_data(data):
    data = copy.deepcopy(data)
    i, k = 0, 1
    result = []
    while i < len(data) - 1:
        a = data[i]
        b = data[i + k]
        if (b['From'] - a['To']) < timedelta(seconds=60 * 20):
            logging.info('Merged %s %s', b['From'], a['To'])
            data[i] = {
                'merged':
                True,
                'Comment':
                b['Comment'],
                'Cycles':
                a['Cycles'] + b['Cycles'],
                'DeepSleep':
                (a['DeepSleep'] * a['Hours'] + b['DeepSleep'] * b['Hours']) /
                (a['Hours'] + b['Hours']),
                'Framerate':
                b['Framerate'],
                'From':
                a['From'],
                'Geo':
                b['Geo'],
                'Hours':
                a['Hours'] + b['Hours'],
                'Id':
                a['Id'],
                'LenAdjust':
                b['LenAdjust'],
                'Noise':
                max(a['Noise'], b['Noise']),
                'Rating':
                b['Rating'],
                'Sched':
                a['Sched'],
                'Snore':
                max(a['Snore'], b['Snore']),
                'To':
                b['To'],
                'Tz':
                b['Tz'],
                'events':
                sorted([*a['events'], *b['events']],
                       key=lambda evt: evt['timestamp']),
                'tags':
                list(set([*a['tags'], *b['tags']])),
                'times': {
                    **a['times'],
                    **b['times']
                }
            }
            k += 1
        else:
            result.append(data[i])
            i += k
            k = 1
    return result


def get_dfs(data):
    data_main = deque()
    data_events = deque()
    data_times = deque()
    for datum in data:
        datum = {key.lower(): value for key, value in datum.items()}
        for event in datum['events']:
            data_events.append({**event, 'sleep_id': datum['id']})
        for time_, value in datum['times'].items():
            data_times.append({
                'time': datetime.strptime(time_, '%H:%M').time(),
                'value': value,
                'sleep_id': datum['id']
            })
        del datum['events']
        del datum['times']
        data_main.append(datum)
    df_main, df_events, df_times = pd.DataFrame(data_main), pd.DataFrame(
        data_events), pd.DataFrame(data_times)
    df_main['merged'] = df_main['merged'].apply(lambda d: d == True)
    df_main['cycles'] = df_main['cycles'].apply(lambda c: c if c > 0 else None)
    df_main['deepsleep'] = df_main['deepsleep'].apply(lambda d: d
                                                      if d > 0 else None)
    return df_main, df_events, df_times


def load():
    DBConn()
    DBConn.engine.execute(f'CREATE SCHEMA IF NOT EXISTS {SCHEMA}')
    if not is_updated(FILE):
        logging.info('Sleep alreay loaded')
        return
    with open(FILE, 'r') as f:
        lines = f.readlines()

    data = parse_csv_dict(lines)
    logging.info('Parsed records: %d', len(data))
    data = merge_data(data)
    logging.info('Records after merge: %d', len(data))

    df_main, df_events, df_times = get_dfs(data)
    logging.info('Events: %d, Times: %d', len(df_events), len(df_times))

    df_main.to_sql('main', schema=SCHEMA, con=DBConn.engine, if_exists='replace')
    df_events.to_sql('events', schema=SCHEMA, con=DBConn.engine, if_exists='replace')
    df_times.to_sql('times', schema=SCHEMA, con=DBConn.engine, if_exists='replace')
    save_hash(FILE)
