# [[file:../../org/core-new.org::*Configuration][Configuration:1]]
import os

from dynaconf import Dynaconf

__all__ = ['settings']

settings_files = [
    # os.path.expanduser('~/.config/sqrt-data/config.service.toml'),
    'config.service.toml'
]

if all([not os.path.exists(f) for f in settings_files]):
    print('No config found!')

settings = Dynaconf(settings_files=settings_files)
# Configuration:1 ends here
