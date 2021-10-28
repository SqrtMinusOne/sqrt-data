# [[file:../../org/vk.org::*CLI][CLI:1]]
import click
from sqrt_data.parse import vk as vk_

__all__ = ['vk']


@click.group(help='Parsing the VK dump')
def vk():
    pass


@vk.command(help='Load the dump to DB')
@click.option(
    '--path',
    '-p',
    type=click.Path(exists=True),
    help='Path to the "messages" directory from the dump',
    required=True
)
def load(path):
    vk_.load(path)
# CLI:1 ends here
