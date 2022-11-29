# [[file:../../../org/service.org::*Compression][Compression:1]]
import json
import os
import pathlib
import subprocess
import time

from prefect import task, flow, get_run_logger
import pandas as pd
import sqlalchemy as sa

from sqrt_data_service.api import settings, DBConn
from sqrt_data_service.models import FileHash
# Compression:1 ends here

# [[file:../../../org/service.org::*Compression][Compression:2]]
def get_date_group(timestamp):
    return timestamp // (60 * 60 * 24 * settings['archive']['days'])
# Compression:2 ends here

# [[file:../../../org/service.org::*Compression][Compression:3]]
@task
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
# Compression:3 ends here

# [[file:../../../org/service.org::*Compression][Compression:4]]
@task
def compress(groups):
    logger = get_run_logger()
    if len(groups) == 0:
        logger.info('Nothing to archive')
        return

    with DBConn.get_session() as db:
        file_entries = db.execute(sa.select(FileHash)).scalars()
        files = [
            f.file_name for f in file_entries if os.path.exists(f.file_name)
        ]

        for date_group, dir, files in groups:
            archive_name = f'{os.path.relpath(os.path.dirname(files[0]), os.path.expanduser(settings["general"]["root"])).replace("/", "_")}_{int(date_group)}.tar.gz'
            logger.info(
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
                logger.info('Removed %s from HashDict', f)
        db.commit()
# Compression:4 ends here

# [[file:../../../org/service.org::*Compression][Compression:5]]
@flow
def archive():
    DBConn()
    groups = get_files_to_compress()
    compress(groups)


if __name__ == '__main__':
    archive()
# Compression:5 ends here
