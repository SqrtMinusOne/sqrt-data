# [[file:../../../org/wakatime.org::*CLI & Init][CLI & Init:1]]
import click

from sqrt_data_service.api import settings

from .flow import wakatime, wakatime_file

__all__ = ['waka']

@click.group()
def waka():
    pass

@waka.command(help='Load WakaTime', name='load')
def wakatime_cmd():
    wakatime()

@waka.command(help='Load WakaTime File', name='load-file')
@click.option('--file', '-f', help='File to load')
def wakatime_file_cmd(file):
    wakatime_file(file)
# CLI & Init:1 ends here
