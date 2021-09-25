# [[file:../../README.org::*Hashes][Hashes:1]]
import json
import logging
import os
import subprocess
from .config import settings
# Hashes:1 ends here

# [[file:../../README.org::*Hashes][Hashes:2]]
def md5sum(filename):
    res = subprocess.run(['md5sum', filename], capture_output=True,
                         check=True).stdout
    res = res.decode('utf-8')
    return res.split(' ')[0]
# Hashes:2 ends here

# [[file:../../README.org::*Hashes][Hashes:3]]
def is_updated(filename):
    if not os.path.exists(settings.general.hash_json):
        return True
    with open(settings.general.hash_json, 'r') as f:
        data = json.load(f)
    if filename not in data:
        return True
    old_hash = data[filename]
    new_hash = md5sum(filename)
    return old_hash != new_hash
# Hashes:3 ends here

# [[file:../../README.org::*Hashes][Hashes:4]]
def save_hash(filename):
    new_hash = md5sum(filename)
    data = {}
    if os.path.exists(settings.general.hash_json):
        with open(settings.general.hash_json, 'r') as f:
            data = json.load(f)
    data[filename] = new_hash
    os.makedirs(os.path.dirname(settings.general.hash_json), exist_ok=True)
    with open(settings.hash_json, 'w') as f:
        json.dump(data, f)
    logging.info('Saved hash for %s', filename)
# Hashes:4 ends here

# [[file:../../README.org::*Hashes][Hashes:5]]
def hash_set(filename):
    if is_updated(filename):
        save_hash(filename)
    else:
        with open(settings.general.hash_json, 'r') as f:
            data = json.load(f)
        data[filename] = '0'
        with open(settings.general.hash_json, 'w') as f:
            json.dump(data, f)
# Hashes:5 ends here

# [[file:../../README.org::*Hashes][Hashes:6]]
def get_filenames():
    data = {}
    if os.path.exists(settings.general.hash_json):
        with open(settings.general.hash_json, 'r') as f:
            data = json.load(f)
    return list(data.keys())
# Hashes:6 ends here

# [[file:../../README.org::*Hashes][Hashes:7]]
def list_hashes():
    data = {}
    if os.path.exists(settings.general.hash_json):
        with open(settings.general.hash_json, 'r') as f:
            data = json.load(f)
    for name, value in data.items():
        if os.path.exists(name):
            if is_updated(name):
                print('[UPD]\t', end='')
            else:
                print('[   ]\t', end='')
        else:
            print('[DEL]\t', end='')
        print(f"{value}\t${name}")
# Hashes:7 ends here
