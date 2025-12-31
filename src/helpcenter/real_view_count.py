import requests
from decouple import config
from django.core.cache import cache
import re

YOUTUBE_DATA_API = config("YOUTUBE_DATA_API")


def parse_duration(iso):
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso)
    if not match:
        return None

    h, m, s = match.groups(default="0")
    h, m, s = int(h), int(m), int(s)

    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def get_youtube_data(video_id):
    if not video_id:
        return None

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics,contentDetails,snippet",
        "id": video_id,
        "key": YOUTUBE_DATA_API,
    }

    r = requests.get(url, params=params, timeout=5)
    data = r.json()

    try:
        item = data["items"][0]
    except (KeyError, IndexError):
        return None

    return {
        "title": item["snippet"]["title"],
        "views": int(item["statistics"]["viewCount"]),
        "duration": parse_duration(item["contentDetails"]["duration"]),
        "thumbnail": item["snippet"]["thumbnails"]["high"]["url"],
    }


def get_cached_youtube_data(video_id):
    key = f"yt_data_{video_id}"
    data = cache.get(key)

    if data is None:
        data = get_youtube_data(video_id)
        cache.set(key, data, 3600)

    return data
