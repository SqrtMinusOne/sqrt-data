import pandas as pd
import dateutil
import os
from mpd import MPDClient

from api import Config

__all__ = ['to_csv']

CSV_PATH = os.path.expanduser(Config.MPD_CSV)


def get_year(datum):
    try:
        if datum['originaldate']:
            return dateutil.parser.parse(datum['originaldate']).year
    except TypeError:
        pass
    if datum['date']:
        return dateutil.parser.parse(datum['date']).year
    return None


def to_csv():
    mpd = MPDClient()
    mpd.connect("localhost", 6600)

    data = mpd.listallinfo()
    data = [datum for datum in data if 'directory' not in datum]
    df = pd.DataFrame(data)

    df['year'] = df.apply(get_year, axis=1)
    df.duration = df.time
    df['album_artist'] = df.albumartist

    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    df.to_csv(CSV_PATH, index=False)


if __name__ == "__main__":
    to_csv()
