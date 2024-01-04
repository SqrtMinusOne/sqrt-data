# [[file:../../../org/service.org::*CLI][CLI:1]]
import click

from sqrt_data_service.api import settings

from .compress import archive

@click.group()
def service():
    pass

@service.command(help="Archive old files", name='archive')
def archive_cmd():
    archive()
# CLI:1 ends here
