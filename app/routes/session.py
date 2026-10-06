from components.page import AppContainer
from components.cards import session_speaker_card
from components.navigation import TopNav
from fasthtml.common import RedirectResponse
from crud.event import get_event, get_events
from crud.speaker import get_speaker
from fasthtml.components import A, H1, H3, Div, P
from components.icon import Icon
from components.timeline import agenda_timeline, agenda_timeline_2, TagFilter
from utils.tags import filter_tags
from db.connection import db_manager
from core.app import rt
from utils.auth import is_moderator

@rt('/agenda')
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db_session:
        events = await get_events(db_session)
        # sort by start_time
        events.sort(key=lambda e: e.start_time)
    return AppContainer(
            Div(
                TopNav('Agenda'),
                H1('4th Annual CYP Conference', cls='page-eyebrow'),
                H1('Saturday · October 24, 2026', cls='page-eyebrow opacity-70'),
                A(Icon('pen', cls='mr-1'), 'Edit Agenda', href='/admin/agenda', cls='btn btn-sm btn-primary mx-auto mt-4 flex w-fit') if is_moderator(sess) else None,
                TagFilter(filter_tags(events)),
                agenda_timeline(events),
                id='page-content',
                cls='blue-background'
            ),
            active_button_index=2,
            is_moderator=is_moderator(sess),
        )

@rt('/agenda_2')
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db_session:
        sessions = await get_events(db_session)
    return AppContainer(
            Div(
                Div(
                H1('Agenda', cls='flex-1 text-black font-medium text-center text-base'),
                    cls='flex justify-center items-center p-4',
                ),
                H1('Testing progress timeline', cls='text-center font-medium text-base'),
                agenda_timeline_2(sessions),
                id='page-content',
                cls='blue-background'
            ),
            active_button_index=2,
            is_moderator=is_moderator(sess),
        )

@rt('/session/{session_id}')
async def get(req, sess, session_id: int):
    async with db_manager.AsyncSessionLocal() as db_session:
        session = await get_event(db_session, session_id)
    if session:
        return AppContainer(
                Div(
                    TopNav('Session Details'),
                    Div (
                        session_speaker_card(session, getattr(session, 'speakers', [])),
                        Div (
                            H3('Description', cls='text-base font-semibold mb-2'),
                            P(session.description, cls='text-base whitespace-pre-line'),
                            cls='white-background p-6 flex-1'
                        ),
                        cls='flex flex-col flex-1'
                    ),
                id='page-content', cls='blue-background p-0 flex flex-col'
                ),
                active_button_index=2,
                is_moderator=is_moderator(sess)
            )
    return RedirectResponse('/agenda', status_code=303)