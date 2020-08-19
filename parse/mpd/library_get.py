import pandas as pd
import sys
import dateutil
import os
from mpd import MPDClient
from tqdm import tqdm

mpd = MPDClient()
mpd.connect("localhost", 6600)

data = mpd.listallinfo()
data = [datum for datum in data if 'directory' not in datum]
df = pd.DataFrame(data)

CSV_PATH = os.path.expanduser('~/logs-sync/mpd/mpd_library.csv')

def get_year(datum):
    if datum['originaldate']:
        return dateutil.parser.parse(datum['originaldate']).year
    if datum['date']:
        return dateutil.parser.parse(datum['date']).year
    return None

df['year'] = df.apply(get_year, axis=1)
df.duration = df.time
df['album_artist'] = df.albumartist

os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)

df.to_csv(CSV_PATH, index=False)
