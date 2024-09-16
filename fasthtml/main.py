from fasthtml.common import *
from datetime import datetime
from components.icons import Icon
from components.titled import CustomTitled
from crud.core import get_session, get_speaker
from components.timeline import agenda_timeline
from db.data import SESSIONS, SPEAKERS, PRAYER_TIMES
from components.cards import speaker_card, brief_speaker_card, speaker_page, homepage_card, prayer_times_page


plink = Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css')
tlink = (Script(src='https://unpkg.com/tailwindcss-cdn@3.4.3/tailwindcss.js'),)
dlink = [Link(
    rel='stylesheet',
    href='https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css',),
    Script(src='https://cdn.tailwindcss.com'),
]
falink = Link(
    rel="stylesheet",
    href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css", 
    integrity="sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==", 
    crossorigin="anonymous",
    referrerpolicy="no-referrer"
)
mlink = Link(
    rel='stylesheet',
    href='main.css',
    type='text/css',
)
fontLink = Link(
    rel='stylesheet',
    href='https://fonts.cdnfonts.com/css/inter',
)
materialLink = Link(
    rel='stylesheet',
    href='https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200',
)

app = FastHTML(hdrs=[tlink, dlink, falink, mlink, fontLink, materialLink])
rt = app.route

# CUSTOM COMPONENTS
############
def BottomNav():
    return Div(
        # <span class=>
        Button(Span("home", cls="material-symbols-rounded"), 'Home', cls='nav-item', hx_get='/' ,hx_target='#page-content', hx_swap='outerHTML'),
        Button(Span("calendar_today", cls="material-symbols-rounded"), 'Agenda', cls='nav-item', hx_get='/agenda', hx_target='#page-content', hx_swap='outerHTML'),
        Button(Span("mic", cls="material-symbols-rounded"), 'Speakers', cls='nav-item', hx_get='/speakers', hx_target='#page-content', hx_swap='outerHTML'),
        Button(Span("handshake", cls="material-symbols-rounded"), 'Settings', cls='nav-item', hx_get='/settings', hx_target='#page-content', hx_swap='outerHTML'),
        cls='btm-nav'
    )

#############



# stylesheet link routing
@app.route('/{fname:path}.{ext:static}')
def get(fname:str, ext:str): 
    return FileResponse(f'./assets/{fname}.{ext}')

# Routes
@rt('/')
def get():
    return CustomTitled('MAS CYP Conference 2024',
                Div(
                    Div(
                        Html(data_theme="cupcake"),
                        Div (
                            Img(src='banner.png', alt='Conference Banner'),
                            Div(
                                Div(
                                    Img(src='mas-logo-square.png', alt='MAS Logo', cls='logo'),
                                    Div( 
                                        H1('2nd Annual CYP Conference', cls="h3"),
                                        P('Mover and Shakers in Islam: Transformative Traits'),
                                        cls="logo-text-text"  
                                    ),
                                    cls="card card-side logo-text"
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
                                    cls="flex items-center justify-between location-date"
                                ),
                                cls="conference-info"
                            ),
                            Grid(
                                homepage_card(icon_name='about.svg', title='About', card_color="blue", hx_get='/about', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='prayer.svg', title='Prayer Times', card_color="green", hx_get='/prayer-times', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='chat.svg', title='Q&A', card_color="pink", hx_get='/qa', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='survey.svg', title='Feedback Survey', card_color="pink", hx_get='/feedback', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='registration.svg', title='Registration', card_color="blue", hx_get='/', hx_target='#page-content', hx_swap='outerHTML'),
                            cls='grid card-grid'),
                            ),
                        cls='container mx-auto px-0',
                        id='page-content',
                    ),
                    BottomNav(),
                    cls="flex-container"
                )
            )

@rt('/agenda')
def get():
    return Div(
                H1('Agenda', cls="text-2xl font-bold mb-6 text-center"),
                H1('Saturday 12th October', cls="text-xl mb-6 text-center"),
                agenda_timeline(SESSIONS),
                id='page-content',
                cls="blue-background"
            )

@rt('/sessions/{session_id}')
def get(session_id: int):
    session = get_session(session_id)
    if session:
        session_speakers = [get_speaker(speaker_id) for speaker_id in session.speakers]
        return Div(
                    *[speaker_card(session, speaker) for speaker in session_speakers],
                    Div(
                        Span(Icon('clock'), f'{session.start_time.strftime('%H %M')} - {session.end_time.strftime('%H %M')}', cls='session-detail'),
                        Span(Icon('calendar'), session.start_time.strftime('%b %d, %Y'), cls='session-detail'),
                        Span(Icon('map-pin'), 'Room 101', cls='session-detail'),
                        cls='session-info'
                    ),
                    H3('Description'),
                    P(session.description),
                id='page-content',
            )
    return RedirectResponse('/agenda', status_code=303)

@rt('/speakers')
def get():
    return Div(
        *[brief_speaker_card(speaker) for speaker in SPEAKERS],
        id='page-content',
    )

@rt('/speakers/{speaker_id}')
def get(speaker_id: int):
    speaker = get_speaker(speaker_id)
    if speaker:
        return Div(
            speaker_page(speaker),
            id='page-content',
        )
    return RedirectResponse('/speakers', status_code=303)

@rt('/about')
def get():
    return Div(
        H1('About'),
        Img(src='banner.png', alt='Conference Banner'),
        Div(
            H2('Description'),
            P('Join us on a journey to uncover the driving forces behind the movers and shakers of our time, and discover how their transformative traits are reshaping our collective future.'),
            P('We delve into the defining characteristics of a generation at the forefront of change.'),
            P('GAZA Teaching Us: Change is the product of sustained efforts of movers and shakers.'),
            P('Showcasing how young movers and shakers navigate challenges, challenge  norms, and champion progress.'),
            P('A testament to the continuous legacy of youth-driven change and the transformative power of visionary young leadership within the Islamic tradition.'),
            ),
        id='page-content',
        cls='container mx-auto p-8',
    )

@rt('/prayer-times')
def get():
    return Div(
                H1('Prayer Times', cls="text-2xl font-bold mb-6 text-center text-black"),
                H1('Saturday 12th October', cls="text-xl mb-6 text-center text-black"),
                prayer_times_page(PRAYER_TIMES),
                id='page-content',
            )

@rt('/admin_login') 
def get():
    return Div(
                H1('Admin Login'),
                Form(
                    Label(
                        Icon('user', cls='h-4 w-4 opacity-70'),
                        Input(placeholder='Username', type='text', cls='grow'),
                        cls='input input-bordered flex items-center gap-2',
                        ),
                    Label(
                        Icon('key', cls='h-4 w-4 opacity-70'),
                        Input(placeholder='Password', type='password', cls='grow'),
                        cls='input input-bordered flex items-center gap-2',
                        ),
                    Button('Login', cls='btn btn-primary'),
                    
                    cls='form-control',
                    hx_get='/admin_dashboard',
                    hx_target='#page-content',
                    hx_swap='outerHTML',
                ),
                id='page-content',
                # title='MAS CYP Conference 2024'
            )

@rt('/admin_dashboard')
def get():
    return Div('Admin Dashboard Functionalities to go here', id='page-content')

serve()