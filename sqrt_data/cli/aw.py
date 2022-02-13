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

@aw.command(help='Load ActivityWatch Android buckets')
def load_android():
    aw_.load_android()
# CLI:3 ends here

# [[file:../../org/aw.org::*CLI][CLI:4]]
@aw.command(help='Set or update SQL definitions for postprocessing')
def postprocessing_set_sql():
    aw_.postprocessing_set_sql()

@aw.command(help='Initialize postprocessing')
def postprocessing_init():
    aw_.postprocessing_init()

@aw.command(help='Perform postprocessing')
def postprocessing_dispatch():
    aw_.postprocessing_dispatch()
# CLI:4 ends here
