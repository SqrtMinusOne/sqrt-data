# [[file:../../../org/mpd.org::*Loading the logs][Loading the logs:1]]
import pandas as pd
import sys
import os
import glob
from tqdm import tqdm
import logging

from sqrt_data.api import DBConn, HashDict, settings
from sqrt_data.models import Base
from sqrt_data.models.mpd import MpdSong, SongListened
# Loading the logs:1 ends here

# [[file:../../../org/mpd.org::*Loading the logs][Loading the logs:2]]
__all__ = ['load_logs']
# Loading the logs:2 ends here

# [[file:../../../org/mpd.org::*Loading the logs][Loading the logs:3]]
def get_logs_to_put():
    folder = os.path.expanduser(settings['mpd']['log_folder'])
    logs = glob.glob(f"{folder}/*.csv")
    with HashDict() as h:
        return [log for log in logs if h.is_updated(log)]
# Loading the logs:3 ends here

# [[file:../../../org/mpd.org::*Loading the logs][Loading the logs:4]]
def put_log(filename):
    logging.info('Reading %s', filename)
    df = pd.read_csv(filename)
    records = df.to_dict(orient='records')
    all_found = True
    with HashDict() as h:
        with DBConn.get_session() as db:
            for record in tqdm(records):
                if record['type'] == 'skipped':
                    continue
                song = db.query(MpdSong).filter_by(file=record['file']).first()
                if song:
                    listened = SongListened(song_id=song.id, time=record['time'])
                    db.merge(listened)
                else:
                    logging.error('Song %s not found', record['file'])
                    all_found = False
            db.commit()
        if all_found:
            h.save_hash(filename)
            h.commit()
# Loading the logs:4 ends here

# [[file:../../../org/mpd.org::*Loading the logs][Loading the logs:5]]
def load_logs():
    logs = get_logs_to_put()
    if len(logs) == 0:
        logging.info('All logs are saved')
        sys.exit(0)
    DBConn()
    for log in logs:
        put_log(log)
# Loading the logs:5 ends here
