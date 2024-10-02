from typing import List
from .icon import Icon, BrandIcon
from db.schemas import SpeakerOut, EventOut, PrayerTime, SponsorOut
from components.navigation import BackButton
from fasthtml.components import Div, Span, Figure, Img, H2, H1, P, Button, A, Hr


def homepage_card(icon_name : str, title: str, card_color: str, **kwargs) -> A:
    custom_cls = kwargs.pop('cls', '')  # Remove 'cls' from kwargs if present
    return A(
                P(title),
                Img(src=icon_name),
                cls=f'card-panel gray custom-card {card_color} {custom_cls}',
                **kwargs
            )

def brief_speaker_card(speaker: SpeakerOut) -> A:
    return A(
            Figure(
                    Img(src=f'/{speaker.image_url}', alt=speaker.name),
                    cls='figure'
                ),
            Div(
                H2(speaker.name),
                Button(Icon('chevron-circle-right speaker-btn')),
                cls='speaker-name',
                style={'display': 'flex',
                    'justify-content': 'space-between',
                    'align-items':'center',
                    'width':'100%',
                    'padding':'0 1rem'}
            ),
            cls='card speaker-card card-side bg-base-100 shadow-xl',
            href=f'/speaker/{speaker.id}',
        )


def speaker_page(speaker: SpeakerOut) -> Div:
    return Div(
            Div(
                BackButton(),
                H1('Speaker Profile', cls='flex-1 text-black font-medium text-center text-base'),
                cls='flex justify-center items-center p-4',
            ),
            Figure(
                Img(
                    src=f'/{speaker.image_url}',
                    alt=speaker.name,
                    cls='rounded-xl'
                ),
            ),
            Div(
                H2(speaker.name, cls='text-base mb-2'),
                P(speaker.bio, cls='text-sm'),
                cls='speaker-detail-body'
            ),
            cls='speaker-detail-view blue-background'
        )

def prayer_time_card(prayer : PrayerTime) -> Div:
    return Div(
            Div(
                P(prayer.name),
                P(prayer.time),
                cls='flex items-center justify-between',
                ),
            Div(
                A('Iqama'),
                A(prayer.iqama),
                cls='flex items-center justify-between text-primary',
                ),
            cls='prayer-card'
        )

def prayer_times_page(prayers: List[PrayerTime]) -> Div:
    return Div(
            *[prayer_time_card(prayer) for prayer in prayers],
        )

def brief_sponsor_card(sponsor: SponsorOut) -> Div:
    return Div(
            Figure(
                    Img(src=f'{sponsor.image_url}', alt=sponsor.name),
                    cls='figure'
                ),
            Div(
                H2(sponsor.name),
                Button(Icon('chevron-circle-right sponsor-btn')),
                cls='sponsor-name',
                style={'display': 'flex',
                    'justify-content': 'space-between',
                    'align-items':'center',
                    'width':'100%',
                    'padding':'0 1rem'}
            ),
            hx_target='#page-content',
            hx_get=f'/sponsors/{sponsor.id}',
            hx_swap='outerHTML',
            cls='card sponsor-card card-side bg-base-100 shadow-xl',
        )

def sponsor_page(sponsor: SponsorOut) -> Div:
    return Div(
            Div(
                BackButton(),
                H1('Sponsor Details', cls='flex-1 text-black font-medium text-center text-base'),
                cls='flex justify-center items-center p-4',
            ),
            Figure(
                Img(
                        src=f'{sponsor.image_url}',
                        alt=sponsor.name,
                        cls='rounded'
                    ),
                cls='flex'
            ),
            Div(
                    H2(sponsor.name, cls='text-base mb-2 font-medium'),
                    P(sponsor.description, cls='text-sm'),
                    Div(
                        P('Links and Socials', cls='text-sm mb-4 font-medium sponsor-social-title'),
                        Div(
                            A(Icon('link'), href=sponsor.website),
                            A(BrandIcon('facebook-f'), href=sponsor.facebook),
                            A(BrandIcon('twitter'), href=sponsor.twitter),
                            A(BrandIcon('instagram'), href=sponsor.instagram),
                            cls='sponsor-social-links flex items-center'
                        ),
                        cls='sponsor-social-container mt-10 text-left'
                    ),
                    cls='speaker-detail-body'
                ),
            
            cls='speaker-detail-view blue-background'
        )

def session_speaker_card(session: EventOut, speaker : SpeakerOut) -> Div:
    return Div(
                Div(
                    A(
                        Figure(
                        Img(src=f'/{speaker.image_url}', alt=speaker.name),
                        cls='figure',
                        ),
                        href=f'/speaker/{speaker.id}',
                    ),
                    Div(
                        H2(session.title, cls='text-base mb-1'),
                        Div(
                            P(f'By {speaker.name}', cls='text-sm'),
                            A(
                                Icon('chevron-circle-right', cls='color-light-blue'),
                                href=f'/speaker/{speaker.id}',
                            ),
                            cls='flex items-center justify-between',
                            ),
                    ),
                    cls='flex items-center card card-side session-card',
                ),
                Div(
                    Span(Icon('clock', solid=False), f"{session.start_time.strftime('%H:%M')} - {session.end_time.strftime('%H:%M')}", cls='session-detail'),
                    Span(Icon('calendar', solid=False), session.start_time.strftime('%b %d, %Y'), cls='session-detail'),
                    cls='flex items-center text-xs p-4 justify-between',
                ),
                cls='p-4 session-detail-view'
            )
