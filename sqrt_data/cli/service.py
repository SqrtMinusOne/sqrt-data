# [[file:../../org/service.org::*CLI][CLI:1]]
import click
from sqrt_data import service as service_

__all__ = ['service']


@click.group(help='Service')
def service():
    pass


@service.command(help='Compress old files')
def compress():
    service_.compress()
# CLI:1 ends here
