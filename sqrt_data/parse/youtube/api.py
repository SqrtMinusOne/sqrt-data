import json
import re
import requests

from sqrt_data.api import settings, DBConn
from sqrt_data.models import Base
from sqrt_data.models.youtube import Channel, Video, Category

__all__ = ['get_video_by_id', 'init_db']

def get_channel_by_id(id, db):
    channel = db.query(Channel).filter_by(id=id).first()
    if channel:
        return channel

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
        channel_item['country'] = channel_data['items'][0]['snippet']['country']
    channel = Channel(**channel_item)
    db.add(channel)
    return channel

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

def get_video_by_id(id, db):
    video = db.query(Video).filter_by(id=id).first()
    if video:
        return video

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
        return None
    item = video_data['items'][0]['snippet']
    get_channel_by_id(item['channelId'], db)
    video = Video(**{
        'id': id,
        'channel_id': item['channelId'],
        'category_id': item['categoryId'],
        'name': item['title'],
        'url': f'https://youtube.com/watch?v={id}',
        'language': item['defaultLanguage'],
        'created': item['publishedAt'],
        'duration': yt_time(video_data['items'][0]['contentDetails']['duration'])
    })
    db.add(video)
    return video

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
        # init_categories(db)
        get_video_by_id('_OsIW3ufZ6I', db)
        db.commit()
