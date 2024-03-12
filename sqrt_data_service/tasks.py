# [[file:../org/core-new.org::*Tasks][Tasks:1]]
import click
import logging
import os
import schedule
import subprocess
import time

__all__ = ["run_tasks"]

TASKS = [
    (schedule.every().day.at("03:00"), ["aw", "process-all"], "aw"),
    (schedule.every().day.at("01:00"), ["mpd", "load"], "mpd"),
    (schedule.every().day.at("05:00"), ["service", "archive"], "archive"),
    (schedule.every().day.at("00:00"), ["waka", "load"], "wakatime"),
]

def make_job(command, scope):
    def job():
        logging.info("Running %s", command)
        subprocess.run(command, env={**os.environ, "SCOPE": scope})

    return job

def run_tasks():
    for schedule_, command, scope in TASKS:
        schedule_.do(make_job(command, scope))
        logging.info("Scheduled %s", command)

    while True:
        n = schedule.idle_seconds()
        if n is None:
            break
        elif n > 0:
            logging.info("Sleeping for %d seconds", n)
            time.sleep(n)
        schedule.run_pending()
# Tasks:1 ends here
