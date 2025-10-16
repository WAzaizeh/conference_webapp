from .icon import Icon
from typing import List
from datetime import datetime
from zoneinfo import ZoneInfo
from db.schemas import Event, Speaker
from fasthtml.components import Ul, Li, Div, Hr, H3, H4, A, Img, Span

def AvatarCircle(src: str, alt: str, **kwargs) -> Div:
    return Div(
            Div(
                Img(src=src, alt=alt, cls='avatar circle'),
                cls='w-10 rounded-full'
                ),
            cls='avatar' + ' ' + kwargs.get('cls', '')
            )

def SpeakerCardBody(speakers_data: List[Speaker]) -> List:
    if speakers_data:
        # Get speaker names for comma-separated list
        speaker_names = ', '.join([speaker.name for speaker in speakers_data])
        
        return [
            Hr(cls='bg-secondary mt-4 mb-4 max-h-px'),
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
                        Span("Panel Discussion", cls="badge badge-accent badge-sm") if event.category == "PANEL DISCUSSION" else None,
                        Span("Workshop", cls="badge badge-neutral badge-sm") if event.category == "WORKSHOP" else None,
                        H3(event.title, cls='text-base font-medium'), 
                        *SpeakerCardBody(getattr(event, 'speakers_data', [])),
                        cls="timeline-box p-4 flex flex-col justify-evenly"
                    ),
                    href=f'/session/{event.id}' if event.description else None,
                ),
                cls='timeline-end ml-4'),
            Hr(cls='border-secondary' if datetime.now(ZoneInfo('America/Chicago')) > event.start_time else 'border-primary'),
        ) for i, event in enumerate(events)],
        cls='timeline timeline-vertical timeline-compact p-8'    
        )

def agenda_timeline_2(events: List[Event]):
    return Ul(
        *[Li(
            Div(
                Span(f'{event.start_time.strftime("%I:%M %p")} - {event.end_time.strftime("%I:%M %p")}', cls='text-sm text-primary ml-4'),
                cls='timeline-start'
            ),
            Div(
                Icon('circle', cls='text-primary' if datetime.now(ZoneInfo('America/Chicago')).hour > event.start_time.hour else 'text-secondary'),
                
                cls='timeline-middle'
            ),
            Div(
                A(
                    Div(
                        H3(event.title, cls='text-base'), 
                        *SpeakerCardBody(getattr(event, 'speakers_data', [])),
                        cls="timeline-box p-4 flex flex-col justify-evenly"
                    ),
                    href=f'/session/{event.id}' if event.description else None,
                ),
                cls='timeline-end ml-4'),
            Hr(cls='border-primary' if datetime.now(ZoneInfo('America/Chicago')).hour > event.end_time.hour else 'border-secondary'),
        ) for i, event in enumerate(events)],
        cls='timeline timeline-vertical timeline-compact p-8'    
        )