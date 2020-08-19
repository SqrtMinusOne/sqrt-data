import os
import sys

from api import is_updated, save_hash, DBConn
from models import Base, MpdSong
from .library_get import CSV_PATH


__all__ = ['put_library']


def put_library():
    if not is_updated(CSV_PATH):
        exit(0)
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


if __name__ == "__main__":
    put_library()
