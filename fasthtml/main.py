from fasthtml.common import *
from dotenv import load_dotenv
from components.icon import Icon
from components.page import AppContainer
from components.navigation import BackButton
from crud.core import get_session, get_speaker
from components.timeline import agenda_timeline
from db.data import SESSIONS, SPEAKERS, PRAYER_TIMES
from components.cards import (
    speaker_card,
    brief_speaker_card,
    speaker_page,
    homepage_card,
    prayer_times_page
)


plink = Link(rel='stylesheet', href='https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css')
tlink = (Script(src='https://unpkg.com/tailwindcss-cdn@3.4.3/tailwindcss.js'),)
dlink = [Link(
    rel='stylesheet',
    href='https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css',),
    Script(src='https://cdn.tailwindcss.com'),
]
falink = Link(
    rel='stylesheet',
    href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.6.0/css/all.min.css', 
    integrity='sha512-Kc323vGBEqzTmouAECnVceyQqyqdsSiqLQISBL29aUW4U/M7pSPA/gEUZQqv1cwx4OnYxTxve5UMg5GT6L4JJg==', 
    crossorigin='anonymous',
    referrerpolicy='no-referrer'
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
back_button_js = Script('function goBack() { window.history.back(); }')

app = FastHTML(hdrs=[tlink, dlink, falink, mlink, fontLink, materialLink, back_button_js])
rt = app.route

# stylesheet link routing
@app.route('/{fname:path}.{ext:static}')
def get(fname:str, ext:str): 
    return FileResponse(f'./assets/{fname}.{ext}')

# Routes
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

@rt('/agenda')
def get():
    return AppContainer(
            Div(
                H1('Agenda', cls='text-gray-800 text-center p-8'),
                H1('Saturday 12th October', cls='text-center'),
                agenda_timeline(SESSIONS),
                id='page-content',
                cls='blue-background'
            ),
        )

@rt('/sessions/{session_id}')
def get(session_id: int):
    session = get_session(session_id)
    if session:
        session_speakers = [get_speaker(speaker_id) for speaker_id in session.speakers]
        return AppContainer(
                Div(
                    Div(
                    BackButton(),
                    H1('Session Details', cls='text-black'),
                    cls='flex justify-center items-center p-4',
                    ),
                    *[speaker_card(session, speaker) for speaker in session_speakers],
                    H3('Description'),
                    P(session.description),
                id='page-content',
                )
            )
    return RedirectResponse('/agenda', status_code=303)

@rt('/speakers')
def get():
    return AppContainer(
            Div(
            H1('Speakers', cls='text-black text-center p-4'),
            *[brief_speaker_card(speaker) for speaker in SPEAKERS],
            cls='blue-background',
            id='page-content',
        ),
    )

@rt('/speakers/{speaker_id}')
def get(speaker_id: int):
    speaker = get_speaker(speaker_id)
    if speaker:
        return AppContainer(
            Div(
            speaker_page(speaker),
            id='page-content',
            )
        )
    return RedirectResponse('/speakers', status_code=303)

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
                    H1('Prayer Times', cls='text-black text-center'),
                    cls='flex justify-center items-center p-4',
                    ),
                H1('Saturday 12th October', cls='text-primary text-center p-4'),
                prayer_times_page(PRAYER_TIMES),
                id='page-content',
                cls='blue-background'
                )
            )

@rt('/sponsors')
def get():
    return AppContainer(
            Div(
                H1('Sponsors', cls='text-black text-center p-4'),
                H2('Coming soon...'),
                id='page-content',
                cls='blue-background'
                )
            )

@rt('/qa')
def get():
    return AppContainer(
            Div(
                H1('Sponsors', cls='text-black text-center p-4'),
                H2('Coming soon...'),
                id='page-content',
                cls='blue-background'
                )
            )

@rt('/feedback-survey')
def get():
    return AppContainer(
            Div(
                H1('Sponsors', cls='text-black text-center p-4'),
                H2('Coming soon...'),
                id='page-content',
                cls='blue-background'
                )
            )

@rt('/registration')
def get():
    return AppContainer(
            Div(
                H1('Sponsors', cls='text-black text-center p-4'),
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


########## Admin Routes ##########
@rt('/settings')
def get_settings():
    # Buttons for settings options
    general_btn = Button('General Settings', disabled=True, cls='btn btn-block btn-glass')
    privacy_btn = Button('Privacy', disabled=True, cls='btn btn-block btn-glass')
    notifications_btn = Button('Notifications', disabled=True, cls='btn btn-block btn-glass')
    admin_access_btn = Button(
                            'Admin Access',
                            hx_get='/admin_login',
                            hx_target='#page-content',
                            hx_swap='outerHTML',
                            id='admin-access-btn',
                            cls='btn btn-block btn-glass'
                            )

    # Layout for the settings page
    content = [
        H1('Settings', cls='text-2xl font-bold mb-6 text-center'),
        general_btn,
        privacy_btn,
        notifications_btn,
        admin_access_btn
    ]
    return AppContainer(
                Div(
                    *content,
                    id='page-content',
                    cls='flex flex-col items-center justify-evenly blue-background'
                    )
                )

@rt('/admin_login') 
def get():
    return AppContainer(
            Div(
                H1('Admin Login', cls='text-2xl font-bold mb-6 text-center'),
                Form(
                    Label(
                        Icon('user', cls='h-4 w-4 opacity-70'),
                        Input(placeholder='Username', name='username', type='text', cls='grow'),
                        cls='input input-bordered flex items-center gap-2',
                        ),
                    Label(
                        Icon('key', cls='h-4 w-4 opacity-70'),
                        Input(placeholder='Password', name='password', type='password', cls='grow'),
                        cls='input input-bordered flex items-center gap-2',
                        ),
                    Button('Login', cls='btn btn-primary'),
                    
                    cls='flex flex-col items-center justify-evenly h-35-vh',
                    hx_post='/admin_login',
                ),
                id='page-content',
                cls='flex flex-col items-center justify-start blue-background'
            )
        )

# Handling admin login POST request
load_dotenv()
@dataclass
class AdminLogin: username: str; password: str

@rt('/admin_login')
def post(admin: AdminLogin, sess):
    # Get admin credentials from environment variables
    ADMIN_USERNAME = os.getenv('ADMIN_USERNAME')
    ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

    if not admin.username or not admin.password:
        return RedirectResponse('/admin-login', status_code=303)
    
    # Compare preset credentials with input
    if compare_digest(admin.username, ADMIN_USERNAME) and compare_digest(admin.password, ADMIN_PASSWORD):
        sess['admin_auth'] = True
        return RedirectResponse('/admin_dashboard', status_code=303)
    else:
        return RedirectResponse('/admin_login', status_code=303)

@rt('/admin_dashboard')
def get(sess):
    # Ensure the user is authenticated as admin
    if not sess.get('admin_auth', False):
        return RedirectResponse('/admin-login', status_code=303)

    # Create buttons for each edit option
    edit_speakers_btn = Button('Edit Speakers', hx_get='/edit-speakers', id='edit-speakers-btn', cls='btn btn-block btn-glass')
    edit_events_btn = Button('Edit Events', hx_get='/edit-events', id='edit-events-btn', cls='btn btn-block btn-glass')
    edit_prayer_times_btn = Button('Edit Prayer Times', hx_get='/edit-prayer-times', id='edit-prayer-times-btn', cls='btn btn-block btn-glass')
    edit_sponsors_btn = Button('Edit Sponsors', hx_get='/edit-sponsors', id='edit-sponsors-btn', cls='btn btn-block btn-glass')
    edit_registration_link_btn = Button('Edit Registration Link', hx_get='/edit-registration-link', id='edit-registration-link-btn', cls='btn btn-block btn-glass')
    edit_feedback_survey_link_btn = Button('Edit Feedback Survey Link', hx_get='/edit-feedback-survey', id='edit-feedback-survey-btn', cls='btn btn-block btn-glass')

    # Layout for the admin dashboard
    content = [
        H1('Admin Dashboard', cls='text-2xl font-bold mb-6 text-center'),
        edit_speakers_btn,
        edit_events_btn,
        edit_prayer_times_btn,
        edit_sponsors_btn,
        edit_registration_link_btn,
        edit_feedback_survey_link_btn
    ]

    return AppContainer(
            Div(
            *content,
            id='page-content',
            cls='flex flex-col items-center justify-evenly blue-background h-70-vh'
            )
        )
######### End Admin Routes #########


# Run the FastHTML app with Uvicorn, using the SSL certificate and private key
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 8000)),
    )