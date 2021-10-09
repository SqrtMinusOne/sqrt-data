# [[file:../../org/index.org::*Configuration][Configuration:1]]
import os

from dynaconf import Dynaconf

__all__ = ['settings']

settings = Dynaconf(
    settings_files=[
        'config.toml',
        os.path.expanduser('~/.config/sqrt-data/config.toml')
    ],
)
# Configuration:1 ends here
