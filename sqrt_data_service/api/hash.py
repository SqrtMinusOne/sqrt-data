# [[file:../../org/core-new.org::*Hashes][Hashes:2]]
import logging
import os
import subprocess
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import insert as pg_insert

from .config import settings
from sqrt_data_service.api import DBConn
from sqrt_data_service.models import FileHash
# Hashes:2 ends here

# [[file:../../org/core-new.org::*Hashes][Hashes:3]]
def md5sum(filename):
    res = subprocess.run(
        ['md5sum', filename],
        capture_output=True,
        check=True,
        cwd=settings.general.root
    ).stdout
    res = res.decode('utf-8')
    return res.split(' ')[0]
# Hashes:3 ends here

# [[file:../../org/core-new.org::*Hashes][Hashes:4]]
class FileHasher:
    def __init__(self):
        DBConn()

    def is_updated(self, file_name, db=None):
        with DBConn.ensure_session(db) as db:
            saved = db.execute(
                sa.select(FileHash).where(FileHash.file_name == file_name)
            ).scalar_one_or_none()
            if saved is None:
                return True
            return saved.hash != md5sum(file_name)

    def save_hash(self, file_name, db=None):
        hash = md5sum(file_name)
        was_ensured = db is None
        with DBConn.ensure_session(db) as db:
            insert_stmt = pg_insert(FileHash)
            upsert_stmt = insert_stmt.on_conflict_do_update(
                constraint='file_hash_pkey',
                set_={'hash': insert_stmt.excluded.hash}
            )
            db.execute(upsert_stmt, { 'file_name': file_name, 'hash': hash })
            if was_ensured:
                db.commit()
# Hashes:4 ends here
