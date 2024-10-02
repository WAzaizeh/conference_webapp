from .icon import Icon
from typing import List
from db.schemas import EventOut
from crud.core import get_speaker
from fasthtml.components import Ul, Li, Div, Hr, H3, A, H4, Img, I, Span

def AvatarCircle(src: str, alt: str, **kwargs) -> Div:
    return Div(
            Div(
                Img(src=src, alt=alt, cls='avatar circle'),
                cls='w-10 rounded-full'
                ),
            cls='avatar' + ' ' + kwargs.get('cls', '')
            )

def SpeakerCardBody(speaker_ids: List[int]) -> List:
    speaker = get_speaker(speaker_ids[0]) if speaker_ids else None
    if speaker:
        return [
            Hr(cls='bg-secondary mt-4 mb-4 max-h-px'),
            Div(
                AvatarCircle(f'/{speaker.image_url}', speaker.name, cls='mr-4'),
                H4(f'By {speaker.name}', cls='text-xs'),
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
            Hr(cls='bg-primary') if i > 0 else None,
            Div(
                Span(f'{event.start_time.time().strftime("%H:%M")} - {event.end_time.time().strftime("%H:%M")}', cls='text-sm text-primary'),
                cls='timeline-start'
            ),
            Div(
                Icon('circle', cls='text-primary'),
                
                cls='timeline-middle'
            ),
            Div(
                A(
                    Div(
                        H3(event.title, cls='text-sm'), 
                        *SpeakerCardBody(event.speakers),
                        cls="timeline-box p-4 flex flex-col justify-evenly"
                    ),
                    href=f'/session/{event.id}',
                ),
                cls='timeline-end ml-4'),
            Hr(cls='bg-primary'),
        ) for i, event in enumerate(events)],
        cls='timeline timeline-vertical timeline-compact p-8'    
        )