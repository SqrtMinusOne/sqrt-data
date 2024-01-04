# [[file:../../../org/wakatime.org::*CLI & Init][CLI & Init:1]]
import click

from sqrt_data_service.api import settings

from .flow import wakatime

__all__ = ['waka']

@click.group()
def waka():
    pass

@waka.command(help='Load WakaTime', name='load')
def wakatime_cmd():
    wakatime()
# CLI & Init:1 ends here
