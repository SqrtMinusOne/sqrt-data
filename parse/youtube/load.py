import os
import json
import pandas as pd
import urllib
import isodate
from collections import deque
from googleapiclient.discovery import build

from api import Config, is_updated


__all__ = ['youtube_load']


def get_df():
    filename = os.path.expanduser(Config.YOUTUBE_HISTORY)
    with open(filename, 'r') as f:
        data = json.load(f)
    entries = deque()
    for datum in data:
        try:
            if datum['details'][0]['name'] == 'From Google Ads':
                continue
        except KeyError:
            pass
        if 'titleUrl' not in datum:
            continue
        q = urllib.parse.urlparse(datum['titleUrl']).query
        video_id = urllib.parse.parse_qs(q)['v'][0]
        entries.append({
            'id': video_id,
            # 'title': datum['title'][8:],
            # 'channel': datum['subtitles'][0]['name'],
            'timestamp': pd.Timestamp(datum['time'])
        })
    df = pd.DataFrame(entries)
    return df


def get_data(df):
    api = build('youtube', 'v3', developerKey=Config.GOOGLE_API)

    publish_date, title, channel, lang = deque(), deque(), deque(), deque()
    duration, definition, view_count = deque(),deque(), deque()
    for row in df.itertuples(index=False):
        request = api.videos().list(
            part="contentDetails,snippet,statistics",
            id=row.id
        )
        response = request.execute()

        datum = response['items'][0]
        publish_date.append(datum['snippet']['publishedAt'])
        title.append(datum['snippet']['title'])
        channel.append(datum['snippet']['channelTitle'])
        lang.append(datum['snippet']['defaultAudioLanguage'])
        duration.append(
            isodate.parse_duration(datum['contentDetails']['duration'])
                .total_seconds() / 60
        )
        definition.append(datum['contentDetails']['definition'])
        view_count.append(datum['statistics']['viewCount'])

    df = df.assign(
        publish_date=publish_date,
        title=title,
        channel=channel,
        lang=lang,
        duration=duration,
        definition=definition,
        view_count=view_count
    )
    return df


def youtube_load():
    df = get_df()[:10]
    __import__('pudb').set_trace()
    df = get_data(df)
    print('hello')
