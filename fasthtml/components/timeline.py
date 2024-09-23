from .icon import Icon
from typing import List
from db.schemas import EventOut
from crud.core import get_speaker
from fasthtml.components import Ul, Li, Div, Hr, H3, P, H4, Img, I, Span

def AvatarCircle(src: str, alt: str, **kwargs) -> Div:
    return Div(
            Div(
                Img(src=src, alt=alt, cls='avatar circle'),
                cls='w-14 rounded-full'
                ),
            cls='avatar' + ' ' + kwargs.get('cls', '')
            )

def SpeakerCardBody(speaker_ids: List[int]) -> List:
    speaker = get_speaker(speaker_ids[0]) if speaker_ids else None
    if speaker:
        return [
            Hr(cls='bg-secondary'),
            Div(
                AvatarCircle(speaker.image_url, speaker.name, cls='mr-1'),
                H4(f'By {speaker.name}'),
                cls='flex flex-row items-center justify-start',
                ),
            ]
    else:
        return [
            Hr(cls='hidden'),
            Div(cls='hidden'),
        ]

def agenda_timeline(events: List[EventOut]):
    return Ul(
        *[Li(
            Hr(cls='bg-primary'),
            Div(
                Span(f'{event.start_time.time().strftime("%H:%M")}', cls='text-sm text-primary'),
                cls='timeline-start'
            ),
            Div(
                Icon('circle', cls='text-primary'),
                
                cls='timeline-middle'
            ),
            Div(
                Div(
                    H3(event.title), 
                    *SpeakerCardBody(event.speakers),
                    cls="timeline-box w-80-vw h-20-vh flex flex-col justify-evenly"
                ),
                hx_target='#page-content',
                hx_get=f'/sessions/{event.id}',
                cls='timeline-end'),
            Hr(cls='bg-primary'),
            hx_target='#page-content',
            hx_get=f'/sessions/{event.id}',

        ) for event in events],
        cls='timeline timeline-vertical timeline-compact p-8'    
        )