from typing import List
from db.schemas import EventOut
from crud.core import get_speaker
from fasthtml.components import Ul, Li, Div, Hr, H3, P, H4, Img, I

def AvatarCircle(src: str, alt: str, **kwargs) -> Div:
    return Div(
            Div(
                Img(src=src, alt=alt, cls='avatar circle'),
                cls='w-14 rounded-full'
                ),
            cls='avatar' + ' ' + kwargs.get('cls', '')
            )

def SpeakerCardBody(speaker_ids: List[int]) -> Div:
    speaker = get_speaker(speaker_ids[0]) if speaker_ids else None
    print(speaker)
    if speaker:
        return Div(
            Hr(),
            Div(
                AvatarCircle(speaker.image_url, speaker.name, cls='mr-1'),
                H4(f'By {speaker.name}'),
                cls='flex flex-row items-center justify-start',
                ),
            cls='even-speaker-card',
        )
    else:
        Div(cls='hidden')

def agenda_timeline(events: List[EventOut]):
    return Ul(
        *[Li(
            Div(
                I(cls=f'fas fa-circle'),
                cls='timeline-middle'
            ),
            Div(f'{event.start_time.time().strftime("%H:%M")}',
                Div(
                    H3(event.title), 
                    SpeakerCardBody(event.speakers),
                    cls="timeline-box w-80-vw"
                ),
                hx_target='#page-content',
                hx_get=f'/sessions/{event.id}',
                cls='timeline-end'),
            Hr(),
            hx_target='#page-content',
            hx_get=f'/sessions/{event.id}',

        ) for event in events],
        cls='timeline timeline-vertical timeline-compact'    
        )