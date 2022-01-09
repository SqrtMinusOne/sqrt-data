# [[file:../../org/core.org::*Server][Server:1]]
import time
import schedule
import subprocess

__all__ = ['run_server_cron']


def waka_task():
    p = subprocess.run(['sqrt_data', 'waka', 'get-data'])
    if p.returncode != 0:
        return
    subprocess.run(['sqrt_data', 'waka', 'load'])


def mpd_task():
    p = subprocess.run(['sqrt_data', 'mpd', 'load-library'])
    if p.returncode != 0:
        return
    subprocess.run(['sqrt_data', 'mpd', 'load-logs'])


def sleep_task():
    subprocess.run(['sqrt_data', 'sleep', 'load'])


def aw_task():
    p = subprocess.run(['sqrt_data', 'aw', 'load'])
    if p.returncode != 0:
        return
    subprocess.run(['sqrt_data', 'aw', 'postprocessing-dispatch'])


def run_server_cron():
    schedule.every().day.at('00:00').do(waka_task)
    schedule.every().day.at('01:00').do(mpd_task)
    schedule.every().day.at('02:00').do(sleep_task)
    schedule.every().day.at('03:00').do(aw_task)

    while True:
        schedule.run_pending()
        time.sleep(1)
# Server:1 ends here