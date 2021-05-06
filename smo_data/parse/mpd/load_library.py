import os
import sys
import logging

import pandas as pd
from tqdm import tqdm

from smo_data.api import is_updated, save_hash, DBConn, Config
from smo_data.models import Base, MpdSong

__all__ = ['load_library']

CSV_PATH = os.path.expanduser(Config.MPD_CSV)

def load_library():
    if not is_updated(CSV_PATH):
        logging.info('MPD library already saved, skipping')
        sys.exit(0)
    logging.info('Saving MPD Library')
    df = pd.read_csv(CSV_PATH)
    DBConn()
    DBConn.create_schema('mpd', Base)

    with DBConn.get_session() as db:
        tracks = list(df.itertuples(index=False))
        for track in tqdm(tracks):
            track = track._asdict()
            song = MpdSong(**{k:v for k, v in track.items() if k in MpdSong.__table__.columns.keys()})

            added = db.query(MpdSong).filter_by(file=track['file']).first()
            if not added:
                db.merge(song)
        db.commit()
    save_hash(CSV_PATH)


if __name__ == "__main__":
    load_library()
