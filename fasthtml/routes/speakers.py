from db.data import SPEAKERS
from crud.core import get_speaker
from fasthtml.components import Div, H1
from components.page import AppContainer
from fasthtml.common import RedirectResponse
from components.cards import brief_speaker_card, speaker_page

def get_speaker_routes(rt):
    @rt('/speakers')
    def get():
        return AppContainer(
                Div(
                    Div(
                        H1('Speakers', cls='flex-1 text-black font-medium text-center text-base'),
                        cls='flex justify-center items-center p-4',
                    ),
                *[brief_speaker_card(speaker) for speaker in SPEAKERS],
                cls='blue-background',
                id='page-content',
            ),
            active_button_index=3
        )

    @rt('/speaker/{speaker_id}')
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