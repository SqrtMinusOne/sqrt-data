import contextlib
import numpy as np
import pandas as pd
import sqlalchemy as sa
import sqlite3

from datetime import datetime

from .api import get_video_by_id, get_video_id, store_logs
from sqrt_data.models.youtube import Watch, NewPipeMeta
from sqrt_data.api import HashDict, DBConn, settings

__all__ = ['parse_newpipe']

def parse_timestamp(timestamp):
    ts = int(timestamp // 1000)
    return pd.Timestamp(datetime.utcfromtimestamp(ts).date())

SQLITE_QUERY = """
SELECT S.url, S.duration, SS.progress_time / 1000 progress, SH.access_date, SH.repeat_count
FROM streams S
         INNER JOIN stream_history SH on S.uid = SH.stream_id
         LEFT JOIN stream_state SS on S.uid = SS.stream_id
WHERE S.url like '%youtube%'
ORDER BY access_date
"""


def get_newpipe_data():
    with contextlib.closing(
        sqlite3.connect(settings['youtube']['newpipe_db'])
    ) as con:
        with con as cur:
            data = cur.execute(SQLITE_QUERY).fetchall()
            df = pd.DataFrame(
                data,
                columns=['url', 'duration', 'progress', 'date', 'repeat_count']
            )
            df.date = df.date.apply(parse_timestamp)
            df['video_id'] = df.url.apply(get_video_id)
            df = df.drop(['url'], axis=1)
            return df

AW_QUERY = """
SELECT date(timestamp) date, sum(duration) duration
FROM aw.android_currentwindow ACW
WHERE ACW.app = 'NewPipe'
GROUP BY date
ORDER BY date
"""

def get_aw_data(db):
    return pd.read_sql(AW_QUERY, db, parse_dates=['date'])

DURATION_THRESHOLDS = [1200, 600, 300, 0]


def fix_durations(group):
    group = group.copy(deep=True)
    group.progress = group.progress.fillna(group.duration_np)
    time_spent = group.iloc[0].duration_aw
    threshold_idx = 0
    while group.progress.sum() >= time_spent:
        time_extra = group.progress.sum() - time_spent
        over_thresh = group[
            group.duration_np >= DURATION_THRESHOLDS[threshold_idx]]
        time_thresh = over_thresh.progress.sum()
        if time_thresh >= time_extra:

            def _fix_progress(datum):
                if datum.duration_np >= DURATION_THRESHOLDS[threshold_idx]:
                    prop = datum.progress / time_thresh
                    return datum.progress - time_extra * prop
                else:
                    return datum.progress

            group.progress = group.apply(_fix_progress, axis=1)
            break
        else:
            threshold_idx += 1
    return group


def parse_newpipe_day(db, group):
    new_group = fix_durations(group)
    res = []
    for datum in new_group.itertuples(index=False):
        meta = db.query(NewPipeMeta).filter_by(video_id=datum.video_id).first()
        if meta and meta.access_date == datum.date:
            print(f'Found saved: {meta.video_id}')
            continue
        res.append(
            {
                'video_id': datum.video_id,
                'date': datum.date.isoformat(),
                'kind': 'newpipe',
                'duration': datum.progress
            }
        )
    if len(res) == 0:
        return
    store_logs(res, db)
    added_ids = set([r['video_id'] for r in res])
    for orig_datum in group.itertuples(index=False):
        if orig_datum.video_id not in added_ids:
            continue
        db.merge(
            NewPipeMeta(
                video_id=orig_datum.video_id,
                access_date=datum.date.isoformat(),
                progress=orig_datum.progress,
                repeat_count=orig_datum.repeat_count
            )
        )
        db.flush()

def parse_newpipe():
    with HashDict() as h:
        if not h.is_updated(settings['youtube']['newpipe_db']):
            print('NewPipe already loaded')
            return
    DBConn()
    df_aw = get_aw_data(DBConn.engine)
    df_np = get_newpipe_data()
    df = pd.merge(df_np, df_aw, on='date', suffixes=('_np', '_aw'))

    with HashDict() as h:
        with DBConn.get_session() as db:
            i = 0
            for _, group in df.groupby('date'):
                parse_newpipe_day(db, group)
                db.commit()
        h.save_hash(settings['youtube']['newpipe_db'])
        h.commit()
