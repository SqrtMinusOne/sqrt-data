import inquirer
import click

from api import list_hashes, get_filenames, hash_set
from cli import mpd

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
    if name is None:
        name = inquirer.prompt([
            inquirer.List(
                'filename',
                'Select filename',
                get_filenames()
            )
        ])['filename']
    hash_set(name)

if __name__ == '__main__':
    cli()
