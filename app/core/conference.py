"""Conference schedule settings shared by routes that open or close with the event."""
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

CONFERENCE_TZ = ZoneInfo('America/Chicago')
CONFERENCE_START = datetime(2026, 10, 24, 11, 0, tzinfo=CONFERENCE_TZ)
CONFERENCE_END = datetime(2026, 10, 24, 20, 0, tzinfo=CONFERENCE_TZ)
FEEDBACK_OPEN_DAYS = 7

# Date windows are only enforced when explicitly enabled, so dev and testing always have access
RESTRICT_DATES = os.getenv('RESTRICT_TO_CONFERENCE_DAY', 'false').lower() == 'true'


def now() -> datetime:
    return datetime.now(CONFERENCE_TZ)


def is_conference_day() -> bool:
    """Q&A window: the calendar day of the conference"""
    return not RESTRICT_DATES or now().date() == CONFERENCE_START.date()


def is_feedback_open() -> bool:
    """Feedback window: from the first session until a week after the conference"""
    return not RESTRICT_DATES or CONFERENCE_START <= now() <= CONFERENCE_END + timedelta(days=FEEDBACK_OPEN_DAYS)
