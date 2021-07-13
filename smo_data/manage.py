import logging

import click
import inquirer

from smo_data.api import get_filenames, hash_set, list_hashes
from smo_data.cli import android, aw, mpd, service, sleep, waka

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.FileHandler('./cli.log'),
              logging.StreamHandler()]
)


@click.group()
def cli():
    pass


cli.add_command(mpd)
cli.add_command(waka)
cli.add_command(aw)
cli.add_command(android)
cli.add_command(sleep)
cli.add_command(service)


@cli.command()
def hash_list():
    list_hashes()


@cli.command()
@click.option('-n', '--name', required=False, type=str)
def hash_toggle(name):
    logging.info('Toggled hash for %s', name)
    if name is None:
        name = inquirer.prompt(
            [inquirer.List('filename', 'Select filename', get_filenames())]
        )['filename'] # type: ignore
    hash_set(name)


if __name__ == '__main__':
    cli()
