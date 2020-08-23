import pandas as pd
import sys
import os
import glob
from tqdm import tqdm
import logging

from api import DBConn, is_updated, save_hash, Config
from models import Base, MpdSong, SongListened


__all__ = ['put_logs']


def get_logs_to_put():
    folder = os.path.expanduser(Config.MPD_LOG_FOLDER)
    logs = glob.glob(f"{folder}/*.csv")
    return [log for log in logs if is_updated(log)]


def put_log(filename):
    logging.info('Reading %s', filename)
    df = pd.read_csv(filename)
    records = df.to_dict(orient='records')
    with DBConn.get_session() as db:
        for record in tqdm(records):
            if record['type'] == 'skipped':
                continue
            song = db.query(MpdSong).filter_by(file=record['file']).first()
            listened = SongListened(song_id=song.id, time=record['time'])
            db.merge(listened)
        db.commit()
    save_hash(filename)


def put_logs():
    logs = get_logs_to_put()
    if len(logs) == 0:
        logging.info('All logs are saved')
        sys.exit(0)
    DBConn()
    DBConn.create_schema('mpd', Base)
    for log in logs:
        put_log(log)