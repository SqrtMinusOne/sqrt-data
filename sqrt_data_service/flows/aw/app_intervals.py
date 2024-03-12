# [[file:../../../org/aw.org::*App Interval][App Interval:1]]
from tqdm import tqdm
from sqrt_data_service.api import settings, DBConn

import sqlalchemy as sa
import pandas as pd
# App Interval:1 ends here

# [[file:../../../org/aw.org::*App Interval][App Interval:2]]
__all__ = ['process_app_intervals']
# App Interval:2 ends here

# [[file:../../../org/aw.org::*App Interval][App Interval:3]]
def extract_data(db=None):
    apps = ', '.join([f"'{app}'" for app in settings.aw.app_interval.apps])
    sql = f"SELECT app, timestamp FROM aw.notafkwindow WHERE app in ({apps}) ORDER BY timestamp ASC"
    with DBConn.ensure_session(db) as db:
        data = db.execute(sa.text(sql)).all()

    app_timestamps = {}
    for app, timestamp in data:
        try:
            app_timestamps[app].append(timestamp)
        except KeyError:
            app_timestamps[app] = [timestamp]
    return app_timestamps
# App Interval:3 ends here

# [[file:../../../org/aw.org::*App Interval][App Interval:4]]
def process_data(app_timestamps):
    time_by_day = {}
    for app, timestamps in app_timestamps.items():
        intervals = []
        start = timestamps[0]
        end = timestamps[0]
        for timestamp in tqdm(timestamps[1:]):
            delta = (timestamp - end).total_seconds()
            if delta > settings.aw.app_interval.interval:
                if end > start:
                    intervals.append((start, end))
                start = timestamp
                end = timestamp
            else:
                end = timestamp
        if end > start:
            intervals.append((start, end))

        time_by_day[app] = {}
        for start, end in intervals:
            date = start.date()
            delta = (end - start).total_seconds()
            try:
                time_by_day[app][date] += delta
            except KeyError:
                time_by_day[app][date] = delta
    return time_by_day
# App Interval:4 ends here

# [[file:../../../org/aw.org::*App Interval][App Interval:5]]
def save_data(time_by_day):
    data = []
    for app, times_per_app in time_by_day.items():
        for date, seconds in times_per_app.items():
            data.append((app, date, seconds))
    df = pd.DataFrame(data, columns=["app", "date", "seconds"])
    df.to_sql(
        "intervals",
        schema=settings["aw"]["schema"],
        con=DBConn.engine,
        if_exists="replace",
    )
# App Interval:5 ends here

# [[file:../../../org/aw.org::*App Interval][App Interval:6]]
def process_app_intervals():
    DBConn()
    with DBConn.get_session() as db:
        raw_data = extract_data(db)
        time_by_day = process_data(raw_data)
        save_data(time_by_day)
# App Interval:6 ends here
