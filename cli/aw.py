import click

from parse.aw import get_buckets


__all__ = ['aw']

@click.group(help='ActivityWatch stats')
def aw():
    pass


@aw.command(help='Save AW data to CSV files')
def to_csv():
    get_buckets()
