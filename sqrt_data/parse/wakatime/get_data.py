# [[file:../../../org/wakatime.org::*Get the data][Get the data:1]]
import base64
import logging
import os
import requests

from sqrt_data.api import settings
# Get the data:1 ends here

# [[file:../../../org/wakatime.org::*Get the data][Get the data:2]]
__all__ = ['get_data']
# Get the data:2 ends here

# [[file:../../../org/wakatime.org::*Get the data][Get the data:3]]
def get_data():
    key = base64.b64encode(str.encode(settings["waka"]["api_key"])).decode('utf-8')
    headers = {'Authorization': f'Basic {key}'}
    r = requests.get(
        f'{settings["waka"]["api_url"]}/users/current/datadumps',
        headers=headers
    )
    print(r.json())
    print(headers)
    data = r.json()['data']
    if len(data) == 0:
        logging.info('No WakaTime dumps found')
        return

    dump_data = data[0]
    if dump_data['status'] != 'Completed':
        logging.info('Dump not completed')
        return

    filename = f'wakatime-{dump_data["created_at"]}.json'
    path = os.path.join(
        os.path.expanduser(settings['general']['temp_data_folder']), filename
    )
    if os.path.exists(path):
        logging.info('File already downloaded')
        return

    dump = requests.get(dump_data['download_url'])
    with open(path, 'wb') as f:
        f.write(dump.content)
    logging.info('WakaTime dump downloaded to %s', filename)
# Get the data:3 ends here
