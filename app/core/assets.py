"""Static files in app/assets (served at /assets/...)."""
from pathlib import Path
from typing import Optional

ASSETS_DIR = Path(__file__).parent.parent / 'assets'
URL_PREFIX = '/assets/'


def available(url: Optional[str]) -> Optional[str]:
    """The URL if it can be shown: external links are trusted; /assets/ files must exist on disk.
    Returns None when there's nothing to show, so callers can fall back (initials, sponsor name)."""
    if not url:
        return None
    if url.startswith(URL_PREFIX):
        return url if (ASSETS_DIR / url[len(URL_PREFIX):]).is_file() else None
    return url
