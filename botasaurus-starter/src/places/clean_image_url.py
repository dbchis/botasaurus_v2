import re


def clean_image_url(url: str) -> str:
    if not url:
        return url
    return re.sub(r'=w\d+-h\d+.*$', '', url)
