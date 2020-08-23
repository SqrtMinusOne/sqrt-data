import click
from parse.wakatime import get_dump_data, dump_load


@click.group(help='WakaTime stats')
def waka():
    pass


@waka.command(help='Download the latest WakaTime dump')
def get_dump():
    get_dump_data()


@waka.command(help='Load the dump to DB')
def load_dump():
    dump_load()
