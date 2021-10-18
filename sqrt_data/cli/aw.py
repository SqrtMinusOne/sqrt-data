# [[file:../../org/aw.org::*CLI][CLI:1]]
import click
from sqrt_data.parse import aw as aw_
# CLI:1 ends here

# [[file:../../org/aw.org::*CLI][CLI:2]]
__all__ = ['aw']

@click.group(help='ActivityWatch stats')
def aw():
    pass
# CLI:2 ends here

# [[file:../../org/aw.org::*CLI][CLI:3]]
@aw.command(help='Save ActivityWatch buckets')
@click.option('--force', '-f', is_flag=True)
def save_buckets(force):
    aw_.save_buckets(force)

@aw.command(help='Load ActivityWatch buckets')
def load():
    aw_.load()
# CLI:3 ends here
