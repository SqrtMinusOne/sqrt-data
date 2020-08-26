import click

from parse.aw import get_buckets, load_data


__all__ = ['aw']

@click.group(help='ActivityWatch stats')
def aw():
    pass


@aw.command(help='Save AW data to CSV files')
def to_csv():
    get_buckets()


@aw.command(help='Load new buckets to DB')
def load():
    load_data()
