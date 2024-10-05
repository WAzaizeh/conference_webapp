from db.data import SESSIONS
from components.page import AppContainer
from components.cards import session_speaker_card
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
                active_button_index=2
            )

    @rt('/session/{session_id}')
    def get(session_id: int):
        session = get_session(session_id)
        if session:
            session_speakers = [get_speaker(speaker_id) for speaker_id in session.speakers]
            return AppContainer(
                    Div(
                         Div(
                            BackButton(),
                            H1('Session Details', cls='flex-1 text-black font-medium text-center text-base'),
                            cls='flex justify-center items-center p-4',
                        ),
                        *[session_speaker_card(session, speaker) for speaker in session_speakers],
                        Div (
                            H3('Description', cls='text-sm font-semibold mb-2'),
                            P(session.description, cls='text-sm'),
                            cls='white-background p-6 flex-1'
                        ),
                    id='page-content', cls='blue-background p-0 flex flex-col'
                    )
                )
        return RedirectResponse('/agenda', status_code=303)