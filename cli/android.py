import click

from parse.android import load_android


__all__ = ['android']


@click.group(help='Android stats')
def android():
    pass


@android.command(help='Load to DB')
def load():
    load_android()
