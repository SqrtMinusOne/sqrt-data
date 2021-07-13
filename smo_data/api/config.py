import json
import logging
import os

__all__ = ['Config']


class Config:
    USER = 'postgres'
    PASSWORD = '******'
    DATABASE = 'data'
    HOST = 'localhost'
    PORT = 5432

    ROOT = '~/logs-sync-debug'

    MPD_CSV = ''
    MPD_LOG_FOLDER = ''
    TEMP_DATA_FOLDER = '~/Code/Data/_data'
    HASH_JSON = ''

    WAKATIME_API_KEY = b'******'

    AW_LAST_UPDATED = ''
    AW_LOGS_FOLDER = ''
    AW_TYPES = ['afkstatus', 'currentwindow']

    ANDROID_FILE = ''

    SLEEP_FILE = ''
    SLEEP_GEOS = {
        'e65661c5': '******',
        'e3336046': '******',
        'e3336012': '******'
    }

    ARCHIVE_DAYS = 31
    ARCHIVE_TIMEOUT = 5

    @classmethod
    def _update_paths(cls):
        cls.ROOT = os.path.expanduser(cls.ROOT)
        cls.TEMP_DATA_FOLDER = os.path.expanduser(cls.TEMP_DATA_FOLDER)

        cls.HASH_JSON = cls.HASH_JSON or cls.ROOT + '/hash.json'
        cls.MPD_CSV = cls.MPD_CSV or cls.ROOT + '/mpd/mpd_library.csv'
        cls.MPD_LOG_FOLDER = cls.MPD_LOG_FOLDER or cls.ROOT + '/mpd/logs'
        cls.AW_LAST_UPDATED = cls.AW_LAST_UPDATED or cls.ROOT + '/aw_last_updated.json'
        cls.AW_LOGS_FOLDER = cls.AW_LOGS_FOLDER or cls.ROOT + '/aw'
        cls.ANDROID_FILE = cls.ANDROID_FILE or cls.ROOT + '/google/android-history.json'
        cls.SLEEP_FILE = cls.SLEEP_FILE or cls.ROOT + '/google/android-history.json'

    @classmethod
    def load_config(cls, path=None):
        if path == 'no':
            return
        if path is None:
            config_root = os.environ.get(
                'XDG_CONFIG_HOME', os.path.expanduser('~/.config')
            )
            path = os.path.join(config_root, 'smo-data', 'config.json')
            if not os.path.exists(path):
                logging.warn('Config not found at %s', path)
                return
        with open(path, 'r') as f:
            config = json.load(f)
            for key, value in config.items():
                if not hasattr(cls, key):
                    logging.warn('Wrong attribute %s', key)
                setattr(cls, key, value)
        cls._update_paths()
        import ipdb
        ipdb.set_trace()
