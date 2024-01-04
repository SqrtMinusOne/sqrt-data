# [[file:../../../org/mpd.org::*Flow][Flow:1]]
import os
import sys
import logging
import glob

import pandas as pd
from tqdm import tqdm

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert

from sqrt_data_service.api import settings, DBConn, FileHasher
from sqrt_data_service.models import Base
from sqrt_data_service.models.mpd import MpdSong, SongListened
# Flow:1 ends here

# [[file:../../../org/mpd.org::*Flow][Flow:2]]
__init__ = ['load_mpd']
# Flow:2 ends here

# [[file:../../../org/mpd.org::*Loading the library][Loading the library:1]]
def load_library():
    csv_path = os.path.expanduser(settings['mpd']['library_csv'])
    hasher = FileHasher()

    logger = get_run_logger()

    if not hasher.is_updated(csv_path):
        logger.info('MPD library already saved, skipping')
        return

    logger.info('Saving MPD Library')
    df = pd.read_csv(csv_path)
    DBConn.create_schema('mpd', Base)

    with DBConn.get_session() as db:
        tracks = list(df.itertuples(index=False))

        song_data = []
        for track in tqdm(tracks):
            track = track._asdict()
            song_datum = {k:v for k, v in track.items() if k in MpdSong.__table__.columns.keys()}
            if pd.isna(song_datum['year']):
                song_datum['year'] = None
            song_data.append(song_datum)

        insert_stmt = pg_insert(MpdSong)
        upsert_stmt = insert_stmt.on_conflict_do_update(
            constraint='MpdSong_file_key',
            set_={
                'duration': insert_stmt.excluded.duration,
                'artist': insert_stmt.excluded.artist,
                'album_artist': insert_stmt.excluded.album_artist,
                'album': insert_stmt.excluded.album,
                'title': insert_stmt.excluded.title,
                'year': insert_stmt.excluded.year,
                'musicbrainz_trackid': insert_stmt.excluded.musicbrainz_trackid
            }
        )

        db.execute(upsert_stmt.values(song_data))
        hasher.save_hash(csv_path, db)
        db.commit()

        logger.info(f'Saved {len(song_data)} records')
# Loading the library:1 ends here

# [[file:../../../org/mpd.org::*Loading the logs][Loading the logs:1]]
def get_logs_to_put():
    folder = os.path.expanduser(settings['mpd']['log_folder'])
    logs = glob.glob(f"{folder}/*.csv")
    hasher = FileHasher()
    with DBConn.get_session() as db:
        return [log for log in logs if hasher.is_updated(log, db)]
# Loading the logs:1 ends here

# [[file:../../../org/mpd.org::*Loading the logs][Loading the logs:2]]
def put_log(filename):
    logger = get_run_logger()
    logger.info('Reading %s', filename)
    df = pd.read_csv(filename)
    records = df.to_dict(orient='records')
    all_found = True
    hasher = FileHasher()
    with DBConn.get_session() as db:
        for record in tqdm(records):
            if record['type'] == 'skipped':
                continue
            song = db.execute(
                sa.select(MpdSong).where(MpdSong.file == record['file'])
            ).scalar_one_or_none()
            if song:
                listened = SongListened(song_id=song.id, time=record['time'])
                db.merge(listened)
            else:
                logger.error('Song %s not found', record['file'])
                all_found = False
        if all_found:
            hasher.save_hash(filename, db)
        db.commit()
# Loading the logs:2 ends here

# [[file:../../../org/mpd.org::*Post-processing][Post-processing:2]]
MPD_VIEW = """
drop view if exists mpd."MpdSongListened";
create view mpd."MpdSongListened" as
select
    S.title title,
    S.album album,
    S.album_artist artist,
    S.duration::float4 / 60 duration,
    S.year "year",
    L.time "time"
from mpd."SongListened" L
left join mpd."MpdSong" S ON L.song_id = S.id
order by time asc;
"""

def create_views():
    DBConn.engine.execute(MPD_VIEW)
# Post-processing:2 ends here

# [[file:../../../org/mpd.org::*Flow][Flow:1]]
def load_mpd():
    DBConn()
    logger = get_run_logger()

    load_library()
    logs = get_logs_to_put()
    logger.info(f'Found unprocessed logs: {len(logs)}')
    for log in logs:
        put_log(log)

    create_views()
# Flow:1 ends here
