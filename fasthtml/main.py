from fasthtml.common import *
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

app, rt = fast_app()

# Models
class Session(BaseModel):
    id: Optional[int] = None
    title: str
    description: str
    date: datetime
    start_time: str
    end_time: str
    speaker: Optional[ List[int] ]

class Speaker(BaseModel):
    id: Optional[int] = None
    name: str
    bio: str
    image_url: str
    sessions: Optional[ List[int] ]

# In-memory storage
sessions = []
speakers = []

# Helper functions
def get_session(session_id: int):
    return next((session for session in sessions if session.id == session_id), None)

def get_speaker(speaker_id: int):
    return next((speaker for speaker in speakers if speaker.id == speaker_id), None)

# Routes
@rt("/")
def get():
    return Titled("MAS CYP Conference 2024",
        Div(
            Img(src="/assets/banner.png", alt="Conference Banner"),
            H1("MAS CYP Conference 2024"),
            P("1818 Blake Dr, Richardson", cls="location"),
            P("Oct 10, 2024", cls="date"),
            Grid(
                Card(Icon("info"), "About", href="/about", cls="menu-item"),
                Card(Icon("clock"), "Prayer Times", href="/prayer-times", cls="menu-item"),
                Card(Icon("question"), "FAQ", href="/faq", cls="menu-item"),
                Card(Icon("message"), "Q&A", href="/qa", cls="menu-item"),
                Card(Icon("clipboard"), "Feedback Survey", href="/survey", cls="menu-item"),
                Card(Icon("heart"), "Sponsors", href="/sponsors", cls="menu-item"),
            ),
            BottomNav(),
            cls="container"
        ),
        Style("""
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f0f0f0; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            h1 { text-align: center; margin-bottom: 10px; }
            .location, .date { text-align: center; margin: 5px 0; color: #666; }
            .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 20px; }
            .menu-item { background-color: #fff; padding: 20px; border-radius: 10px; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .menu-item i { font-size: 24px; margin-bottom: 10px; }
        """)
    )

@rt("/agenda")
def get():
    return Titled("Agenda",
        Div(
            H1("Agenda"),
            Div(
                Button("9 Oct", cls="date-btn"),
                Button("10 Oct", cls="date-btn active"),
                Button("11 Oct", cls="date-btn"),
                cls="date-selector"
            ),
            Ul(*[Li(
                Div(f"{session.start_time} - {session.end_time}", cls="time"),
                H3(session.title),
                Div(f"By {session.speaker}", cls="speaker"),
                A("View Details", href=f"/sessions/{session.id}", cls="details-link"),
                cls="session-item"
            ) for session in sessions], cls="session-list"),
            BottomNav(),
            cls="container"
        ),
        Style("""
            .date-selector { display: flex; justify-content: space-between; margin-bottom: 20px; }
            .date-btn { padding: 10px; border: none; background-color: #f0f0f0; border-radius: 5px; }
            .date-btn.active { background-color: #007bff; color: white; }
            .session-list { list-style-type: none; padding: 0; }
            .session-item { background-color: white; margin-bottom: 15px; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .time { color: #007bff; font-weight: bold; }
            .speaker { color: #666; margin-top: 5px; }
            .details-link { display: inline-block; margin-top: 10px; color: #007bff; text-decoration: none; }
        """)
    )

@rt("/sessions/{session_id}")
def get(session_id: int):
    session = get_session(session_id)
    if session:
        speaker = get_speaker(session.speaker)
        return Titled(session.title,
            Div(
                Div(
                    Img(src=speaker.image_url, alt=speaker.name, cls="speaker-img"),
                    H2(session.title),
                    P(f"By {speaker.name}", cls="speaker-name"),
                    cls="session-header"
                ),
                Div(
                    Div(Icon("clock"), f"{session.start_time} - {session.end_time}", cls="session-detail"),
                    Div(Icon("calendar"), session.date.strftime("%b %d, %Y"), cls="session-detail"),
                    Div(Icon("map-pin"), "Room 101", cls="session-detail"),
                    cls="session-info"
                ),
                H3("Description"),
                P(session.description),
                H3("Speaker"),
                Div(
                    Img(src=speaker.image_url, alt=speaker.name, cls="speaker-img-small"),
                    Div(
                        H4(speaker.name),
                        P(speaker.bio),
                        cls="speaker-info"
                    ),
                    cls="speaker-container"
                ),
                BottomNav(),
                cls="container"
            ),
            Style("""
                .session-header { text-align: center; margin-bottom: 20px; }
                .speaker-img { width: 100px; height: 100px; border-radius: 50%; object-fit: cover; }
                .speaker-name { color: #666; }
                .session-info { background-color: #f0f0f0; padding: 15px; border-radius: 10px; margin-bottom: 20px; }
                .session-detail { display: flex; align-items: center; margin-bottom: 10px; }
                .session-detail i { margin-right: 10px; color: #007bff; }
                .speaker-container { display: flex; align-items: start; }
                .speaker-img-small { width: 50px; height: 50px; border-radius: 50%; object-fit: cover; margin-right: 15px; }
                .speaker-info { flex: 1; }
            """)
        )
    return RedirectResponse("/agenda", status_code=303)

@rt("/speakers")
def get():
    return Titled("Speakers",
        Div(
            H1("Speakers"),
            Ul(*[Li(
                Img(src=speaker.image_url, alt=speaker.name, cls="speaker-img"),
                Div(
                    H3(speaker.name),
                    A("View Profile", href=f"/speakers/{speaker.id}", cls="profile-link"),
                    cls="speaker-info"
                ),
                cls="speaker-item"
            ) for speaker in speakers], cls="speaker-list"),
            BottomNav(),
            cls="container"
        ),
        Style("""
            .speaker-list { list-style-type: none; padding: 0; }
            .speaker-item { display: flex; align-items: center; background-color: white; margin-bottom: 15px; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            .speaker-img { width: 60px; height: 60px; border-radius: 50%; object-fit: cover; margin-right: 15px; }
            .speaker-info { flex: 1; }
            .profile-link { color: #007bff; text-decoration: none; }
        """)
    )

@rt("/speakers/{speaker_id}")
def get(speaker_id: int):
    speaker = get_speaker(speaker_id)
    if speaker:
        return Titled(f"{speaker.name} - Profile",
            Div(
                Img(src=speaker.image_url, alt=speaker.name, cls="speaker-img-large"),
                H2(speaker.name),
                P(speaker.bio),
                BottomNav(),
                cls="container"
            ),
            Style("""
                .speaker-img-large { width: 150px; height: 150px; border-radius: 50%; object-fit: cover; margin: 0 auto 20px; display: block; }
            """)
        )
    return RedirectResponse("/speakers", status_code=303)

def BottomNav():
    return Div(
        A(Icon("home"), "Home", href="/", cls="nav-item"),
        A(Icon("calendar"), "Agenda", href="/agenda", cls="nav-item"),
        A(Icon("users"), "Speakers", href="/speakers", cls="nav-item"),
        A(Icon("settings"), "Settings", href="/settings", cls="nav-item"),
        cls="bottom-nav"
    )

def Icon(name):
    return I(cls=f"fas fa-{name}")

serve()