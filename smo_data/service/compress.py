import json
import logging
import os
import pathlib
import subprocess
import time

import pandas as pd

from smo_data.api import Config

__all__ = ['compress']


def get_date_group(timestamp):
    return timestamp // (60 * 60 * 24 * Config.ARCHIVE_DAYS)


def get_files_to_compress(data):
    files = [f for f in data.keys() if os.path.exists(f)]
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
    ) // (60 * 60 * 24) - current_date_group * Config.ARCHIVE_DAYS
    df = df[df.date_group != current_date_group]
    if current_date_group_delta <= Config.ARCHIVE_TIMEOUT:
        df = df[df.date_group != current_date_group - 1]

    return [
        (date_group, dir, g.name.tolist())  # type: ignore
        for (date_group,
             dir), g in df.groupby(['date_group', 'dir'])  # type: ignore
    ]


def compress():
    with open(os.path.expanduser(Config.HASH_JSON), 'r') as f:
        data = json.load(f)

    groups = get_files_to_compress(data)
    if len(groups) == 0:
        logging.info('Nothing to archive')
        return

    for date_group, dir, files in groups:
        archive_name = f'{os.path.relpath(os.path.dirname(files[0]), os.path.expanduser(Config.ROOT)).replace("/", "_")}_{int(date_group)}.tar.gz'
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
        for f in files:
            del data[f]

    with open(os.path.expanduser(Config.HASH_JSON), 'w') as f:
        json.dump(data, f)
