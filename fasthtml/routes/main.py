from db.data import PRAYER_TIMES
from components.page import AppContainer
from components.cards import homepage_card
from components.navigation import BackButton
from components.cards import prayer_times_page
from fasthtml.components import H1, H2, Div, Img, P, Span, Grid, A

def get_main_routes(rt):
    @rt('/')
    def get():
        return AppContainer(
                    Div(
                        Div (
                            Img(src='banner.png', alt='Conference Banner'),
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
                                        P('1515 Blake Dr, Richardson'),
                                        cls='flex items-center justify-between',
                                    ),
                                    Span(
                                        Img(src='calendar.png', alt='calendar icon', cls='hero-icon'),
                                        P('Oct 12, 2024'),
                                        cls='flex items-center justify-between',
                                    ),
                                    cls='flex items-center justify-between location-date'
                                ),
                                cls='conference-info'
                            ),
                            Grid(
                                homepage_card(icon_name='about.svg', title='About', card_color='blue', href='/about'),
                                homepage_card(icon_name='prayer.svg', title='Prayer Times', card_color='green', href='/prayer-times'),
                                homepage_card(icon_name='chat.svg', title='Q&A', card_color='pink', href='/qa'),
                                homepage_card(icon_name='survey.svg', title='Feedback Survey', card_color='pink', href='/feedback-survey'),
                                homepage_card(icon_name='registration.svg', title='Registration', card_color='blue', href='/registration'),
                            cls='grid card-grid'),
                            ),
                        cls='container mx-auto px-0',
                        id='page-content',
                    ),
                )
    
    @rt('/about')
    def get():
        return AppContainer(
            Div(
                Div(
                    BackButton(),
                    H1('About', cls='text-black'),
                    cls='flex justify-center items-center p-4',
                    ),
                Img(src='banner.png', alt='Conference Banner'),
                Div(
                    H2('Description' , cls='font-bold pb-2'),
                    P('Join us on a journey to uncover the driving forces behind the movers and shakers of our time, and discover how their transformative traits are reshaping our collective future.'),
                    P('We delve into the defining characteristics of a generation at the forefront of change.'),
                    P('GAZA Teaching Us: Change is the product of sustained efforts of movers and shakers.'),
                    P('Showcasing how young movers and shakers navigate challenges, challenge  norms, and champion progress.'),
                    P('A testament to the continuous legacy of youth-driven change and the transformative power of visionary young leadership within the Islamic tradition.'),
                    cls='p-8',
                    ),
                id='page-content',
                cls='container',
            )
        )

    @rt('/prayer-times')
    def get():
        return AppContainer(
                Div(
                    Div(
                        BackButton(),
                        H1('Prayer Times', cls='flex-1 text-black font-medium text-center text-base'),
                        cls='flex justify-center items-center p-4',
                        ),
                    H1('Saturday 12th October', cls='text-black font-medium text-center text-sm'),
                    prayer_times_page(PRAYER_TIMES),
                    id='page-content',
                    cls='white-background'
                    )
                )
    
    @rt('/qa')
    def get():
        return AppContainer(
                Div(
                    H1('Q&A', cls='text-black text-center p-4'),
                    H2('Coming soon...'),
                    id='page-content',
                    cls='blue-background'
                    )
                )

    @rt('/feedback-survey')
    def get():
        return AppContainer(
                Div(
                    H1('Feedback Survey', cls='text-black text-center p-4'),
                    H2('Coming soon...'),
                    id='page-content',
                    cls='blue-background'
                    )
                )

    @rt('/registration')
    def get():
        return AppContainer(
                Div(
                    H1('Registration', cls='text-black text-center p-4'),
                    H2('Get your tickets here!', cls='text-center text-primary p-4'),
                    A(
                        'Buy tickets',
                        href='https://buytickets.at/mascyp/1359890',
                        title='Buy tickets for Muslim American Society - CYP',  
                        cls='btn bg-primary text-white flex justify-center',
                    ),
                    id='page-content',
                    cls='blue-background flex flex-col items-center justify-start'
                    )
                )