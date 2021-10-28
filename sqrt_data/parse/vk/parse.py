# [[file:../../../org/vk.org::*Parsing][Parsing:1]]
import pandas as pd
import os
import sys

from sqrt_data.api import DBConn, settings

from bs4 import BeautifulSoup
from collections import deque
from dateutil import parser
from tqdm import tqdm
# Parsing:1 ends here

# [[file:../../../org/vk.org::*Parsing][Parsing:2]]
__all__ = ['load']
# Parsing:2 ends here

# [[file:../../../org/vk.org::*Parsing][Parsing:4]]
def parse_date_english(date):
    is_edited = False
    if date.endswith(' (edited)'):
        is_edited = True
        date = date[:-9]
    date = date[2:]
    date = parser.parse(date)
    return is_edited, date
# Parsing:4 ends here

# [[file:../../../org/vk.org::*Parsing][Parsing:5]]
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
# Parsing:5 ends here

# [[file:../../../org/vk.org::*Parsing][Parsing:6]]
def parse_file(path):
    with open(path, 'r', encoding='windows-1251') as f:
        soup = BeautifulSoup(f)

    content = soup.html.body.div
    name = content.find(class_='page_content page_block'
                       ).h2.div.find(class_='_header_inner'
                                    ).find('div', class_='ui_crumb').text
    items = content.find(class_='page_content page_block'
                        ).find(class_='wrap_page_content')

    senders, dates, messages, edited = deque(), deque(), deque(), deque()

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

    global_author = settings['vk']['author']

    df = pd.DataFrame(
        {
            "target": name,
            "sender": [s if s != 'You' else global_author for s in senders],
            "is_outgoing": [s == 'You' for s in senders],
            "message": messages,
            "date": dates,
            "is_edited": edited
        }
    )
    return df
# Parsing:6 ends here

# [[file:../../../org/vk.org::*Parsing][Parsing:7]]
def parse_directory(path):
    files = sorted([f for f in os.listdir(path) if f.endswith('html')])
    df = pd.DataFrame(
        columns=[
            'target', 'sender', 'is_outgoing'
            'message', 'date', 'is_edited'
        ]
    )
    for file in tqdm(files, desc=path):
        df_ = parse_file(os.path.join(path, file))
        df = pd.concat([df, df_])
    df = df.sort_values(by='date').reset_index(drop=True)
    return df
# Parsing:7 ends here

# [[file:../../../org/vk.org::*Parsing][Parsing:8]]
def load(directory):
    DBConn()
    DBConn.engine.execute(f'DROP SCHEMA IF EXISTS {settings["vk"]["schema"]}')
    DBConn.create_schema(settings["vk"]["schema"])

    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        if not os.path.isdir(path) or path.endswith('.ipynb_checkpoints'):
            continue

        df = parse_directory(path)
        df.to_sql(
            'messages',
            schema=settings["vk"]["schema"],
            con=DBConn.engine,
            if_exists='append'
        )
# Parsing:8 ends here
