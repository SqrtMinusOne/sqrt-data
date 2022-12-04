# [[file:../../../org/vk.org::*Flow][Flow:1]]
import argparse
import pandas as pd
import os
import sys
import sqlalchemy as sa

from sqrt_data_service.api import DBConn, settings

from bs4 import BeautifulSoup
from collections import deque
from dateutil import parser
from prefect import task, flow, get_run_logger
from tqdm import tqdm
# Flow:1 ends here

# [[file:../../../org/vk.org::*Flow][Flow:2]]
def parse_date_english(date):
    is_edited = False
    if date.endswith(' (edited)'):
        is_edited = True
        date = date[:-9]
    date = date[2:]
    date = parser.parse(date)
    return is_edited, date
# Flow:2 ends here

# [[file:../../../org/vk.org::*Flow][Flow:3]]
MONTHS = [
    'янв', 'фев', 'мар', 'апр', 'мая', 'июн', 'июл', 'авг', 'сен', 'окт', 'ноя',
    'дек'
]


def parse_date_russian(date):
    is_edited = False
    if date.endswith(' (ред.)'):
        is_edited = True
        date = date[:-7]
    day, month, year, _, time = date.split()

    month = MONTHS.index(month) + 1
    date = parser.parse(time).replace(day=int(day), month=month, year=int(year))
    return is_edited, date
# Flow:3 ends here

# [[file:../../../org/vk.org::*Flow][Flow:4]]
def parse_file(path):
    with open(path, 'r', encoding='windows-1251') as f:
        soup = BeautifulSoup(f, features="html.parser")

    content = soup.html.body.div
    name = content.find(class_='page_content page_block'
                       ).h2.div.find(class_='_header_inner'
                                    ).find('div', class_='ui_crumb').text
    items = content.find(class_='page_content page_block'
                        ).find(class_='wrap_page_content')

    senders, dates, messages, edited = deque(), deque(), deque(), deque()
    is_group = None

    for item in items.find_all(class_='item'):
        header = item.div.find(class_='message__header')
        author, date = header.text.split(', ', 1)

        is_edited, date = parse_date_english(date)
        message_div = item.div.find('div', class_='')
        message = ''
        for content in message_div.contents:
            if content.name is None:
                if message:
                    message += '\n' + content
                else:
                    message += content

        if message:
            senders.append(author)
            dates.append(date)
            messages.append(message)
            edited.append(is_edited)

            if is_group is None and author == name:
                is_group = False

    if is_group is None:
        is_group = True

    global_author = settings['vk']['author']

    df = pd.DataFrame(
        {
            "target": name,
            "sender": [s if s != 'You' else global_author for s in senders],
            "is_outgoing": [s == 'You' for s in senders],
            "message": messages,
            "date": dates,
            "is_edited": edited,
            "is_group": is_group
        }
    )
    return df
# Flow:4 ends here

# [[file:../../../org/vk.org::*Flow][Flow:5]]
@task
def parse_directory(path):
    logger = get_run_logger()
    files = sorted([f for f in os.listdir(path) if f.endswith('html')])
    df = pd.DataFrame(
        {
            'target': pd.Series(dtype='str'),
            'sender': pd.Series(dtype='str'),
            'is_outgoing': pd.Series(dtype='bool'),
            'message': pd.Series(dtype='str'),
            'date': pd.Series(dtype='datetime64[ns]'),
            'is_edited': pd.Series(dtype='bool'),
            'is_group': pd.Series(dtype='bool')
        }
    )
    for file in files:
        df_ = parse_file(os.path.join(path, file))
        df = pd.concat([df, df_])
    df = df.sort_values(by='date').reset_index(drop=True)
    logger.info(f'Parsed: {path}')
    if len(df) > 0:
        df.is_outgoing = df.is_outgoing.astype(bool)
        df.is_edited = df.is_edited.astype(bool)
    return df
# Flow:5 ends here

# [[file:../../../org/vk.org::*Flow][Flow:6]]
@task
def store_directory(df):
    DBConn()
    df.to_sql(
        'messages',
        schema=settings["vk"]["schema"],
        con=DBConn.engine,
        if_exists='append'
    )
# Flow:6 ends here

# [[file:../../../org/vk.org::*Flow][Flow:7]]
@flow
def vk_load(directory):
    DBConn()
    schema = settings["vk"]["schema"]
    with DBConn.get_session() as db:
        db.execute(sa.text(f'create schema if not exists "{schema}"'))
        exists = db.execute(
            sa.text(
                f"select exists(select from information_schema.tables where table_schema = '{schema}' and table_name = 'messages')"
            )
        ).scalar_one()
        if exists:
            db.execute(sa.text(f'truncate table {schema}.messages'))
        db.commit()

    futures = []

    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        if not os.path.isdir(path) or path.endswith('.ipynb_checkpoints'):
            continue
        df = parse_directory(path)
        store_directory(df)

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        prog='sqrt_data_service.flows.vk.flow'
    )
    arg_parser.add_argument('-p', '--path', required=True)
    args = arg_parser.parse_args()
    vk_load(args.path)
# Flow:7 ends here
