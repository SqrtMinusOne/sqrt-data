import click
from smo_data.parse import wakatime


@click.group(help='WakaTime stats')
def waka():
    pass


@waka.command(help='Download the latest WakaTime dump')
def get_data():
    wakatime.get_data()


@waka.command(help='Load the dump to DB')
def load():
    wakatime.load()