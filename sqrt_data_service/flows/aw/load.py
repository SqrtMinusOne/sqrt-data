# [[file:../../../org/aw.org::*Loading (Desktop)][Loading (Desktop):1]]
import furl
import tldextract
import glob
import pandas as pd
import os
import re
import logging

from sqlalchemy.dialects.postgresql import insert as pg_insert
from prefect import task, flow, get_run_logger
from tqdm import tqdm

from sqrt_data_service.api import settings, DBConn, FileHasher
from sqrt_data_service.models import Base
from sqrt_data_service.models.aw import AfkStatus, CurrentWindow, AppEditor, WebTab
from sqrt_data_service.common.locations import LocationMatcher
# Loading (Desktop):1 ends here

# [[file:../../../org/aw.org::*Loading (Desktop)][Loading (Desktop):2]]
@task(name='aw-desktop-get-dataframes')
def get_dataframes(db):
    logger = get_run_logger()
    files = glob.glob(
        f'{os.path.expanduser(settings["aw"]["logs_folder"])}/*.csv'
    )
    dfs_by_type = {}
    files_by_type = {}
    hasher = FileHasher()
    for f in files:
        if not hasher.is_updated(f, db):
            continue
        try:
            df = pd.read_csv(f, lineterminator='\n', index_col=False)
        except pd.errors.ParserError:
            logging.error(f'Error parsing file: {f}')
            continue
        type_ = re.search(r'^\w+', os.path.basename(f)).group(0)
        try:
            dfs_by_type[type_].append(df)
            files_by_type[type_].append(f)
        except KeyError:
            dfs_by_type[type_] = [df]
            files_by_type[type_] = [f]
        hasher.save_hash(f, db)
    for type, files in files_by_type.items():
        logger.info(f'{type}: {"; ".join(files)}')
    return dfs_by_type
# Loading (Desktop):2 ends here

# [[file:../../../org/aw.org::*Loading (Desktop)][Loading (Desktop):3]]
MODELS = {
    'afkstatus': AfkStatus,
    'currentwindow': CurrentWindow,
    'app_editor_activity': AppEditor,
    'web_tab_current': WebTab
}
# Loading (Desktop):3 ends here

# [[file:../../../org/aw.org::*Loading (Desktop)][Loading (Desktop):4]]
@task(name='aw-desktop-get-records')
def get_records(type_, df):
    loc = LocationMatcher()
    if type_ == 'afkstatus':
        df['status'] = df['status'] == 'not-afk'
    if type_ == 'currentwindow':
        df['app'] = df['app'].apply(
            lambda app: settings['aw']['apps_convert'].get(app, app)
        )
    if type_ == 'web_tab_current':
        df = df.rename({'tabCount': 'tab_count'}, axis=1)
        df['site'] = [
            tldextract.extract(url).registered_domain
            for url in df['url']
        ]
        df['url_no_params'] = [
            furl.furl(url).remove(args=True, fragment=True).url
            for url in df['url']
        ]
    if type_ == 'app_editor_activity':
        if 'branch' in df.columns:
            df = df.drop('branch', axis=1)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    locations = df.apply(
        lambda row: loc.get_location(row.timestamp, row.hostname), axis=1
    )
    df['location'] = [l[0] for l in locations]
    df['timestamp'] = [l[1] for l in locations]
    return df.to_dict(orient='records')
# Loading (Desktop):4 ends here

# [[file:../../../org/aw.org::*Loading (Desktop)][Loading (Desktop):5]]
@task(name='aw-desktop-insert-data')
def insert_data(type_, entries, db):
    db.execute(
        pg_insert(MODELS[type_]).values(entries).on_conflict_do_nothing()
    )
# Loading (Desktop):5 ends here

# [[file:../../../org/aw.org::*Loading (Desktop)][Loading (Desktop):6]]
@flow
def aw_load_desktop():
    DBConn()
    DBConn.create_schema('aw', Base)
    logger = get_run_logger()
    with DBConn.get_session() as db:
        dfs_by_type = get_dataframes(db)

        for type_, dfs in tqdm(dfs_by_type.items()):
            for df in dfs:
                entries = get_records(type_, df)
                insert_data(type_, entries, db)
                logger.info(f'Inserted {len(entries)} records of type "{type_}"')
        db.commit()
# Loading (Desktop):6 ends here

# [[file:../../../org/aw.org::*Loading (Desktop)][Loading (Desktop):7]]
if __name__ == '__main__':
    aw_load_desktop()
# Loading (Desktop):7 ends here
