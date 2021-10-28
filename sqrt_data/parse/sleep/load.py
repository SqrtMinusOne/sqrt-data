# [[file:../../../org/sleep.org::*Parse the data][Parse the data:1]]
import copy
import logging
import re
from collections import deque
from datetime import datetime, timedelta

import pandas as pd

from sqrt_data.api import settings, DBConn, HashDict
# Parse the data:1 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:2]]
__all__ = ['load']
# Parse the data:2 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:3]]
KEY_SEQ = 'Id'
NUM_COLS = set(
    [
        'Id', 'Hours', 'Rating', 'Framerate', 'Snore', 'Noise', 'Cycles',
        'DeepSleep', 'LenAdjust'
    ]
)
# Parse the data:3 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:4]]
DATE = '%d. %m. %Y %H:%M'
# Parse the data:4 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:5]]
def get_tags(comment):
    tags = re.findall('#\S+', comment)
    for i, tag in enumerate(tags):
        comment = comment.replace(tag, '')
        tags[i] = tag[1:]
    comment = comment.strip()
    return tags, comment
# Parse the data:5 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:6]]
def parse_event(event):
    values = event.split('-')
    return {
        'kind': values[0],
        'timestamp': int(values[1]),
        'time': datetime.utcfromtimestamp(int(values[1]) / 1000),
        'data': values[2:]
    }
# Parse the data:6 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:7]]
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
                    row[key] = settings['sleep']['geos'].get(datum, datum)
                else:
                    row[key] = datum
            row['events'] = sorted(events, key=lambda evt: evt['timestamp'])
            row['times'] = times
            keys = None
            result.append(row)
    result = sorted(result, key=lambda datum: datum['From'])
    return result
# Parse the data:7 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:8]]
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
                    (a['DeepSleep'] * a['Hours'] + b['DeepSleep'] * b['Hours'])
                    / (a['Hours'] + b['Hours']),
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
                    sorted(
                        [*a['events'], *b['events']],
                        key=lambda evt: evt['timestamp']
                    ),
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
# Parse the data:8 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:9]]
def get_dfs(data):
    data_main = deque()
    data_events = deque()
    data_times = deque()
    for datum in data:
        datum = {key.lower(): value for key, value in datum.items()}
        for event in datum['events']:
            data_events.append({**event, 'sleep_id': datum['id']})
        for time_, value in datum['times'].items():
            data_times.append(
                {
                    'time': datetime.strptime(time_, '%H:%M').time(),
                    'value': value,
                    'sleep_id': datum['id']
                }
            )
        del datum['events']
        del datum['times']
        data_main.append(datum)
    df_main, df_events, df_times = pd.DataFrame(data_main), pd.DataFrame(
        data_events
    ), pd.DataFrame(data_times)
    df_main['merged'] = df_main['merged'].apply(lambda d: d == True)
    df_main['cycles'] = df_main['cycles'].apply(lambda c: c if c > 0 else None)
    df_main['deepsleep'] = df_main['deepsleep'].apply(
        lambda d: d if d > 0 else None
    )
    return df_main, df_events, df_times
# Parse the data:9 ends here

# [[file:../../../org/sleep.org::*Parse the data][Parse the data:11]]
CONSTRAINTS = """
ALTER TABLE sleep.main DROP CONSTRAINT IF EXISTS main_pk;
ALTER TABLE sleep.main ADD CONSTRAINT main_pk PRIMARY KEY (id);
ALTER TABLE sleep.events DROP CONSTRAINT IF EXISTS events_sleep_fk;
ALTER TABLE sleep.times DROP CONSTRAINT IF EXISTS events_times_fk;
ALTER TABLE sleep.events ADD CONSTRAINT events_sleep_fk FOREIGN KEY (sleep_id) REFERENCES sleep.main(id);
ALTER TABLE sleep.times ADD CONSTRAINT times_sleep_fk FOREIGN KEY (sleep_id) REFERENCES sleep.main(id);
"""

def load():
    schema = settings['sleep']['schema']
    DBConn()
    DBConn.engine.execute(f'DROP SCHEMA IF EXISTS {schema} CASCADE')
    DBConn.engine.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')

    with HashDict() as h:
        if not h.is_updated(settings['sleep']['file']):
            logging.info('Sleep alreay loaded')
            return
        with open(settings['sleep']['file'], 'r') as f:
            lines = f.readlines()

        data = parse_csv_dict(lines)
        logging.info('Parsed records: %d', len(data))
        data = merge_data(data)
        logging.info('Records after merge: %d', len(data))

        df_main, df_events, df_times = get_dfs(data)
        df_main = df_main.set_index('id')
        logging.info('Events: %d, Times: %d', len(df_events), len(df_times))

        df_main.to_sql(
            'main', schema=schema, con=DBConn.engine, if_exists='replace'
        )
        df_events.to_sql(
            'events', schema=schema, con=DBConn.engine, if_exists='replace'
        )
        df_times.to_sql(
            'times', schema=schema, con=DBConn.engine, if_exists='replace'
        )
        DBConn.engine.execute(CONSTRAINTS)
        h.save_hash(settings['sleep']['file'])
        h.commit()
# Parse the data:11 ends here