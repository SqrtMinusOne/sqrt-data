# [[file:../../../org/messengers.org::*Telegram][Telegram:1]]
import argparse
import json
import pandas as pd
import sqlalchemy as sa
from prefect import task, flow, get_run_logger
from collections import deque

from sqrt_data_service.api import settings, DBConn
# Telegram:1 ends here

# [[file:../../../org/messengers.org::*Telegram][Telegram:2]]
@task
def parse_json(file_name):
    with open(file_name) as f:
        data = json.load(f)

    me_id = f'user{data["personal_information"]["user_id"]}'
    me = ' '.join(
        [
            data["personal_information"]["first_name"],
            data["personal_information"]["last_name"]
        ]
    )
    messages = deque()

    for chat in data['chats']['list']:
        if chat['id'] in settings.messengers.telegram.exclude_ids or chat[
            'type'] == 'saved_messages':
            continue
        name = chat['name']
        is_group = chat['type'] != 'personal_chat'
        target = name
        if is_group is False:
            for message in chat['messages']:
                if message['type'] != 'message':
                    continue
                if message['from_id'] != me_id:
                    target = message['from']
                    break

        for message in chat['messages']:
            if message['type'] != 'message':
                continue
            text = message['text']
            if isinstance(text, list):
                text = ' '.join(
                    [
                        token['text'] if isinstance(token, dict) else token
                        for token in text
                    ]
                )
            is_outgoing = message['from_id'] == me_id
            messages.append(
                {
                    'target': target,
                    'sender': message['from'],
                    'is_outgoing': is_outgoing,
                    'is_group': is_group,
                    'message': text,
                    'date': message['date'],
                    'is_edited': 'edited' in message
                }
            )

    df = pd.DataFrame(messages)
    df.date = df.date.astype('datetime64[ns]')
    return df
# Telegram:2 ends here

# [[file:../../../org/messengers.org::*Telegram][Telegram:3]]
@task
def store_df(df):
    DBConn()
    with DBConn.get_session() as db:
        db.execute(sa.text('create schema if not exists "messengers"'))
        exists = DBConn.table_exists('telegram', 'messengers', db)
        if exists:
            db.execute(sa.text('truncate table messengers.telegram'))
        db.commit()

    df.to_sql(
        'telegram', schema='messengers', con=DBConn.engine, if_exists='append'
    )
# Telegram:3 ends here

# [[file:../../../org/messengers.org::*Telegram][Telegram:4]]
@flow
def telegram_load(file_name):
    df = parse_json(file_name)
    store_df(df)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='sqrt_data_service.flows.messengers.telegram'
    )
    parser.add_argument('-p', '--path', required=True)
    args = parser.parse_args()
    telegram_load(args.path)
# Telegram:4 ends here
