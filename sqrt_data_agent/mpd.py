# [[file:../org/mpd.org::*Logging][Logging:1]]
import csv
import logging
import os
import socket
import sys
import time
from datetime import datetime, timedelta

from mpd import MPDClient

from sqrt_data_agent.api import settings
# Logging:1 ends here

# [[file:../org/mpd.org::*Logging][Logging:2]]
def get_lock(process_name):
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    try:
        get_lock._lock_socket.bind('\0' + process_name)
        logging.info('Got the lock')
    except socket.error:
        logging.info('Lock already exists, exiting')
        sys.exit()
# Logging:2 ends here

# [[file:../org/mpd.org::*Logging][Logging:3]]
def get_log_filename():
    return os.path.join(
        settings.mpd.log_folder,
        f'{datetime.now().strftime("%Y-%m-%d")}-{socket.gethostname()}-log.csv'
    )
# Logging:3 ends here

# [[file:../org/mpd.org::*Logging][Logging:4]]
def write_song(song):
    time_listened = (datetime.now() - song['start_time']).seconds
    duration = float(song['duration'])
    if (time_listened / duration > settings.mpd.listened_threshold):
        evt_type = 'listened'
    else:
        evt_type = 'skipped'

    event = {
        'file': song['file'],
        'artist': song.get('artist', ''),
        'album_artist': song.get('albumartist', ''),
        'title': song.get('title', ''),
        'album': song.get('album'),
        'time': song['start_time'].isoformat(' ', 'seconds'),
        'type': evt_type,
        **{attr: song.get(attr, '')
           for attr in settings.mpd.custom_attrs}
    }

    fieldnames = event.keys()
    log_file = get_log_filename()
    log_exists = os.path.exists(log_file)
    mode = 'a' if log_exists else 'w'
    with open(log_file, mode) as f:
        writer = csv.DictWriter(f, fieldnames)
        if not log_exists:
            writer.writeheader()
            logging.info('Initialized CSV log')
        writer.writerow(event)
        logging.info('Saved an entry')
# Logging:4 ends here

# [[file:../org/mpd.org::*Logging][Logging:5]]
def get_current_song(mpd: MPDClient):
    status = mpd.status()
    song = mpd.currentsong()
    if song and status['state'] != 'stop':
        time_elapsed = float(status['elapsed'])
        song['start_time'] = datetime.now() - timedelta(
            seconds=int(time_elapsed))
        return song
    return None
# Logging:5 ends here

# [[file:../org/mpd.org::*Logging][Logging:6]]
current_song = None

def watch(mpd: MPDClient):
    global current_song

    while True:
        song = get_current_song(mpd)

        if not current_song:
            current_song = song
        elif not song or (song and song['file'] != current_song['file']):
            write_song(current_song)
            current_song = song

        mpd.idle('player')
# Logging:6 ends here

# [[file:../org/mpd.org::*Logging][Logging:7]]
def connect():
    mpd = MPDClient()
    mpd.connect('localhost', 6600)
    logging.info('Connect successful, running')
    return mpd
# Logging:7 ends here

# [[file:../org/mpd.org::*Logging][Logging:8]]
def main():
    last_error = datetime.now()
    error_count = 0

    get_lock('sqrt-data-agent-mpd')

    while True:
        try:
            mpd = connect()
            watch(mpd)
        except Exception as exp:
            logging.error(repr(exp))
            logging.error('Waiting %s seconds, error count: %s',
                          settings.mpd.exception_timeout, error_count)
            time.sleep(settings.mpd.exception_timeout)

            if (datetime.now() - last_error).seconds > 60:
                error_count = 0
            last_error = datetime.now()
            error_count += 1
            if error_count > settings.mpd.exception_count:
                raise exp

if __name__ == "__main__":
    main()
# Logging:8 ends here
