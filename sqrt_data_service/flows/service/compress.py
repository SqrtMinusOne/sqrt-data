# [[file:../../../org/service.org::*Compression][Compression:1]]
import json
import os
import pathlib
import subprocess
import time

import pandas as pd
import sqlalchemy as sa

from sqrt_data_service.api import settings, DBConn
from sqrt_data_service.models import FileHash
# Compression:1 ends here

# [[file:../../../org/service.org::*Compression][Compression:2]]
__all__ = ['archive']
# Compression:2 ends here

# [[file:../../../org/service.org::*Compression][Compression:3]]
def get_date_group(timestamp):
    return timestamp // (60 * 60 * 24 * settings['archive']['days'])
# Compression:3 ends here

# [[file:../../../org/service.org::*Compression][Compression:4]]
def get_files_to_compress():
    with DBConn.get_session() as db:
        file_entries = db.execute(sa.select(FileHash)).scalars()
        files = [
            f.file_name for f in file_entries if os.path.exists(f.file_name)
        ]

    df = pd.DataFrame(
        {
            "name": files,
            "date_group":
                [
                    get_date_group(pathlib.Path(f).stat().st_mtime)
                    for f in files
                ],
            "dir": [os.path.dirname(f) for f in files]
        }
    )

    current_date_group = get_date_group(time.time())
    current_date_group_delta = time.time(
    ) // (60 * 60 * 24) - current_date_group * settings['archive']['days']
    df = df[df.date_group != current_date_group]
    if current_date_group_delta <= settings['archive']['timeout']:
        df = df[df.date_group != current_date_group - 1]

    return [
        (date_group, dir, g.name.tolist())
        for (date_group, dir), g in df.groupby(['date_group', 'dir'])
        if dir not in settings['archive']['exclude_dirs']
    ]
# Compression:4 ends here

# [[file:../../../org/service.org::*Compression][Compression:5]]
def compress(groups):
    if len(groups) == 0:
        logging.info('Nothing to archive')
        return

    with DBConn.get_session() as db:
        file_entries = db.execute(sa.select(FileHash)).scalars()
        files = [
            f.file_name for f in file_entries if os.path.exists(f.file_name)
        ]

        for date_group, dir, files in groups:
            archive_name = f'{os.path.relpath(os.path.dirname(files[0]), os.path.expanduser(settings["general"]["root"])).replace("/", "_")}_{int(date_group)}.tar.gz'
            logging.info(
                'Creating archive %s with %d files', archive_name, len(files)
            )
            subprocess.run(
                [
                    'tar', '-czvf', archive_name, '--remove-files',
                    *[os.path.relpath(f, dir) for f in files]
                ],
                check=True,
                cwd=dir
            )
        for f in list(files):
            if not os.path.exists(f):
                db.execute(sa.delete(FileHash).where(FileHash.file_name == f))
                logging.info('Removed %s from HashDict', f)
        db.commit()
# Compression:5 ends here

# [[file:../../../org/service.org::*Compression][Compression:6]]
def archive():
    DBConn()
    groups = get_files_to_compress()
    compress(groups)
# Compression:6 ends here
