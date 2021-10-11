# [[file:../../org/wakatime.org::*CLI][CLI:1]]
import click
from sqrt_data.parse import wakatime


@click.group(help='WakaTime stats')
def waka():
    pass


@waka.command(help='Download the latest WakaTime dump')
def get_data():
    wakatime.get_data()


@waka.command(help='Load the dump to DB')
def load():
    wakatime.load()
# CLI:1 ends here
