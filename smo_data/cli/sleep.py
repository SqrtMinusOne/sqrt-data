import click
from smo_data.parse import sleep as sleep_


@click.group(help='SleepAsAndroid stats')
def sleep():
    pass


@sleep.command(help='Load the data to DB')
def load():
    sleep_.load()
