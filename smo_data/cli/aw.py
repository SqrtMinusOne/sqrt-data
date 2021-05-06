import click

from smo_data.parse import aw as awc


__all__ = ['aw']


@click.group(help='ActivityWatch stats')
def aw():
    pass


@aw.command(help='Save AW data to CSV files')
def to_csv():
    awc.to_csv()


@aw.command(help='Load new buckets to DB')
@click.option('--dry-run', help='Dry run', is_flag=True)
def load(dry_run):
    awc.load(dry_run)
