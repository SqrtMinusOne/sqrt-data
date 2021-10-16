# [[file:../../org/sleep.org::*CLI][CLI:1]]
import click
from sqrt_data.parse import sleep as sleep_
# CLI:1 ends here

# [[file:../../org/sleep.org::*CLI][CLI:2]]
__all__ = ['sleep']

@click.group(help='Sleep stats')
def sleep():
    pass
# CLI:2 ends here

# [[file:../../org/sleep.org::*CLI][CLI:3]]
@sleep.command(help='Load to DB')
def load():
    sleep_.load()
# CLI:3 ends here
