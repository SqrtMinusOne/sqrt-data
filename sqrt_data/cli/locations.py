# [[file:../../org/locations.org::*CLI][CLI:1]]
import click

from sqrt_data.parse.locations import LocationMatcher

__all__ = ['locations']

@click.group(help='Locations')
def locations():
    pass
# CLI:1 ends here

# [[file:../../org/locations.org::*CLI][CLI:2]]
@locations.command(help='Check if the location data is consistent')
def check():
    LocationMatcher()
    print('Everything is OK')
# CLI:2 ends here
