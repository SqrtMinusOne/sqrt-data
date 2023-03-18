# [[file:../../../org/aw.org::*Final flow][Final flow:1]]
import argparse
from prefect import flow

from .app_intervals import process_app_intervals
from .load import aw_load_desktop
from .load_android import aw_load_android
from .postprocessing import aw_postprocessing_init, aw_postprocessing_dispatch

@flow
def aw_process(init=False):
    aw_load_desktop()
    aw_load_android()
    if init:
        aw_postprocessing_init()
    aw_postprocessing_dispatch()
    process_app_intervals()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='sqrt_data_service.flows.aw.main'
    )
    parser.add_argument('-i', '--init', action='store_true')
    args = parser.parse_args()
    aw_process(args.init)
# Final flow:1 ends here
