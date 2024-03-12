# [[file:../../../org/aw.org::*Final flow][Final flow:1]]
import argparse

from .app_intervals import process_app_intervals
from .load import aw_load_desktop
from .load_android import aw_load_android
from .postprocessing import aw_postprocessing_init, aw_postprocessing_dispatch


__all__ = ['aw_process']

def aw_process(init=False):
    aw_load_desktop()
    aw_load_android()
    if init:
        aw_postprocessing_init()
    aw_postprocessing_dispatch()
    process_app_intervals()
# Final flow:1 ends here
