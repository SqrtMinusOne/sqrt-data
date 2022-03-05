import pandas as pd
import sqlalchemy as sa
import json

from tqdm import tqdm

from .api import get_video_by_id, get_video_id, store_logs
from sqrt_data.models.aw import CurrentWindow
from sqrt_data.models.youtube import Watch
from sqrt_data.api import HashDict, DBConn, settings

__all__ = ['parse_youtube']

AW_DATES_QUERY = """
SELECT DISTINCT date(timestamp) date FROM aw.currentwindow
"""

ANDROID_DATES_QUERY = """
SELECT DISTINCT date(timestamp) FROM aw.android_currentwindow
WHERE app = 'YouTube'
"""

ANDROID_USAGE_QUERY = """
SELECT date(timestamp) date, sum(duration) duration FROM aw.android_currentwindow
WHERE app = 'YouTube'
GROUP BY date
ORDER BY date
"""


def get_data(db):
    df_bd = pd.read_sql(AW_DATES_QUERY, db)
    aw_dates = set(df_bd.date)

    df_ad = pd.read_sql(ANDROID_DATES_QUERY, db)
    android_dates = set(df_ad.date)

    df_a = pd.read_sql(ANDROID_USAGE_QUERY, db, parse_dates=['date'])

    return aw_dates, android_dates, df_a

def prepare_history_df(db):
    df_h = pd.read_json(settings['youtube']['browser_history'])
    duration = []
    progress = []
    for datum in df_h.itertuples(index=False):
        video, new = get_video_by_id(datum.id, db)
        # if new:
        #     db.flush()
        duration.append(video.duration)
        progress.append(((datum.progress - 10) / 90) * video.duration)
    df_h['duration'] = duration
    df_h['progress'] = progress
    df_h['date'] = df_h.date.apply(lambda d: d.date())

    unique_videos = {
        index: count
        for index, count in df_h.id.value_counts().items()
    }
    df_h['count_v'] = df_h.id.apply(lambda i: unique_videos[i])
    df_h = df_h[(df_h.progress > 0) | (df_h.count_v > 1)]
    df_h = df_h.drop(['channel'], axis=1)
    df_h['orig_progress'] = df_h.progress
    df_h.progress = df_h.progress / df_h.count_v
    return df_h

def process_clear_dates(df_h, browser_dates, android_dates, res):
    clear_dates = df_h.date.apply(
        lambda d: d not in browser_dates and d not in android_dates
    )
    df_clear = df_h[clear_dates]
    df_h = df_h[~clear_dates]

    for item in df_clear.itertuples(index=False):
        res.append({
            'video_id': item.id,
            'date': item.date.isoformat(),
            'kind': 'youtube',
            'duration': item.duration
        })
    return df_h, res

def get_browser_duration(df_h, browser_dates, db):
    browser_video_data = []
    video_ids = set()
    for datum in tqdm(list(df_h.itertuples(index=False))):
        if datum.date not in browser_dates:
            continue
        if datum.id in video_ids:
            continue
        video, _ = get_video_by_id(datum.id, db)
        video_name = video.name.replace("'", "''")
        duration = db.execute(
            f'''SELECT date(timestamp) date, app, title, sum(duration) duration
            FROM aw.currentwindow
            WHERE title ILIKE '%{video_name}%' AND app != 'mpv'
            GROUP BY date(timestamp), app, title
            '''
        )
        browser_video_data.extend(
            {
                'video_id': datum.id,
                'date': e[0],
                'app': e[1],
                'title': e[2],
                'duration': e[3]
            }
            for e in duration
        )
        video_ids.add(datum.id)
    return pd.DataFrame(browser_video_data)

def process_browser_duration(df_h, df_b, res):
    browser_groups = {id: group for id, group in df_b.groupby('video_id')}
    remaining = []

    for id, group in df_h.groupby('id'):
        try:
            browser_data = browser_groups[id]
        except KeyError:
            remaining.extend(group.to_dict('records'))
            continue

        res.extend(
            {
                'video_id': datum.video_id,
                'date': datum.date,
                'duration': datum.duration,
                'kind': f'youtube-{datum.app}'
            } for datum in browser_data.itertuples(index=False)
            if datum.duration > 30
        )

        orig_progress = group.iloc[0].orig_progress
        if orig_progress >= group.duration.sum() * 1.1 and orig_progress > 30:
            remaining.extend(
                {
                    **item, 'orig_progress': orig_progress,
                    'progress': orig_progress / item.count_v
                } for item in group.to_dict('records')
            )
    return pd.DataFrame(remaining), res

DURATION_THRESHOLDS = [1200, 600, 300, 0]


def fix_durations(group, max_duration):
    group = group.copy(deep=True)
    group.progress = group.orig_progress
    threshold_idx = 0
    while group.progress.sum() >= max_duration:
        time_extra = group.progress.sum() - max_duration
        over_thresh = group[group.progress >= DURATION_THRESHOLDS[threshold_idx]]
        time_thresh = over_thresh.progress.sum()

        if time_thresh >= time_extra:

            def _fix_progress(datum):
                if datum.duration >= DURATION_THRESHOLDS[threshold_idx]:
                    prop = datum.progress / time_thresh
                    return datum.progress - time_extra * prop
                else:
                    return datum.progress

            group.progress = group.apply(_fix_progress, axis=1)
            break
        else:
            threshold_idx += 1
    return group

def process_android_dates(df_h, android_dates, df_a, res):
    is_android = df_h.date.apply(lambda d: d in android_dates)
    df_android = df_h[is_android]

    err_dates = set()

    for date, group in df_android.groupby('date'):
        try:
            max_duration = df_a[df_a.date == date.isoformat()].duration.iloc[0]
        except IndexError:
            err_dates.add(date)
            continue
        group = fix_durations(group, max_duration)
        for item in group.itertuples(index=False):
            res.append(
                {
                    'video_id': item.id,
                    'date': item.date.isoformat(),
                    'kind': 'youtube-android',
                    'duration': item.duration
                }
            )

    df_h = df_h[[not a for a in is_android]]
    res.extend(
        {
            'video_id':
                datum.id,
            'date':
                datum.date.isoformat(),
            'kind':
                'youtube-android' if datum.date not in err_dates else 'youtube',
            'duration':
                datum.duration
        } for datum in df_h.itertuples(index=False)
    )
    return res

def process_history(db):
    browser_dates, android_dates, df_a = get_data(DBConn.engine)

    df_h = prepare_history_df(db)
    df_h, res = process_clear_dates(df_h, browser_dates, android_dates, [])

    df_b = get_browser_duration(df_h, browser_dates, db)
    # df_b.to_csv('browser-duration.csv')
    # df_b = pd.read_csv('browser-duration.csv')
    df_h, res = process_browser_duration(df_h, df_b, res)
    res = process_android_dates(df_h, android_dates, df_a, res)

    df = pd.DataFrame(res)
    df.duration = df.duration.astype(int)
    db.flush()
    db.execute("DELETE FROM youtube.watch WHERE kind like 'youtube%'")
    for datum in df.itertuples(index=False):
        db.merge(Watch(
            video_id=datum.video_id,
            date=datum.date,
            kind=datum.kind,
            duration=int(datum.duration)
        ))
    db.commit()

def parse_youtube():
    DBConn()
    with DBConn.get_session() as db:
        process_history(db)
