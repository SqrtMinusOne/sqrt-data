# [[file:../../org/core.org::*Client][Client:1]]
import schedule
import time
import logging
from sqrt_data.service import sync_logs

__all__ = ['run_client_cron']


def client_task():
    try:
        sync_logs()
    except Exception:
        logging.exception('Sync error!')


def run_client_cron():
    schedule.every().hour.at(":00").do(client_task)
    while True:
        schedule.run_pending()
        time.sleep(1)
# Client:1 ends here
