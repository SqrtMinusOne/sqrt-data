# [[file:../org/core-new.org::*Sync][Sync:1]]
import argparse
import os
import subprocess
import socket
from datetime import datetime

from sqrt_data_agent.api import settings
from .aw import save_buckets
from .mpd_save_library import save_library
# Sync:1 ends here

# [[file:../org/core-new.org::*Sync][Sync:2]]
EXEC_OSYNC = 'osync.sh'
EXEC_NOTIFY_SEND = 'notify-send'
# Sync:2 ends here

# [[file:../org/core-new.org::*Sync][Sync:3]]
def log_string():
    date_string = datetime.strftime(datetime.now(), "%Y-%m-%d")
    return f'{socket.gethostname()}: {date_string}'
# Sync:3 ends here

# [[file:../org/core-new.org::*Sync][Sync:4]]
def check_today_sync():
    if not os.path.exists(settings.sync.log_file):
        return False
    string = log_string()
    with open(settings.sync.log_file, 'r') as f:
        for line in f:
            if line.strip() == string:
                return True
    return False
# Sync:4 ends here

# [[file:../org/core-new.org::*Sync][Sync:5]]
def set_today_sync():
    with open(settings.sync.log_file, 'a') as f:
        f.write(log_string() + '\n')
# Sync:5 ends here

# [[file:../org/core-new.org::*Sync][Sync:6]]
def sync_logs(force=False):
    if not force and check_today_sync():
        print('Already synced today!')
        return
    save_library()
    save_buckets(force)
    subprocess.run(
        [
            EXEC_OSYNC, f'--initiator={settings.general.root}',
            f'--target={settings.sync.target}'
        ],
        env={
            **os.environ,
            'RSYNC_EXCLUDE_PATTERN': 'sync.log',
            'CREATE_DIRS': 'yes',
            'REMOTE_HOST_PING': 'false',
            'PATH': os.environ['PATH']
        },
        check=True
    )
    if not is_android():
        subprocess.run(
            [EXEC_NOTIFY_SEND, 'Sync', 'Logs submitted to the server'],
            env={'DISPLAY': ':0', **os.environ}
        )
    set_today_sync()
# Sync:6 ends here

# [[file:../org/core-new.org::*Sync][Sync:7]]
def main():
    parser = argparse.ArgumentParser(
        prog='sqrt_data_agent.aw'
    )
    parser.add_argument('-f', '--force', action='store_true')
    args = parser.parse_args()
    sync_logs(args.force)

if __name__ == '__main__':
    main()
# Sync:7 ends here
