from fasthtml.components import Div
from components.page import AppContainer
from fasthtml.common import RedirectResponse
from components.cards import brief_speaker_card, speaker_page
from crud.speaker import get_speakers, get_speaker
from db.connection import db_manager
from core.app import rt
from utils.auth import is_moderator
from components.navigation import TopNav

@rt('/speakers')
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db_session:
        speakers = await get_speakers(db_session)
    return AppContainer(
            Div(
                TopNav('Speakers'),
            *[brief_speaker_card(speaker) for speaker in speakers],
            cls='blue-background',
            id='page-content',
        ),
        active_button_index=3,
        is_moderator=is_moderator(sess)
    )

@rt('/speakers/{speaker_id}')
async def get(req, sess, speaker_id: int):
    async with db_manager.AsyncSessionLocal() as db_session:
        speaker = await get_speaker(db_session, speaker_id)
    if speaker:
        return AppContainer(
            Div(
                TopNav('Speaker Details', cls='blue-background'),
                speaker_page(speaker),
                id='page-content',
            ),
            active_button_index=3,
            is_moderator=is_moderator(sess)
        )
    return RedirectResponse('/speakers', status_code=303)