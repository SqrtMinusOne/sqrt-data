# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):1]]
import json
import pandas as pd

from tqdm import tqdm

from sqrt_data.api import settings, DBConn, HashDict
from sqrt_data.models import Base
from sqrt_data.parse.locations import LocationMatcher
# Loading (Android):1 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):2]]
__all__ = ['load_android']
# Loading (Android):2 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):3]]
def get_dataframes(h):
    if not h.is_updated(settings["aw"]["android_file"]):
        print('Android already loaded')
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
# Loading (Android):3 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):4]]
def get_records(type_, df):
    loc = LocationMatcher()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    locations = df.apply(
        lambda row: loc.get_location(row.timestamp, row.hostname), axis=1
    )
    df['location'] = [l[0] for l in locations]
    df['timestamp'] = [l[1] for l in locations]
    return df
# Loading (Android):4 ends here

# [[file:../../../org/aw.org::*Loading (Android)][Loading (Android):5]]
TABLE_NAMES = {
    'os.lockscreen.unlocks': 'android_unlock',
    'currentwindow': 'android_currentwindow'
}

def load_android():
    DBConn()
    DBConn.create_schema('aw', Base)

    with HashDict() as h:
        dfs_by_type = get_dataframes(h)

        for type_, df in tqdm(dfs_by_type.items()):
            df = get_records(type_, df)
            df.to_sql(
                TABLE_NAMES[type_],
                schema=settings['aw']['schema'],
                con=DBConn.engine,
                if_exists='replace'
            )
            print(df)
        h.save_hash(settings["aw"]["android_file"])
        h.commit()
# Loading (Android):5 ends here
