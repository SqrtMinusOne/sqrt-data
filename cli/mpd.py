import click
from parse.mpd import save_library, put_library

__all__ = ['mpd']

@click.group(help='MPD stats')
def mpd():
    pass


@mpd.command(help='Save the library to CSV file')
def to_csv():
    save_library()


@mpd.command(help='Load the library to DB')
def load():
    put_library()