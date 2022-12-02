# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:1]]
import click
import os

from sqrt_data_service.api import FileHasher, DBConn
from sqrt_data_service.models import Base

@click.group()
def cli():
    print(f'CWD: {os.getcwd()}')
# CLI entrypoint:1 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:2]]
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
# CLI entrypoint:2 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:3]]
@click.group(help='Database')
def db():
    pass

@db.command()
@click.option('-n', '--name', required=True, type=str)
def create_schema(name):
    DBConn()
    DBConn.create_schema(name, Base)

cli.add_command(db)
# CLI entrypoint:3 ends here

# [[file:../org/core-new.org::*CLI entrypoint][CLI entrypoint:4]]
if __name__ == '__main__':
    cli()
# CLI entrypoint:4 ends here
