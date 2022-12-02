# [[file:../../org/core-new.org::*Connection][Connection:1]]
import logging
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from .config import settings

__all__ = ['DBConn']


class DBConn:
    engine = None
    Session = None
    Base = None

    def __init__(self, **kwargs):
        DBConn.engine = DBConn.get_engine(**kwargs)
        DBConn.Session = sessionmaker()
        DBConn.Session.configure(bind=self.engine)
        DBConn.scoped_session = scoped_session(DBConn.Session)
        logging.info('Initialized database connection')
    @classmethod
    def reset(cls):
        cls.engine = cls.Session = None
    @staticmethod
    @contextmanager
    def get_session(**kwargs):
        session = DBConn.Session(**kwargs)
        yield session
        session.close()
    @staticmethod
    @contextmanager
    def ensure_session(session, **kwargs):
        if session is None:
            session = DBConn.Session(**kwargs)
            yield session
            session.close()
        else:
            yield session
    @staticmethod
    def get_url(user=None, password=None, **kwargs):
        url = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
            user or settings.database.user, password or
            settings.database.password, settings.database.host,
            settings.database.port, settings.database.database
        )
        return url
    
    @staticmethod
    def get_engine(**kwargs):
        url = DBConn.get_url(**kwargs)
        return create_engine(url, **kwargs)
    @staticmethod
    def create_schema(schema, Base=None):
        DBConn.engine.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
        if Base is not None:
            tables = []
            for name, table in Base.metadata.tables.items():
                if table.schema == schema:
                    tables.append(table)
            Base.metadata.create_all(DBConn.engine, tables)
# Connection:1 ends here
