import click
import inquirer
import logging

from api import get_filenames, hash_set, list_hashes
from cli import mpd

logging.basicConfig(
    filename='./cli.log',
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

@click.group()
def cli():
    pass


cli.add_command(mpd)


@cli.command()
def hash_list():
    list_hashes()


@cli.command()
@click.option('-n', '--name', required=False, type=str)
def hash_toggle(name):
    logging.info('Toggled hash for %s', name)
    if name is None:
        name = inquirer.prompt(
            [inquirer.List('filename', 'Select filename',
                           get_filenames())])['filename']
    hash_set(name)


if __name__ == '__main__':
    cli()
