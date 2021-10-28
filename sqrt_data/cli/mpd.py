# [[file:../../org/mpd.org::*CLI][CLI:1]]
import click
from sqrt_data.parse import mpd as mpd_
# CLI:1 ends here

# [[file:../../org/mpd.org::*CLI][CLI:2]]
__all__ = ['mpd']

@click.group(help='MPD stats')
def mpd():
    pass
# CLI:2 ends here

# [[file:../../org/mpd.org::*CLI][CLI:3]]
@mpd.command(help='Save the MPD library to the CSV format')
def save_library():
    mpd_.save_library()
# CLI:3 ends here

# [[file:../../org/mpd.org::*CLI][CLI:4]]
@mpd.command(help='Load the MPD library')
def load_library():
    mpd_.load_library()
# CLI:4 ends here

# [[file:../../org/mpd.org::*CLI][CLI:5]]
@mpd.command(help='Load MPD logs')
def load_logs():
    mpd_.load_logs()
# CLI:5 ends here

# [[file:../../org/mpd.org::*CLI][CLI:6]]
@mpd.command(help='Create views for Metabase')
def create_views():
    mpd_.create_views()
# CLI:6 ends here
