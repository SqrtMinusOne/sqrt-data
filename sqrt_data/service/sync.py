# [[file:../../org/service.org::*Sync][Sync:1]]
import os
import subprocess
from datetime import datetime

from sqrt_data.api import settings, get_hostname
# Sync:1 ends here

# [[file:../../org/service.org::*Sync][Sync:2]]
EXEC_GREP = 'grep'
EXEC_OSYNC = 'osync.sh'
EXEC_NOTIFY_SEND = 'notify-send'
# Sync:2 ends here

# [[file:../../org/service.org::*Sync][Sync:3]]
__all__ = ['sync_logs']
# Sync:3 ends here

# [[file:../../org/service.org::*Sync][Sync:4]]
def log_string():
    date_string = datetime.strftime(datetime.now(), "%Y-%m-%d")
    return f'{get_hostname()}: {date_string}'
# Sync:4 ends here

# [[file:../../org/service.org::*Sync][Sync:5]]
def check_today_sync():
    result = subprocess.run(
        [EXEC_GREP, '-F',
         log_string(), settings.general.sync_log_file]
    )
    return result.returncode == 0
# Sync:5 ends here

# [[file:../../org/service.org::*Sync][Sync:6]]
def sync_logs(force=False):
    if not force and check_today_sync():
        print('Already synced today!')
        return
# Sync:6 ends here
