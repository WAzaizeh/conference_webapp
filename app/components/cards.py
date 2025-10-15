from typing import List
from .icon import Icon, BrandIcon
from db.schemas import Speaker, Event, PrayerTime, Sponsor
from components.navigation import TopNav
from fasthtml.components import Div, Span, Figure, Img, H2, H1, P, Button, A, Hr


def homepage_card(icon_name : str, title: str, card_color: str, bold_style: bool = False, **kwargs) -> A:
    custom_cls = kwargs.pop('cls', '')  # Remove 'cls' from kwargs if present
    if bold_style:
        custom_cls += ' font-bold border-2 border-pink-300 shadow-lg'
    return A(
                P(title),
                Img(src=icon_name),
                cls=f'card-panel gray custom-card {card_color} {custom_cls}',
                **kwargs
            )

def brief_speaker_card(speaker: Speaker) -> A:
    return A(
            Figure(
                    Img(src=speaker.image_url, alt=speaker.name),
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
            href=f'/speakers/{speaker.id}',
        )


def speaker_page(speaker: Speaker) -> Div:
    return Div(
            Figure(
                Img(
                    src=speaker.image_url,
                    alt=speaker.name,
                    cls='rounded-xl'
                ),
            ),
            Div(
                H2(speaker.name, cls='text-base mb-2 font-medium'),
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

def brief_sponsor_card(sponsor: Sponsor) -> Div:
    return A(
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
            cls='card sponsor-card card-side bg-base-100 shadow-xl',
            href=f'/sponsors/{sponsor.id}',
        )

def sponsor_page(sponsor: Sponsor) -> Div:
    return Div(
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
                    cls='sponsor-detail-body'
                ),
            
            cls='sponsor-detail-view blue-background'
        )

def session_speaker_card(session: Event, speakers: List[Speaker]) -> Div:
    """Display session with multiple speakers using avatar group"""
    return Div(
        Div(
            # Title in top row
            H2(session.title, cls='text-base mb-3 font-medium'),
            # Bottom row: avatars left, names right
            Div(
                # Avatar group - overlapping circular images on left
                Div(
                    *[
                        A(
                            Div(
                                Img(src=speaker.image_url, alt=speaker.name),
                                cls='w-12 h-12 rounded-full'
                            ),
                            href=f'/speakers/{speaker.id}',
                            cls='avatar hover:z-10 hover:scale-110 transition-transform'
                        ) for speaker in speakers
                    ],
                    cls='avatar-group -space-x-4'
                ),
                # Speaker names stacked on right
                Div(
                    *[
                        A(
                            f"{speaker.name}",
                            href=f'/speakers/{speaker.id}',
                            cls='text-sm text-primary hover:underline'
                        ) for speaker in speakers
                    ],
                    cls='flex flex-col gap-1'
                ),
                cls='flex items-center justify-between gap-4'
            ),
            cls='card-body p-4'
        ),
        Div(
            Span(Icon('clock', solid=False), f"{session.start_time.strftime('%I:%M %p')} - {session.end_time.strftime('%I:%M %p')}", cls='session-detail'),
            Span(Icon('calendar', solid=False), session.start_time.strftime('%b %d, %Y'), cls='session-detail'),
            cls='flex items-center text-xs p-4 justify-between'
        ),
        cls='card session-detail-view'
    )
