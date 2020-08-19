import click

from cli import mpd

@click.group()
def cli():
    pass

cli.add_command(mpd)

if __name__ == '__main__':
    cli()
