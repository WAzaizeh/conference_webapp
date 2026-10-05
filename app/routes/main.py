from components.navigation import TopNav
from components.page import AppContainer
from components.cards import homepage_card
from components.coming_soon import ComingSoon
from components.home import HimHerBanner, HomeHeader
from fasthtml.common import RedirectResponse
from components.cards import prayer_times_page
from db.connection import db_manager
from crud.prayer_time import get_prayer_times
from fasthtml.components import H1, H2, Div, Img, P, Span, Grid, A, Ul, Li, Title
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
            homepage_card(icon_name='edit-agenda.svg', title='Edit Agenda', card_color='blue', href='/admin/agenda', cls='full-card', bold_style=True),
        ])
    else:
        cards.extend([
            homepage_card(icon_name='chat.svg', title='Q&A', card_color='pink', href='/qa', cls='full-card'),
            homepage_card(icon_name='survey.svg', title='Feedback Survey', card_color='pink', href='/feedback', cls='full-card'),
        ])
    
    return AppContainer(
        Div(
            Div(
                HomeHeader(),
                Div(
                    *cards,  # Spread conditional cards
                    homepage_card(icon_name='registration.svg', title='Registration', card_color='blue', href='/registration', cls='home-register'),
                    cls='home-grid',
                ),
                cls='home-inner with-auth-badge' if user_is_moderator else 'home-inner',
            ),
            cls='home-26',
            id='page-content',
        ),
        active_button_index=1,
        is_moderator=user_is_moderator,
        request=req  # Pass request to show moderator login on select pages
    )

@rt('/coming-soon')
def get():
    return Title('CYP conference 2026 - coming soon'), ComingSoon()

@rt('/about')
def get(req, sess):
    paragraphs = [
        'MAS Dallas College & Young Professionals (CYP) presents the 4th Annual CYP Conference — Him & Her: Building Success at Every Stage — on Saturday, October 24, 2026 (11 AM – 8 PM) at GEM Academy & Facility in Plano.',
        'Redefine masculinity and womanhood through an Islamic lens. The conference introduces Allah’s complementary vision for men and women — not as competing paths, but as two halves of one shared purpose — and empowers young Muslim men and women to build success at every stage, from college and career to marriage and parenthood, through faith-rooted guidance, practical tools, and dedicated tracks that turn individual growth into resilient families and a thriving community.',
        'Through keynotes, interactive workshops, small-group discussions, and parallel sessions, we will explore:',
    ]
    bulletPoints = [
        'Masculinity Track: Leadership through responsibility — protecting, providing, emotional maturity, and spiritual leadership as a son, brother, husband, father, and community leader.',
        'Womanhood Track: Strength through faith — confident identity, nurturing with purpose, balancing aspirations, and leadership as a daughter, sister, wife, mother, and community builder.',
        'The Art of Good Relations: Marriage as real life, not reel life, and emotional intelligence for healthy relationships with family, friends, and beyond.',
        'The Ripple Effect: The parenting challenges no one warns you about, and building a legacy that lives beyond your lifetime.',
    ]
    return AppContainer(
        Div(
            TopNav('About',),
            HimHerBanner(),
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
                H1('Saturday · October 24, 2026', cls='page-eyebrow pt-2'),
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