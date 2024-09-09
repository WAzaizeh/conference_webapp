from db.schemas import EventOut
from typing import List
from fasthtml.components import Ul, Li, Div, Hr, H3, P
from fasthtml.common import *

def agenda_timeline(events: List[EventOut]):
    return Ul(
        *[Li(
            Div(
                I(cls=f'fas fa-circle'),
                cls='timeline-middle'
            ),
            Div(f'{event.start_time.time().strftime("%H:%M")}',
                Div(
                    H3(event.title, cls="font-bold"),
                    P(event.description),
                    cls="timeline-box"
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