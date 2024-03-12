# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:1]]
import click
import os

from sqrt_data_service.api import FileHasher, DBConn
from sqrt_data_service.models import Base
from sqrt_data_service.common.logging import configure_logging

from sqrt_data_service.flows.aw import aw
from sqrt_data_service.flows.messengers import msg
from sqrt_data_service.flows.mpd import mpd
from sqrt_data_service.flows.service import service
from sqrt_data_service.flows.vk import vk
from sqrt_data_service.flows.wakatime import waka

from .tasks import run_tasks

@click.group()
def cli():
    configure_logging()
    print(f'CWD: {os.getcwd()}')
# CLI entrypoint:1 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:2]]
cli.add_command(aw)
cli.add_command(msg)
cli.add_command(mpd)
cli.add_command(service)
cli.add_command(vk)
cli.add_command(waka)
# CLI entrypoint:2 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:3]]
@cli.command(help='Run recurring tasks', name='tasks')
def tasks():
    configure_logging()
    run_tasks()
# CLI entrypoint:3 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:4]]
@click.group(help='Hashes')
def hash():
    pass

@hash.command()
@click.option('-f', '--file-name', required=True, type=str)
def check_hash(file_name):
    hasher = FileHasher()
    if not os.path.exists(file_name):
        print('File not found')
    else:
        result = hasher.is_updated(file_name)
        print(f'Updated: {result}')


@hash.command()
@click.option('-f', '--file-name', required=True, type=str)
def save_hash(file_name):
    hasher = FileHasher()
    hasher.save_hash(file_name)

cli.add_command(hash)
# CLI entrypoint:4 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:5]]
@click.group(help='Database')
def db():
    pass

@db.command()
@click.option('-n', '--name', required=True, type=str)
def create_schema(name):
    DBConn()
    DBConn.create_schema(name, Base)

cli.add_command(db)
# CLI entrypoint:5 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:6]]
if __name__ == '__main__':
    cli()
# CLI entrypoint:6 ends here
