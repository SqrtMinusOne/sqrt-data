# [[file:../../../org/mpd.org::*CLI][CLI:1]]
import click

from sqrt_data_service.api import settings

from .flow import load_mpd

__all__ = ['mpd']

@click.group()
def mpd():
    pass

@mpd.command(help='Load MPD', name='load')
def load_mpd_cmd():
    load_mpd()
# CLI:1 ends here
