import json
import logging
import os
import subprocess

from .db import Config

HASH_JSON = os.path.expanduser(Config.HASH_JSON)

__all__ = [
    'md5sum', 'is_updated', 'save_hash', 'list_hashes', 'hash_set',
    'get_filenames'
]


def md5sum(filename):
    res = subprocess.run(['md5sum', filename], capture_output=True,
                         check=True).stdout
    res = res.decode('utf-8')
    return res.split(' ')[0]


def is_updated(filename):
    if not os.path.exists(HASH_JSON):
        return True
    with open(HASH_JSON, 'r') as f:
        data = json.load(f)
    if filename not in data:
        return True
    old_hash = data[filename]
    new_hash = md5sum(filename)
    return old_hash != new_hash


def save_hash(filename):
    new_hash = md5sum(filename)
    data = {}
    if os.path.exists(HASH_JSON):
        with open(HASH_JSON, 'r') as f:
            data = json.load(f)
    data[filename] = new_hash
    os.makedirs(os.path.dirname(HASH_JSON), exist_ok=True)
    with open(HASH_JSON, 'w') as f:
        json.dump(data, f)
    logging.info('Saved hash for %s', filename)


def hash_set(filename):
    if is_updated(filename):
        save_hash(filename)
    else:
        with open(HASH_JSON, 'r') as f:
            data = json.load(f)
        data[filename] = '0'
        with open(HASH_JSON, 'w') as f:
            json.dump(data, f)


def get_filenames():
    data = {}
    if os.path.exists(HASH_JSON):
        with open(HASH_JSON, 'r') as f:
            data = json.load(f)
    return list(data.keys())


def list_hashes():
    data = {}
    if os.path.exists(HASH_JSON):
        with open(HASH_JSON, 'r') as f:
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
