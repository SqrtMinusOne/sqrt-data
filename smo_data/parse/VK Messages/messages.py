import glob
import pandas as pd
import os
import sys

from smo_data.api import DBConn
from smo_data.models import VkMessage, VkUser, Base

from bs4 import BeautifulSoup
from collections import deque
from dateutil import parser
from IPython.core.debugger import set_trace
from tqdm import tqdm

sys.path.append('/..')


MESSAGES_DIR = 'source/messages'
AUTHOR = 'Pavel Korytov'
MONTHS = 'янв', 'фев', 'мар', 'апр', 'мая', 'июн',     'июл', 'авг', 'сен', 'окт', 'ноя', 'дек'

def parse_date_russian(date):
    is_edited = False
    if date.endswith(' (ред.)'):
        is_edited = True
        date = date[:-7]
    day, month, year, _, time = date.split()

    month = MONTHS.index(month) + 1
    date = parser.parse(time).replace(day=int(day), month=month, year=int(year))
    return is_edited, date


def parse_date_english(date):
    is_edited = False
    if date.endswith(' (edited)'):
        is_edited = True
        date = date[:-9]
    date = date[2:]
    date = parser.parse(date)
    return is_edited, date


def parse_file(path):
    with open(path, 'r', encoding='windows-1251') as file:
        soup = BeautifulSoup(file)

        content = soup.html.body.div
        name = content.find(class_='page_content page_block').h2.div.find(class_='_header_inner')             .find('div', class_='ui_crumb').text
        items = content.find(class_='page_content page_block').find(class_='wrap_page_content')

        senders, recipients, dates, messages, edited = deque(), deque(), deque(), deque(), deque()

        for item in items.find_all(class_='item'):
            header = item.div.find(class_='message__header')
            author, date = header.text.split(', ', 1)
            if author == 'You':
                author, recipient = AUTHOR, name
            else:
                recipient = AUTHOR

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
                recipients.append(recipient)
                dates.append(date)
                messages.append(message)
                edited.append(is_edited)

        return pd.DataFrame({
            "sender": senders,
            "recepient": recipients,
            "message": messages,
            "date": dates,
            "is_edited": edited
        }), name

def fix_group(df, name):
    recepients = df.recepient.unique()
    df.sender = df.sender.apply(lambda sender: AUTHOR if sender == AUTHOR else name)
    return df


def parse_directory(path):
    files = sorted([file for file in os.listdir(path) if file.endswith('html')])
    df = pd.DataFrame(columns=['sender', 'recipient', 'message', 'date', 'is_edited'])
    for file in tqdm(files, desc=path):
        df_, name = parse_file(os.path.join(path, file))
        df = pd.concat([df, df_])
    df = df.sort_values(by='date').reset_index(drop=True)
    return df, name


DBConn()

DBConn.engine.execute('DROP SCHEMA IF EXISTS vk CASCADE')
DBConn.engine.execute('CREATE SCHEMA vk')
tables = []
for name, table in Base.metadata.tables.items():
    if table.schema == 'vk':
        tables.append(table)
Base.metadata.create_all(DBConn.engine, tables)


for file in os.listdir(MESSAGES_DIR):
    path = os.path.join(MESSAGES_DIR, file)
    if os.path.isdir(path):
        id_ = file
        if path.endswith('.ipynb_checkpoints'):
            continue
        df, name = parse_directory(path)

        df['target_id'] = id_
        is_group = df.sender.nunique() > 2
        if is_group:
            df = fix_group(df, name)
        with DBConn.get_session() as db:
            user = VkUser(name=name, id=id_, is_group=is_group)
            data = df.to_dict(orient='records')
            db.add(user)
            db.commit()

            db.bulk_insert_mappings(VkMessage, data)
            db.commit()
