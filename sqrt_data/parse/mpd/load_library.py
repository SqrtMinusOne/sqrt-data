# [[file:../../../org/mpd.org::*Loading the library][Loading the library:1]]
import os
import sys
import logging

import pandas as pd
from tqdm import tqdm

from sqrt_data.api import HashDict, DBConn, settings
from sqrt_data.models import Base
from sqrt_data.models.mpd import MpdSong
# Loading the library:1 ends here

# [[file:../../../org/mpd.org::*Loading the library][Loading the library:2]]
__all__ = ['load_library']
# Loading the library:2 ends here

# [[file:../../../org/mpd.org::*Loading the library][Loading the library:3]]
def load_library():
    csv_path = os.path.expanduser(settings['mpd']['library_csv'])
    with HashDict() as h:
        if not h.is_updated(csv_path):
            logging.info('MPD library already saved, skipping')
            return

        logging.info('Saving MPD Library')
        df = pd.read_csv(csv_path)
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
        h.save_hash(csv_path)
        h.commit()
# Loading the library:3 ends here
