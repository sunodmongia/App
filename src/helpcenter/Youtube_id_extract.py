import re

YOUTUBE_PATTERNS = [
    r"(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^\/\?\&]+)",
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)",
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^\/\?\&]+)",
    r"(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([^\/\?\&]+)",
]


def extract_youtube_id(url):
    for pattern in YOUTUBE_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def save(self, *args, **kwargs):
    if self.youtube_url:
        self.youtube_id = extract_youtube_id(self.youtube_url)
    else:
        self.youtube_id = ""
    super().save(*args, **kwargs)
