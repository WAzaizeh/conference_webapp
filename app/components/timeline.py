from .icon import Icon
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from db.schemas import Event, Speaker
from fasthtml.components import Ul, Li, Div, Hr, H3, H4, A, Img, Span, Button
from utils.tags import SHARED_TAG, TRACK_TAGS
import json

def SpeakerCardBody(speakers_data: List[Speaker]) -> List:
    if speakers_data:
        # Get speaker names for comma-separated list
        speaker_names = ', '.join([speaker.name for speaker in speakers_data])
        
        return [
            Hr(cls='bg-secondary', style='height:1px;'),
            Div(
                # Avatar group - overlapping circular images
                Div(
                    *[
                        Div(
                            Img(src=speaker.image_url, alt=speaker.name, cls='avatar circle'),
                            cls='w-10 h-10 rounded-full'
                        ) for speaker in speakers_data
                    ],
                    cls='avatar-group -space-x-3'
                ),
                # Comma-separated speaker names
                H4(f'By {speaker_names}', cls='text-sm ml-2'),
                cls='flex flex-row items-center justify-start',
            )
        ]
    else:
        return [
            Hr(cls='hidden'),
            Div(cls='hidden'),
        ]

def TagBadges(tags: List[str]):
    """Small labels for a session's tags (the shared marker is not shown)"""
    visible = [t for t in tags or [] if t != SHARED_TAG]
    return Div(*[Span(t, cls='badge badge-sm tag-badge') for t in visible], cls='flex flex-wrap gap-1') if visible else None


def TagFilter(tags: List[str]):
    """Filter pills above the agenda; tapping pills narrows to sessions with all of them
    (behaviour in assets/agenda-filter.js)"""
    if not tags:
        return None
    return Div(
        *[Button(t, type='button', cls='tag-pill active', data_tag=t, aria_pressed='false') for t in tags],
        Button('Clear', type='button', cls='tag-clear', hidden=True),
        id='agenda-filter',
        data_track_tags=json.dumps(TRACK_TAGS),
        role='group',
        aria_label='Filter sessions',
    )


def agenda_timeline(events: List[Event]):
    return Ul(
        *[Li(
            Div(
                Span(f'{event.start_time.strftime("%I:%M %p")} - {event.end_time.strftime("%I:%M %p")}', cls='text-sm text-primary ml-4'),
                cls='timeline-start'
            ),
            Div(
                Icon('circle', cls='text-secondary' if datetime.now(ZoneInfo('America/Chicago')) > event.start_time else 'text-primary'),
                cls='timeline-middle'
            ),
            Div(
                A(
                    Div(
                        Div(
                            TagBadges(event.tags),
                            H3(event.title, cls='text-base font-medium'),
                            cls="flex flex-col gap-2"
                        ),
                        *SpeakerCardBody(event.speakers),
                        cls="timeline-box p-4 flex flex-col gap-4"
                    ),
                    href=f'/session/{event.id}' if event.description else None,
                ),
                cls='timeline-end ml-4'),
            Hr(cls='border-secondary' if datetime.now(ZoneInfo('America/Chicago')) > event.start_time else 'border-primary'),
            data_tags=json.dumps(event.tags or []),
        ) for i, event in enumerate(events)],
        cls='timeline timeline-vertical timeline-compact p-8'    
        )
