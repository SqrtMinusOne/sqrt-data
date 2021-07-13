import click
from sqrt_data.parse.mpd import to_csv as to_csv_mpd, load_library, load_logs as load_logs_mpd

__all__ = ['mpd']


@click.group(help='MPD stats')
def mpd():
    pass


@mpd.command(help='Save the library to CSV file')
def to_csv():
    to_csv_mpd()


@mpd.command(help='Load the library to DB')
def load():
    load_library()


@mpd.command(help='Load the logs to DB')
def load_logs():
    load_logs_mpd()
