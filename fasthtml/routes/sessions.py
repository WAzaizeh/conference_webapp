from db.data import SESSIONS
from components.page import AppContainer
from components.cards import speaker_card
from components.navigation import BackButton
from fasthtml.common import RedirectResponse
from crud.core import get_session, get_speaker
from fasthtml.components import H1, H3, Div, P
from components.timeline import agenda_timeline


def get_session_routes(rt):
    @rt('/agenda')
    def get():
        return AppContainer(
                Div(
                    Div(
                    H1('Agenda', cls='flex-1 text-black font-medium text-center text-base'),
                        cls='flex justify-center items-center p-4',
                    ),
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