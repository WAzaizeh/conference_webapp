from fasthtml.common import *
from datetime import datetime
from components.icons import Icon
from db.data import SESSIONS, SPEAKERS
from components.titled import CustomTitled
from crud.core import get_session, get_speaker
from components.timeline import agenda_timeline
from db.schemas import EventOut, EVENT_CATEGORY, SpeakerOut
from components.cards import speaker_card, brief_speaker_card, speaker_page, homepage_card


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

app = FastHTML(hdrs=[tlink, dlink, falink, mlink])
rt = app.route

# CUSTOM COMPONENTS
############
def BottomNav():
    return Div(
        Button(Icon('home'), 'Home', cls='nav-item', hx_get='/' ,hx_target='#page-content', hx_swap='outerHTML'),
        Button(Icon('calendar'), 'Agenda', cls='nav-item', hx_get='/agenda', hx_target='#page-content', hx_swap='outerHTML'),
        Button(Icon('users'), 'Speakers', cls='nav-item', hx_get='/speakers', hx_target='#page-content', hx_swap='outerHTML'),
        Button(Icon('gear'), 'Settings', cls='nav-item', hx_get='/settings', hx_target='#page-content', hx_swap='outerHTML'),
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
                        Html(data_theme="cupcake", cls="blue-background"),
                        Div(
                            Img(src='banner.png', alt='Conference Banner'),
                            H1('MAS CYP Conference 2024'),
                            P('1818 Blake Dr, Richardson', cls='location'),
                            P('Oct 10, 2024', cls='date'),
                            Grid(
                                homepage_card(icon_name='info', title='About', hx_get='/about', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='clock', title='Prayer Times', hx_get='/prayer-times', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='question', title='FAQ', hx_get='/faq', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='message', title='Q&A', hx_get='/qa', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='clipboard', title='Feedback Survey', hx_get='/feedback', hx_target='#page-content', hx_swap='outerHTML'),
                                homepage_card(icon_name='heart', title='Sponsors', hx_get='/sponsors', hx_target='#page-content', hx_swap='outerHTML'),
                            cls='grid card-grid'),
                            ),
                        cls='container mx-auto px-4',
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
                Div(
                    A('9 Oct', cls='tab', role="tab"),
                    A('10 Oct', cls='tab tab-active', role="tab"),
                    A('11 Oct', cls='tab', role="tab"),
                    cls='tabs tabs-bordered',
                    role="tablist"
                ),
                agenda_timeline(SESSIONS),
                id='page-content',
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
        H1('About Us'),
        P('Join us on a journey to uncover the driving forces behind the movers and shakers of our time, and discover how their transformative traits are reshaping our collective future.'),
        P('We delve into the defining characteristics of a generation at the forefront of change.'),
        P('GAZA Teaching Us: Change is the product of sustained efforts of movers and shakers.'),
        P('Showcasing how young movers and shakers navigate challenges, challenge  norms, and champion progress.'),
        P('A testament to the continuous legacy of youth-driven change and the transformative power of visionary young leadership within the Islamic tradition.'),
        id='page-content',
    )

@rt('/prayer-times')
def get():
    return Div(
        H1('Prayer Times'),
        P('This is a conference'),
        id='page-content',
    )

serve()