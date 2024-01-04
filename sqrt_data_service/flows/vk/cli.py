# [[file:../../../org/vk.org::*CLI][CLI:1]]
import click

from sqrt_data_service.api import settings

from .flow import vk_load

__all__ = ['vk']

@click.group()
def vk():
    pass

@vk.command(help='Load VK', name='load')
@click.option('--folder', type=click.Path(exists=True))
def load_cmd():
    vk_load(folder)
# CLI:1 ends here
