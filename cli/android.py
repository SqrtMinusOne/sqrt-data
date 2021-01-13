import click

from parse import android as andc


__all__ = ['android']


@click.group(help='Android stats')
def android():
    pass


@android.command(help='Load to DB')
def load():
    andc.load()
