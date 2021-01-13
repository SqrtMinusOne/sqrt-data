import base64
import logging
import os

import requests

from api import Config

API = 'https://wakatime.com/api/v1'

__all__ = ['get_data']


def get_data():
    headers = {
        'Authorization':
        f'Basic {base64.b64encode(Config.WAKATIME_API_KEY).decode("utf-8")}'
    }
    r = requests.get(f'{API}/users/current/datadumps', headers=headers)
    data = r.json()['data']
    if len(data) == 0:
        logging.info('No WakaTime dumps found')
        return

    dump_data = data[0]
    if dump_data['status'] != 'Completed':
        logging.info('Dump not completed')
        return

    filename = f'wakatime-{dump_data["created_at"]}.json'
    path = os.path.join(os.path.expanduser(Config.TEMP_DATA_FOLDER), filename)
    if os.path.exists(path):
        logging.info('File already downloaded')
        return

    dump = requests.get(dump_data['download_url'])
    with open(path, 'wb') as f:
        f.write(dump.content)
    logging.info('WakaTime dump downloaded to %s', filename)
