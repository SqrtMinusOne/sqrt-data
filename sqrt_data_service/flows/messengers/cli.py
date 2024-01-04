# [[file:../../../org/messengers.org::*CLI & init][CLI & init:1]]
import click

from sqrt_data_service.api import settings

from .telegram import telegram_load
from .aggregate import messengers_aggregate

__all__ = ['msg']

@click.group()
def msg():
    pass

@msg.command(help='Load data from telegram', name='load-telegram')
@click.option('-f', '--file', 'file', required=True)
def telegram_cmd(file):
    telegram_load(file)

@msg.command(help='Aggregate data from messengers', name='aggregate')
def aggregate_cmd():
    messengers_aggregate()
# CLI & init:1 ends here
