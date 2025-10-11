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
def get(sess):
    """Homepage with conditional cards based on user role"""
    user_is_moderator = is_moderator(sess)
    print(f'route User is moderator: {sess.get("admin_auth")}')
    
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
                            H1('2nd Annual CYP Conference', cls='h3'),
                            P('Mover and Shakers in Islam: Transformative Traits'),
                            cls='logo-text-text'  
                        ),
                        cls='card card-side logo-text'
                    ),
                    Div(
                        Span(
                            Img(src='location.png', alt='location icon', cls='hero-icon'),
                            P('5353 Independence Pkwy, Frisco'),
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
        is_moderator=user_is_moderator
    )

@rt('/about')
def get(req, sess):
    bulletPoints = [
        'Join us on a journey to uncover the driving forces behind the movers and shakers of our time, and discover how their transformative traits are reshaping our collective future.', 
        'We delve into the defining characteristics of a generation at the forefront of change.',
        'GAZA Teaching Us: Change is the product of sustained efforts of movers and shakers.',
        'Showcasing how young movers and shakers navigate challenges, challenge  norms, and champion progress.',
        'A testament to the continuous legacy of youth-driven change and the transformative power of visionary young leadership within the Islamic tradition.'
    ]
    return AppContainer(
        Div(
            TopNav('About',),
            Div(alt='Conference banner_2', cls='hero-image'),
            Div(
                H2('Description' , cls='font-bold pb-2'),
                Ul(
                    *[Li(point) for point in bulletPoints],
                    cls='text-sm about-list'
                ),
                cls='p-8',
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
    return RedirectResponse('https://buytickets.at/mascyp/1359890')
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