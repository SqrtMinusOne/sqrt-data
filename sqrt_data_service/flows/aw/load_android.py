# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):1]]
import json
import pandas as pd

from tqdm import tqdm
from prefect import task, flow, get_run_logger

from sqrt_data_service.api import settings, DBConn, FileHasher
from sqrt_data_service.models import Base
from sqrt_data_service.common.locations import LocationMatcher
# Loading (Android):1 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):2]]
@task(name='aw-android-get-dataframes')
def get_dataframes(db):
    logger = get_run_logger()
    hasher = FileHasher()
    if not hasher.is_updated(settings["aw"]["android_file"], db):
        logger.info('Android already loaded')
        return
    dfs_by_type = {}
    with open(settings["aw"]["android_file"], 'r') as f:
        data = json.load(f)
        buckets = data['buckets']
        for bucket in buckets.values():
            df = pd.DataFrame(
                [
                    {
                        'id': f"{bucket['id']}-{event['id']}",
                        'bucket_id': bucket['id'],
                        'hostname': bucket['hostname'],
                        'duration': event['duration'],
                        'timestamp': pd.Timestamp(event['timestamp']),
                        **event['data'],
                    } for event in bucket['events']
                ]
            )
            df = df.set_index('id')
            dfs_by_type[bucket['type']] = df
    return dfs_by_type
# Loading (Android):2 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):3]]
@task(name='aw-android-get-records')
def get_records(type_, df):
    loc = LocationMatcher()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    locations = df.apply(
        lambda row: loc.get_location(row.timestamp, row.hostname), axis=1
    )
    df['location'] = [l[0] for l in locations]
    df['timestamp'] = [l[1] for l in locations]
    return df
# Loading (Android):3 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):4]]
TABLE_NAMES = {
    'os.lockscreen.unlocks': 'android_unlock',
    'currentwindow': 'android_currentwindow'
}

@flow
def aw_load_android():
    DBConn()
    DBConn.create_schema('aw', Base)

    hasher = FileHasher()
    with DBConn.get_session() as db:
        dfs_by_type = get_dataframes(db)

        if dfs_by_type is None:
            return

        for type_, df in tqdm(dfs_by_type.items()):
            df = get_records(type_, df)
            df.to_sql(
                TABLE_NAMES[type_],
                schema=settings['aw']['schema'],
                con=DBConn.engine,
                if_exists='replace'
            )
            print(df)
        hasher.save_hash(settings["aw"]["android_file"])
        db.commit()
# Loading (Android):4 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):5]]
if __name__ == '__main__':
    aw_load_android()
# Loading (Android):5 ends here