# [[file:../../org/youtube.org::*CLI][CLI:1]]
import click
from sqrt_data.parse import youtube as youtube_
# CLI:1 ends here

# [[file:../../org/youtube.org::*CLI][CLI:2]]
__all__ = ['youtube']

@click.group(help='YouTube stats')
def youtube():
    pass
# CLI:2 ends here

# [[file:../../org/youtube.org::*CLI][CLI:3]]
@youtube.command(help='Initialize the DB')
def init_db():
    youtube_.init_db()
# CLI:3 ends here
