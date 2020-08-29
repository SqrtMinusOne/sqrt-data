import click

from parse.youtube import youtube_load


__all__ = ['google']

@click.group(help='Google stats')
def google():
    pass


@google.command(help='Load Youtube stats')
def load_youtube():
    youtube_load()
