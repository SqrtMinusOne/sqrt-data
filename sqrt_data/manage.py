# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:1]]
import logging

import click
import os
import inquirer

from sqrt_data.api import HashDict, settings, get_hostname
from sqrt_data import cli as cli_modules
# CLI entrypoint:1 ends here

# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:2]]
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[logging.FileHandler('./cli.log'),
              logging.StreamHandler()]
)
# CLI entrypoint:2 ends here

# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:3]]
@click.group()
def cli():
    print(f'CWD: {os.getcwd()}')
    print(f'hostname: {get_hostname()}')
# CLI entrypoint:3 ends here

# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:4]]
cli.add_command(cli_modules.waka)
cli.add_command(cli_modules.android)
cli.add_command(cli_modules.vk)
cli.add_command(cli_modules.sleep)
cli.add_command(cli_modules.mpd)
cli.add_command(cli_modules.aw)
cli.add_command(cli_modules.locations)
cli.add_command(cli_modules.service)
# CLI entrypoint:4 ends here

# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:6]]
@cli.command()
def hash_list():
    hashes = HashDict()
    hashes.report()


@cli.command()
@click.option('-n', '--name', required=False, type=str)
def hash_toggle(name):
    with HashDict() as h:
        if name is None:
            name = inquirer.prompt(
                [
                    inquirer.List(
                        'filename', 'Select filename', choices=list(h.keys())
                    )
                ]
            )['filename']  # type: ignore
        h.toggle_hash(os.path.join(settings.general.root, name))
        logging.info('Toggled hash for %s', name)
        h.commit()
# CLI entrypoint:6 ends here

# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:7]]
if __name__ == '__main__':
    cli()
# CLI entrypoint:7 ends here
