from decouple import config
from django.core.cache import cache

YOUTUBE_DATA_API = config("YOUTUBE_DATA_API")

def get_youtube_views(requests, video_id):
    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "statistics",
        "id": video_id,
        "key": YOUTUBE_DATA_API
    }
    r = requests.get(url, params=params)
    data = r.json()

    if "items" not in data or not data["items"]:
        return 0

    return int(data["items"][0]["statistics"]["viewCount"])



def get_cached_views(video_id):
    key = f"yt_views_{video_id}"
    views = cache.get(key)

    if views is None:
        views = get_youtube_views(video_id)
        cache.set(key, views, 3600)

    return views