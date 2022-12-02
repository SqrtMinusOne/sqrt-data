# [[file:../org/mpd.org::*Storing the library][Storing the library:1]]
import os
import dateutil
import pandas as pd
import numpy as np

from mpd import MPDClient
from sqrt_data_agent.api import settings
# Storing the library:1 ends here

# [[file:../org/mpd.org::*Storing the library][Storing the library:2]]
def get_year(datum):
    try:
        if datum['originaldate']:
            return dateutil.parser.parse(datum['originaldate']).year
    except TypeError:
        pass
    if datum['date']:
        try:
            return dateutil.parser.parse(datum['date']).year
        except TypeError:
            pass
    return None
# Storing the library:2 ends here

# [[file:../org/mpd.org::*Storing the library][Storing the library:3]]
def save_library():
    mpd = MPDClient()
    mpd.connect("localhost", 6600)

    data = mpd.listallinfo()
    data = [datum for datum in data if 'directory' not in datum]
    df = pd.DataFrame(data)

    df['year'] = df.apply(get_year, axis=1)
    df.duration = df.time
    df['album_artist'] = df.albumartist

    csv_path = os.path.expanduser(settings['mpd']['library_csv'])

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    df.to_csv(csv_path, index=False)

if __name__ == '__main__':
    save_library()
# Storing the library:3 ends here
