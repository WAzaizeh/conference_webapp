"""Session tags: free-form labels used to filter the agenda (e.g. Masculinity, Workshop, Prayer).

SHARED_TAG marks sessions for everyone (keynotes, prayers, breaks); they stay visible whatever
filter is selected, so a filtered agenda is still a complete schedule for that attendee.
"""
from typing import Iterable, List

SHARED_TAG = 'All'

# Preferred pill order; any other tags follow alphabetically
TAG_ORDER = ['Masculinity', 'Womanhood', 'Talk', 'Workshop', 'Panel', 'Discussion', 'Presentation', 'Prayer', 'Break']

# Former single "category" values -> tags (used by the migration and legacy importers)
CATEGORY_TAGS = {
    'MAIN': [SHARED_TAG],
    'TALK': ['Talk'],
    'PANEL DISCUSSION': ['Panel'],
    'WORKSHOP': ['Workshop'],
    'LIGHTNING_TALK': ['Talk'],
    'PRESENTATION': ['Presentation'],
    'ACTIVITY': ['Discussion'],
    'BREAK': ['Break', SHARED_TAG],
    'PRAYER': ['Prayer', SHARED_TAG],
}

TRACK_PREFIXES = {'Masculinity Track': 'Masculinity', 'Womanhood Track': 'Womanhood'}


def normalize_tags(tags: Iterable[str]) -> List[str]:
    """Trim, drop blanks, and de-duplicate case-insensitively (first spelling wins)"""
    seen, result = set(), []
    for tag in tags:
        tag = ' '.join(str(tag).split())
        if tag and tag.lower() not in seen:
            seen.add(tag.lower())
            result.append(tag)
    return sort_tags(result)


def sort_tags(tags: Iterable[str]) -> List[str]:
    order = {t.lower(): i for i, t in enumerate([SHARED_TAG, *TAG_ORDER])}
    return sorted(tags, key=lambda t: (order.get(t.lower(), len(order)), t.lower()))


def tags_from_category(category: str, title: str = '') -> List[str]:
    """Tags for a session that only has the old category: category tags, track from the title
    prefix, and keynotes marked as shared"""
    tags = list(CATEGORY_TAGS.get((category or 'MAIN').upper(), [category.replace('_', ' ').title()]))
    for prefix, track in TRACK_PREFIXES.items():
        if title.startswith(prefix):
            tags.append(track)
    if 'keynote' in title.lower():
        tags.append(SHARED_TAG)
    return normalize_tags(tags)


def filter_tags(events) -> List[str]:
    """Tags offered as agenda filter pills (every tag in use except the shared marker)"""
    return sort_tags({t for e in events for t in (e.tags or []) if t != SHARED_TAG})
