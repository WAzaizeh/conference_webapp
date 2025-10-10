from fasthtml.components import Div, H1
from components.page import AppContainer
from fasthtml.common import RedirectResponse
from components.cards import brief_speaker_card, speaker_page
from crud.speaker import get_speakers, get_speaker
from db.connection import db_manager
from core.app import rt

@rt('/speakers')
async def get():
    async with db_manager.AsyncSessionLocal() as db_session:
        speakers = await get_speakers(db_session)
    return AppContainer(
            Div(
                Div(
                    H1('Speakers', cls='flex-1 text-black font-medium text-center text-base'),
                    cls='flex justify-center items-center p-4',
                ),
            *[brief_speaker_card(speaker) for speaker in speakers],
            cls='blue-background',
            id='page-content',
        ),
        active_button_index=3
    )

@rt('/speakers/{speaker_id}')
async def get(speaker_id: int):
    async with db_manager.AsyncSessionLocal() as db_session:
        speaker = await get_speaker(db_session, speaker_id)
    if speaker:
        return AppContainer(
            Div(
            speaker_page(speaker),
            id='page-content',
            ),
            active_button_index=3
        )
    return RedirectResponse('/speakers', status_code=303)