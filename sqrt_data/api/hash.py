# [[file:../../org/core.org::*Hashes][Hashes:1]]
from sqlitedict import SqliteDict
import logging
import os
import subprocess
from .config import settings

__all__ = ['md5sum', 'HashDict']
# Hashes:1 ends here

# [[file:../../org/core.org::*Hashes][Hashes:2]]
def md5sum(filename):
    res = subprocess.run(
        ['md5sum', filename],
        capture_output=True,
        check=True,
        cwd=settings.general.root
    ).stdout
    res = res.decode('utf-8')
    return res.split(' ')[0]
# Hashes:2 ends here

# [[file:../../org/core.org::*Hashes][Hashes:3]]
import ctypes
libgcc_s = ctypes.CDLL('libgcc_s.so.1')
# Hashes:3 ends here

# [[file:../../org/core.org::*Hashes][Hashes:4]]
class HashDict(SqliteDict):
    def __init__(self, *args, **kwargs):
        super().__init__(settings.general.hash_db, *args, **kwargs)

    def is_updated(self, filename):
        saved = self.get(filename)
        return saved is None or saved != md5sum(filename)

    def save_hash(self, filename):
        self[filename] = md5sum(filename)

    def toggle_hash(self, filename):
        if self.is_updated(filename):
            self.save_hash(filename)
        else:
            self[filename] = '0'

    def report(self):
        for name, value in self.items():
            if os.path.exists(name):
                if self.is_updated(name):
                    print('[UPD]\t', end='')
                else:
                    print('[   ]\t', end='')
            else:
                print('[DEL]\t', end='')
            print(f"{value}\t{name}")
# Hashes:4 ends here
