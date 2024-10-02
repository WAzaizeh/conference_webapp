from typing import List
from .icon import Icon, BrandIcon
from db.schemas import SpeakerOut, EventOut, PrayerTime, SponsorOut
from components.navigation import BackButton
from fasthtml.components import Div, Span, Figure, Img, H2, H1, P, Button, A, Hr


def homepage_card(icon_name : str, title: str, card_color: str, **kwargs) -> A:
    return A(
                P(title),
                Img(src=icon_name),
                cls='card-panel full-card gray custom-card ' + card_color,
                **kwargs
            )

def speaker_card(session: EventOut, speaker : SpeakerOut) -> Div:
    return Div(
                Figure(Img(src=f'/{speaker.image_url}', alt=speaker.name)),
                Div(
                    H2(session.title),
                    P(f'By {speaker.name}'),
                    Div(
                        Span(Icon('clock'), f"{session.start_time.strftime('%H %M')} - {session.end_time.strftime('%H %M')}", cls='session-detail'),
                        Span(Icon('calendar'), session.start_time.strftime('%b %d, %Y'), cls='session-detail'),
                        Span(Icon('map-pin'), 'Room 101', cls='session-detail'),
                        cls='card-actions'
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
            hx_target='#page-content',
            hx_get=f'/speakers/{speaker.id}',
            hx_swap='outerHTML',
            cls='card speaker-card card-side bg-base-100 shadow-xl',
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
                    src=speaker.image_url,
                    alt=speaker.name,
                    cls='rounded-xl'
                ),
            ),
            Div(
                H2(speaker.name, cls='text-lg mb-2'),
                P(speaker.bio),
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
                    Img(src=sponsor.image_url, alt=sponsor.name),
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
                    src=sponsor.image_url,
                    alt=sponsor.name,
                    cls='rounded h-full'
                ),
                cls='bg-aliceblue'
            ),
            Div(
                H2(sponsor.name, cls='text-lg mb-2'),
                P(sponsor.description),
                cls='sponsor-detail-body flex flex-col justify-center items-center p-6'
            ),
            Div(
                Span('Links and Socials', cls='sponsor-social-title'),
                Div(
                    A(Icon('globe'), href=sponsor.website),
                    A(BrandIcon('facebook-f'), href=sponsor.facebook),
                    A(BrandIcon('twitter'), href=sponsor.twitter),
                    A(BrandIcon('instagram'), href=sponsor.instagram),
                    cls='sponsor-social-links flex justify-around items-center'
                    ),
                cls='sponsor-social-container flex flex-col justify-around items-center p-4'
            ),
            cls='sponsor-detail-view blue-background'
        )