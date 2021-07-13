import click

from sqrt_data import service as sc

__all__ = ['service']


@click.group(help='Service actions')
def service():
    pass


@service.command(help='Compress old files')
def compress():
    sc.compress()
