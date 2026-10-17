"""Conference schedule settings shared by routes that open or close with the event."""
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

CONFERENCE_TZ = ZoneInfo('America/Chicago')
CONFERENCE_START = datetime(2026, 10, 24, 11, 0, tzinfo=CONFERENCE_TZ)
CONFERENCE_END = datetime(2026, 10, 24, 20, 0, tzinfo=CONFERENCE_TZ)
FEEDBACK_OPEN_DAYS = 7
# With COMING_SOON=true (production), the site shows only the coming soon page until SITE_OPENS
SITE_OPENS = datetime(2026, 10, 17, 7, 0, tzinfo=CONFERENCE_TZ)
# Q&A and feedback open an hour before the first session
INTERACTIVE_OPENS = datetime(2026, 10, 24, 10, 0, tzinfo=CONFERENCE_TZ)

# Date windows are enforced on production only, so dev and testing always have access.
# RESTRICT_TO_CONFERENCE_DAY=true/false overrides this in any environment.
IS_PRODUCTION = os.getenv('ENVIRONMENT', '').lower() == 'production'
RESTRICT_DATES = os.getenv('RESTRICT_TO_CONFERENCE_DAY', str(IS_PRODUCTION)).lower() == 'true'
COMING_SOON = os.getenv('COMING_SOON', 'false').lower() == 'true'


def now() -> datetime:
    return datetime.now(CONFERENCE_TZ)


def is_coming_soon() -> bool:
    """Before the site opens, only the coming soon page is served"""
    return COMING_SOON and now() < SITE_OPENS


def is_conference_day() -> bool:
    """Q&A window: from INTERACTIVE_OPENS until the end of the conference day"""
    current = now()
    return not RESTRICT_DATES or (INTERACTIVE_OPENS <= current and current.date() == CONFERENCE_START.date())


def is_feedback_open() -> bool:
    """Feedback window: from INTERACTIVE_OPENS until a week after the conference"""
    return not RESTRICT_DATES or INTERACTIVE_OPENS <= now() <= CONFERENCE_END + timedelta(days=FEEDBACK_OPEN_DAYS)
