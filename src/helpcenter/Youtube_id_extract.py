import re

def extract_youtube_id(url):
    patterns = [
        r"youtu\.be\/([^\/]+)",
        r"v=([^&]+)",
        r"embed\/([^\/]+)"
    ]
    for p in patterns:
        m = re.search(p, url)
        if m:
            return m.group(1)
    return None

def save(self, *args, **kwargs):
    if self.youtube_url and not self.youtube_id:
        self.youtube_id = extract_youtube_id(self.youtube_url)
    super().save(*args, **kwargs)
