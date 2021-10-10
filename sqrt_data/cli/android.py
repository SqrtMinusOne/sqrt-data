# [[file:../../org/google-android.org::*CLI][CLI:1]]
import click
from sqrt_data.parse import android as andc
# CLI:1 ends here

# [[file:../../org/google-android.org::*CLI][CLI:2]]
__all__ = ['android']

@click.group(help='Android stats')
def android():
    pass
# CLI:2 ends here

# [[file:../../org/google-android.org::*CLI][CLI:3]]
@android.command(help='Load to DB')
def load():
    andc.load()
# CLI:3 ends here
