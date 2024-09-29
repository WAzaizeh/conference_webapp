from .icon import Icon
from typing import List
from db.schemas import SpeakerOut, EventOut, PrayerTime
from fasthtml.components import Div, Span, Figure, Img, H2, P, Button, A, Hr


def homepage_card(icon_name : str, title: str, card_color: str, **kwargs) -> A:
    return A(
                P(title),
                Img(src=icon_name),
                cls='card-panel full-card gray custom-card ' + card_color,
                **kwargs
            )

def speaker_card(session: EventOut, speaker : SpeakerOut) -> Div:
    return Div(
                Figure(Img(src=speaker.image_url, alt=speaker.name)),
                Div(
                    H2(session.title),
                    P(f'By {speaker.name}'),
                    Div(
                        Span(Icon('clock'), f"{session.start_time.strftime('%H %M')} - {session.end_time.strftime('%H %M')}", cls='session-detail'),
                        Span(Icon('calendar'), session.start_time.strftime('%b %d, %Y'), cls='session-detail'),
                        Span(Icon('map-pin'), 'Room 101', cls='session-detail'),
                        cls="card-actions"
                    ),
                    cls='card-body'
                ),
                hx_target='#page-content',
                hx_get=f'/speakers/{speaker.id}',
                hx_swap='outerHTML',
                cls='card card-side bg-base-100 shadow-xl',
            )


def brief_speaker_card(speaker: SpeakerOut) -> Div:
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


def speaker_page(speaker: SpeakerOut) -> Div:
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

def prayer_time_card(prayer : PrayerTime) -> Div:
    return Div(
            Div(
                A(prayer.name),
                A(prayer.time),
                cls='flex items-center justify-between',
                ),
            Div(
                A('Iqama'),
                A(prayer.iqama),
                cls='flex items-center justify-between text-primary',
                ),
            Hr(cls='bg-secondary h-1 my-8'),
            cls='prayer-card'
        )

def prayer_times_page(prayers: List[PrayerTime]) -> Div:
    return Div(
            *[prayer_time_card(prayer) for prayer in prayers],
            cls='p-8'
        )