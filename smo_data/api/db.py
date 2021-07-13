from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

__all__ = ['DBConn', 'Config']


class Config:
    USER = 'postgres'
    PASSWORD = '******'
    DATABASE = 'data'
    HOST = 'localhost'
    PORT = 5432

    ROOT = '~/logs-sync-debug'

    MPD_CSV = ROOT + '/mpd/mpd_library.csv'
    MPD_LOG_FOLDER = ROOT + '/mpd/logs'
    TEMP_DATA_FOLDER = '~/Code/Data/_data'
    HASH_JSON = ROOT + '/hash.json'

    WAKATIME_API_KEY = b'******'

    AW_LAST_UPDATED = ROOT + '/aw_last_updated.json'
    AW_LOGS_FOLDER = ROOT + '/aw'
    AW_TYPES = ['afkstatus', 'currentwindow']

    ANDROID_FILE = ROOT + '/google/android-history.json'

    SLEEP_FILE = ROOT + '/sleep/sleep-export.csv'
    SLEEP_GEOS = {
        'e65661c5': '******',
        'e3336046': '******',
        'e3336012': '******'
       }

    ARCHIVE_DAYS = 31
    ARCHIVE_TIMEOUT = 5


class DBConn:
    engine = None
    Session = None
    Base = None

    def __init__(self, **kwargs):
        DBConn.engine = DBConn.get_engine(**kwargs)
        DBConn.Session = sessionmaker()
        DBConn.Session.configure(bind=self.engine)
        DBConn.scoped_session = scoped_session(DBConn.Session)

    @classmethod
    def reset(cls):
        cls.engine = cls.Session = None

    @staticmethod
    def make_get_session(**kwargs):
        engine = DBConn.get_engine(**kwargs)
        Session = sessionmaker()
        Session.configure(bind=engine)

        @contextmanager
        def get_session(**session_kwargs):
            session = Session(**session_kwargs)
            yield session
            session.close()

        return get_session

    @staticmethod
    @contextmanager
    def get_session(**kwargs):
        """
        Get automatically closing sessions
        Usage:
        ```
        with DBConn.get_session() as session:
            # do stuff
        ```
        """
        session = DBConn.Session(**kwargs)
        yield session
        session.close()

    @staticmethod
    @contextmanager
    def ensure_session(session, **kwargs):
        """
        If session is None, make a new one
        """
        if session is None:
            session = DBConn.Session(**kwargs)
            yield session
            session.close()
        else:
            yield session

    @staticmethod
    def get_engine(user=None, password=None, **kwargs):
        """Initialize SQLAlchemy engine from configuration parameters
        :param **kwargs: to sqlalchemy.create_engine
        """
        url = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            user or Config.USER, password or
            Config.PASSWORD, Config.HOST,
            Config.PORT, Config.DATABASE
        )
        return create_engine(url, **kwargs)

    @staticmethod
    def create_schema(schema, Base):
        DBConn.engine.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
        tables = []
        for name, table in Base.metadata.tables.items():
            if table.schema == schema:
                tables.append(table)
                Base.metadata.create_all(DBConn.engine, tables)
