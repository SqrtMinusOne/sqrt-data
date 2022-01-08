# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:1]]
import logging

import click
import os
import inquirer

from sqrt_data.api import HashDict, settings, get_hostname
from sqrt_data import cli as cli_modules
from sqrt_data import tasks
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
@click.group(help='Working with hashes')
def hash():
    pass

@hash.command()
def hash_list():
    hashes = HashDict()
    hashes.report()


@hash.command()
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

cli.add_command(hash)
# CLI entrypoint:6 ends here

# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:7]]
@click.group(help='Initialize recurring tasks. Meant to be run in a service or such')
def cron():
    pass


@cron.command()
def run_server_cron():
    tasks.run_server_cron()


@cron.command()
def run_client_cron():
    tasks.run_client_cron()


cli.add_command(cron)
# CLI entrypoint:7 ends here

# [[file:../org/core.org::*CLI entrypoint][CLI entrypoint:8]]
if __name__ == '__main__':
    cli()
# CLI entrypoint:8 ends here
