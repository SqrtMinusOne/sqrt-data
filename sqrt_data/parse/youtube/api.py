import json
import re
import requests
import pandas as pd
import sqlalchemy as sa

from urllib.parse import urlparse, parse_qs

from sqrt_data.api import settings, DBConn
from sqrt_data.models import Base
from sqrt_data.models.youtube import Channel, Video, Category, Watch

__all__ = [
    'get_video_by_id', 'init_db', 'get_video_id', 'store_logs', 'create_views'
]

def get_channel_by_id(id, db):
    channel = db.query(Channel).filter_by(id=id).first()
    if channel:
        return channel, False

    channel_response = requests.get(
        'https://youtube.googleapis.com/youtube/v3/channels',
        params={
            'part': 'snippet',
            'id': id,
            'key': settings['google']['api_key']
        }
    )
    channel_response.raise_for_status()
    channel_data = channel_response.json()
    channel_item = {
        'id': id,
        'url': f'https://youtube.com/c/{id}',
        'name': 'unknown'
    }
    if len(channel_data['items']) > 0:
        channel_item['name'] = channel_data['items'][0]['snippet']['title']
        channel_item['description'] = channel_data['items'][0]['snippet'][
            'description']
        channel_item['country'] = channel_data['items'][0]['snippet'].get('country', None)
    channel = Channel(**channel_item)
    db.add(channel)
    return channel, True

def yt_time(duration="P1W2DT6H21M32S"):
    """
    Converts YouTube duration (ISO 8061)
    into Seconds

    see http://en.wikipedia.org/wiki/ISO_8601#Durations
    """
    ISO_8601 = re.compile(
        'P'   # designates a period
        '(?:(?P<years>\d+)Y)?'   # years
        '(?:(?P<months>\d+)M)?'  # months
        '(?:(?P<weeks>\d+)W)?'   # weeks
        '(?:(?P<days>\d+)D)?'    # days
        '(?:T' # time part must begin with a T
        '(?:(?P<hours>\d+)H)?'   # hours
        '(?:(?P<minutes>\d+)M)?' # minutes
        '(?:(?P<seconds>\d+)S)?' # seconds
        ')?')   # end of time part
    # Convert regex matches into a short list of time units
    units = list(ISO_8601.match(duration).groups()[-3:])
    # Put list in ascending order & remove 'None' types
    units = list(reversed([int(x) if x != None else 0 for x in units]))
    # Do the maths
    return sum([x*60**units.index(x) for x in units])

def process_language(item):
    lang = item.get('defaultLanguage', None) or item.get('defaultAudioLanguage', None)
    if not lang:
        return '??'
    return lang.split('-')[0]

def get_video_by_id(id, db):
    video = db.query(Video).filter_by(id=id).first()
    if video:
        return video, False

    video_response = requests.get(
        'https://youtube.googleapis.com/youtube/v3/videos',
        params={
            'part': 'snippet,contentDetails',
            'id': id,
            'key': settings['google']['api_key']
        }
    )
    video_response.raise_for_status()
    video_data = video_response.json()
    if len(video_data['items']) == 0:
        print(f'Video not found : {id}')
        return None, None
    item = video_data['items'][0]['snippet']
    _, new_channel = get_channel_by_id(item['channelId'], db)
    if new_channel:
        db.flush()
    video = Video(**{
        'id': id,
        'channel_id': item['channelId'],
        'category_id': item['categoryId'],
        'name': item['title'],
        'url': f'https://youtube.com/watch?v={id}',
        'language': process_language(item),
        'created': item['publishedAt'],
        'duration': yt_time(video_data['items'][0]['contentDetails']['duration'])
    })
    db.add(video)
    return video, True

def init_categories(db):
    categories_response = requests.get(
        'https://youtube.googleapis.com/youtube/v3/videoCategories',
        params={
            'part': 'snippet',
            'regionCode': 'US',
            'key': settings['google']['api_key']
        }
    )
    categories_response.raise_for_status()
    categories = categories_response.json()['items']
    for category in categories:
        db.merge(
            Category(id=int(category['id']), name=category['snippet']['title'])
        )

def init_db():
    DBConn()
    DBConn.create_schema('youtube', Base)

    with DBConn.get_session() as db:
        init_categories(db)
        # get_video_by_id('_OsIW3ufZ6I', db)
        db.commit()

def get_video_id(url):
    data = urlparse(url)
    query = parse_qs(data.query)
    id = query.get('v', [None])[0]
    if id is None:
        return
    if id.endswith(']'):
        id = id[:-1]
    return id

def store_logs(logs, db):
    date = logs[0]['date']
    df = pd.DataFrame(logs)
    df = df.groupby(by=['video_id', 'kind', 'date']).sum().reset_index()
    db.execute(
        sa.delete(Watch).where(
            sa.and_(Watch.date == date, Watch.kind == logs[0]['kind'])
        )
    )
    missed = False
    for _, item in df.iterrows():
        video, added = get_video_by_id(item['video_id'], db)
        if added:
            db.flush()
        if video:
            db.add(Watch(**item))
        else:
            missed = True
    return missed

def create_views():
    DBConn()
    DBConn.engine.execute('DROP VIEW IF EXISTS "youtube"."watch_data"')
    DBConn.engine.execute(
    '''
    CREATE VIEW youtube.watch_data AS
    SELECT V.*, W.duration watched, W.kind, W.date, C.name category, C2.name channel_name, C2.country channel_country
    FROM youtube.watch W
             INNER JOIN youtube.video V ON W.video_id = V.id
             INNER JOIN youtube.category C ON V.category_id = C.id
             INNER JOIN youtube.channel C2 ON V.channel_id = C2.id;
    '''
    )
