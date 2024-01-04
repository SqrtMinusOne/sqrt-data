# [[file:../../../org/aw.org::*CLI & Init][CLI & Init:1]]
import click

from sqrt_data_service.api import settings

from .app_intervals import process_app_intervals
from .load import aw_load_desktop
from .load_android import aw_load_android
from .postprocessing import aw_postprocessing_init, aw_postprocessing_dispatch
from .main import aw_process


__all__ = ["aw"]

@click.group()
def aw():
    pass

@aw.command(help="Load desktop data", name="load-desktop")
def aw_load_desktop_cmd():
    aw_load_desktop()

@aw.command(help="Load android data", name="load-android")
def aw_load_android_cmd():
    aw_load_android()

@aw.command(help="Process app intervals", name="process-app-intervals")
def aw_process_app_intervals_cmd():
    process_app_intervals()

@aw.command(help="Postprocessing init", name="postprocessing-init")
def aw_postprocessing_init_cmd():
    aw_postprocessing_init()

@aw.command(help="Postprocessing dispatch", name="postprocessing-dispatch")
def aw_postprocessing_dispatch_cmd():
    aw_postprocessing_dispatch()

@aw.command(help="Process all", name="process-all")
def aw_process_all_cmd():
    aw_process()
# CLI & Init:1 ends here
