from components.navigation import TopNav
from components.page import AppContainer
from components.cards import homepage_card
from fasthtml.common import RedirectResponse
from components.cards import prayer_times_page
from db.connection import db_manager
from crud.prayer_time import get_prayer_times
from fasthtml.components import H1, H2, Div, Img, P, Span, Grid, A, Ul, Li
from core.app import rt
from utils.auth import is_moderator

@rt('/')
def get(req, sess):
    """Homepage with conditional cards based on user role"""
    user_is_moderator = is_moderator(sess)
    
    # Build card list based on user type
    cards = [
        homepage_card(icon_name='about.svg', title='About', card_color='blue', href='/about', cls='full-card'),
        homepage_card(icon_name='prayer.svg', title='Prayer Times', card_color='green', href='/prayer-times', cls='full-card'),
    ]
    
    # Add role-specific cards
    if user_is_moderator:
        cards.extend([
            homepage_card(icon_name='chat.svg', title='Q&A (Guest)', card_color='pink', href='/qa', cls='full-card'),
            homepage_card(icon_name='chat.svg', title='Q&A (Moderator)', card_color='pink', href='/qa/moderator', cls='full-card', bold_style=True),
            homepage_card(icon_name='survey.svg', title='Feedback (Guest)', card_color='pink', href='/feedback', cls='full-card'),
            homepage_card(icon_name='survey.svg', title='Feedback (Moderator)', card_color='pink', href='/feedback/moderator', cls='full-card', bold_style=True),
        ])
    else:
        cards.extend([
            homepage_card(icon_name='chat.svg', title='Q&A', card_color='pink', href='/qa', cls='full-card'),
            homepage_card(icon_name='survey.svg', title='Feedback Survey', card_color='pink', href='/feedback', cls='full-card'),
        ])
    
    return AppContainer(
        Div(
            Div(
                Div(alt='Conference banner_2', cls='hero-image cropped'),
                Div(
                    Div(
                        Img(src='mas-logo-square.png', alt='MAS Logo', cls='logo'),
                        Div( 
                            H1('3rd Annual CYP Conference', cls='h3'),
                            P('Weathering the Storm: Faith, Resilience & Action'),
                            cls='logo-text-text'  
                        ),
                        cls='card card-side logo-text'
                    ),
                    Div(
                        Span(
                            A(
                                Img(src='location.png', alt='location icon', cls='hero-icon'),
                                P('Crystal Banquet, Plano'),
                                href='https://www.google.com/maps/search/?api=1&query=Crystal+Banquet+Hall+Plano+TX',
                                target='_blank',
                                cls='flex items-center justify-between hover:text-primary transition-colors',
                            ),
                            cls='flex items-center justify-between',
                        ),
                        Span(
                            Img(src='calendar.png', alt='calendar icon', cls='hero-icon'),
                            P('Oct 18, 2025'),
                            cls='flex items-center justify-between',
                        ),
                        cls='flex items-center justify-between location-date'
                    ),
                    cls='conference-info'
                ),
                Grid(
                    *cards,  # Spread conditional cards
                    cls='grid card-grid mb-7 home-page-content'
                ),
                homepage_card(
                    icon_name='registration.svg', 
                    title='Registration', 
                    card_color='blue', 
                    href='/registration',
                    cls='mx-6 mt-4'
                ),
                cls='mb-8',
            ),
            cls='container mx-auto',
            id='page-content',
        ),
        active_button_index=1,
        is_moderator=user_is_moderator,
        request=req  # Pass request to show moderator login on select pages
    )

@rt('/about')
def get(req, sess):
    paragraphs = [
        'In the wake of the recent ICE abductions targeting Muslim leaders in Dallas, our community once again finds itself in the heart of a storm — a test of faith, unity, and conviction. This comes while the Muslim Ummah continues to reel from the pain and anguish of two long years of genocide in Gaza — a wound that weighs heavily on every conscious heart.',
        'In response to these realities, MAS Dallas and its College & Young Professionals (CYP) program have chosen to change the original theme of the 3rd Annual CYP Conference (October 18, 2025) to “Weathering the Storm: Faith, Resilience & Action.” This new direction calls not only CYP members, but our entire community, to meet this defining moment with clarity, courage, and divine purpose.',
        'Storms are not unfamiliar to those who strive for truth. Throughout history, believers have faced waves of trials — each carrying divine wisdom within the ongoing “push and pull” between truth and falsehood. This conference invites college students and young professionals & the whole community  to reflect deeply on why we face such storms, how we remain steadfast through them, and what it means to emerge from them stronger and more united.',
        'Through inspiring talks, interactive discussion circles, and a powerful panel on Faith, Resilience, and Collective Action, we will explore:',
    ]
    bulletPoints = [
        'Faith: Grounding the heart in certainty of Allah’s plan — so that the losses of this world never shake the believer’s hope in the eternal reward.',
        'Resilience: Preparing before the storm hits — drawing lessons from those who stood firm with courage, patience, and Tawakkul (trust in Allah).',
        'Action: Moving beyond reaction — embodying goodness, organizing collectively, and serving as instruments of Allah’s mercy and justice on earth.',
    ]
    return AppContainer(
        Div(
            TopNav('About',),
            Div(alt='Conference banner_2', cls='hero-image'),
            Div(
                H2('Description' , cls='font-bold pb-2'),
                P(*paragraphs, cls='text-sm mb-4'),
                Ul(
                    *[Li(point) for point in bulletPoints],
                    cls='text-sm about-list'
                ),
                cls='p-8 pt-0',
                ),
            id='page-content',
        ),
        active_button_index=1,
        is_moderator=is_moderator(sess)
    )

@rt('/prayer-times')
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db_session:
        prayer_times = await get_prayer_times(db_session)
    return AppContainer(
            Div(
                TopNav('Prayer Times'),
                H1('Saturday 18th October', cls='text-black font-medium text-center text-sm'),
                prayer_times_page(prayer_times),
                id='page-content',
                cls='white-background'
                ),
            active_button_index=1,
            is_moderator=is_moderator(sess)
            )

# @rt('/qa')
# def get():
#     return RedirectResponse('https://app.sli.do/event/cRE7CEK9iN7cR8Rg2UFZMk')
#     # return AppContainer(
#     #         Div(
#     #             TopNav('Q&A'),
#     #             H2('Coming soon...'),
#     #             id='page-content',
#     #             cls='blue-background'
#     #             )
#     #         )

# @rt('/feedback-survey')
# def get():
#     return AppContainer(
#             Div(
#                 TopNav('Feedback Survey'),
#                 H2('Coming soon...'),
#                 id='page-content',
#                 cls='blue-background'
#                 ),
#             active_button_index=1
#             )

@rt('/registration')
def get(resq, sess):
    return RedirectResponse('https://www.tickettailor.com/events/mascyp/1841794')
    # return AppContainer(
    #         Div(
    #             TopNav('Registration'),
    #             Div(
    #                 H2('Get your tickets here!', cls='text-center text-primary p-4'),
    #                 A(
    #                     'Buy tickets',
    #                     href='https://buytickets.at/mascyp/1359890',
    #                     title='Buy tickets for Muslim American Society - CYP',  
    #                     cls='btn bg-primary text-white flex justify-center',
    #                 ),
    #                 cls='flex flex-col justify-center items-center',
    #             ),
    #             id='page-content',
    #             cls='blue-background flex flex-col'
    #             )
    #         )