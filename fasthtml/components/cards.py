from .icons import Icon
from db.schemas import SpeakerOut, EventOut
from fasthtml.components import Div, Span, Figure, Img, H2, P, Button


def homepage_card(icon_name : str, title: str, card_color: str, **kwargs):
    return Div(
                P(title),
                Img(src=icon_name),
                cls='card-panel full-card gray custom-card ' + card_color,
                **kwargs
            )

def speaker_card(event: EventOut, speaker : SpeakerOut):
    return Div(
                Figure(Img(src=speaker.image_url, alt=speaker.name)),
                Div(
                    H2(event.title),
                    P(f'By {speaker.name}'),
                    P(speaker.bio),
                ),
                hx_target='#page-content',
                hx_get=f'/speakers/{speaker.id}',
                hx_swap='outerHTML',
                cls='card card-side bg-base-100 shadow-xl',
            )


def brief_speaker_card(speaker: SpeakerOut):
    return Div(
            Figure(
                    Img(src=speaker.image_url, alt=speaker.name),
                    style={'width':'55vw'}
                ),
            Div(
                H2(speaker.name),
                Button(Icon('chevron-right')),
                cls='speaker-name',
                style={'display': 'flex',
                    'justify-content': 'space-between',
                    'align-items':'center',
                    'width':'100%',
                    'padding':'0 1rem'}
            ),
            hx_target='#page-content',
            hx_get=f'/speakers/{speaker.id}',
            hx_swap='outerHTML',
            cls='card card-side bg-base-100 shadow-xl',
        )


def speaker_page(speaker: SpeakerOut):
    return Div(
            Figure(
                Img(
                    src=speaker.image_url,
                    alt=speaker.name,
                    cls="rounded-xl"
                ),
                cls="px-10 pt-10"
            ),
            Div(
                H2(speaker.name, cls="card-title"),
                P(speaker.bio),
                cls="card-body items-center text-center"
            ),
            cls="card bg-base-100 w-96 shadow-xl"
        )