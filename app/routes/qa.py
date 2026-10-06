from fasthtml.common import *
from components.page import AppContainer
from components.navigation import TopNav
from components.qa import (
    GUEST, MODERATOR, SORTS,
    QAPage, QuestionCard, QuestionForm, QuestionsListContainer, SessionCard, SessionStatusToggle,
)
from core.app import rt
from core.visitor import visitor_id
from crud.event import get_event, get_events, toggle_qa_active
from crud.question import (
    create_question, delete_question, get_liked_question_ids, get_question,
    get_questions_by_event, toggle_like, update_question,
)
from db.connection import db_manager
from db.schemas import QuestionCreate, QuestionUpdate
from utils import live
from utils.auth import is_moderator, require_conference_day, require_moderator

NICKNAME_COOKIE = 'qa_nickname'


def _sort(value: str) -> str:
    return value if value in SORTS else 'popular'


async def _questions_for(db, event_id: int, view: str, sort: str, request):
    """Questions for a view (guests see approved only) plus the visitor's likes"""
    questions = await get_questions_by_event(db, event_id, visible_only=view == GUEST, sort_by=sort)
    likes = await get_liked_question_ids(db, event_id, visitor_id(request)) if view == GUEST else set()
    return questions, likes


def _sessions_page(events, view: str, sess, request):
    cards = [SessionCard(e, is_moderator=view == MODERATOR) for e in sorted(events, key=lambda e: e.start_time)]
    return AppContainer(
        Div(
            TopNav('Q&A Sessions'),
            Div(P("Select a session to view or ask questions", cls="text-sm"), cls="text-center mb-8"),
            Div(
                *cards or [Div(
                    I(cls="fas fa-inbox text-4xl text-base-content/30 mb-4"),
                    P("No Q&A sessions available", cls="text-base-content/60"),
                    cls="timeline-box"
                )],
                cls="flex flex-col gap-4"
            ),
            id='page-content',
            cls='container mx-auto px-4 py-8 blue-background'
        ),
        is_moderator=is_moderator(sess),
        request=request
    )


async def _session_page(request, sess, event_id: int, view: str):
    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        if not event:
            return Response("Event not found", status_code=404)
        questions, likes = await _questions_for(db, event_id, view, 'popular', request)

    nickname = request.cookies.get(NICKNAME_COOKIE, '')
    return AppContainer(
        Div(
            TopNav('Q&A Moderator' if view == MODERATOR else 'Q&A Session'),
            QAPage(event, questions, view, user_likes=likes, nickname=nickname),
            id='page-content',
            cls='white-background'
        ),
        is_moderator=is_moderator(sess),
        request=request,
    )


async def _list_fragment(request, event_id: int, sort: str, view: str):
    sort = _sort(sort)
    async with db_manager.AsyncSessionLocal() as db:
        questions, likes = await _questions_for(db, event_id, view, sort, request)
    return QuestionsListContainer(questions, show_admin_controls=view == MODERATOR, user_likes=likes, sort=sort)


# Guest routes

@rt('/qa')
@require_conference_day
async def get(request, sess):
    async with db_manager.AsyncSessionLocal() as db:
        events = await get_events(db)
    return _sessions_page(events, GUEST, sess, request)


@rt('/qa/event/{event_id}')
@require_conference_day
async def get(request, sess, event_id: int):
    return await _session_page(request, sess, event_id, GUEST)


@rt('/qa/event/{event_id}/questions')
@require_conference_day
async def get(request, event_id: int, sort: str = "popular"):
    return await _list_fragment(request, event_id, sort, GUEST)


@rt('/qa/event/{event_id}/submit')
@require_conference_day
async def post(request, event_id: int, nickname: str = '', question_text: str = ''):
    """Submit a question; it waits for moderator approval before guests see it"""
    nickname = nickname.strip()[:50] or 'Anonymous'
    question_text = question_text.strip()[:500]

    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        if not event:
            return Div(P("Event not found", cls="text-error"), cls="alert alert-error")
        if not event.is_qa_active:
            return QuestionForm(event_id, nickname, is_active=False)
        if not question_text:
            return QuestionForm(event_id, nickname)
        question = await create_question(db, QuestionCreate(event_id=event_id, nickname=nickname, question_text=question_text))

    await live.publish(event_id, live.CREATED, question.id)
    return (
        QuestionForm(event_id, nickname, message="Submitted! It will appear once a moderator approves it."),
        cookie(NICKNAME_COOKIE, nickname, max_age=86400 * 365),
    )


@rt('/qa/question/{question_id}/like')
@require_conference_day
async def post(request, question_id: str):
    async with db_manager.AsyncSessionLocal() as db:
        question = await get_question(db, question_id)
        if not question:
            return Response("Question not found", status_code=404)
        liked, likes = await toggle_like(db, question_id, visitor_id(request))
        await db.refresh(question)

    await live.publish(question.event_id, live.LIKED, question.id, likes=likes)
    return QuestionCard(question, show_admin_controls=False, user_liked=liked)


@rt('/qa/event/{event_id}/stream')
@require_conference_day
async def get(request, sess, event_id: int, view: str = GUEST):
    """Server-Sent Events for live updates; moderator streams include unapproved questions"""
    if view == MODERATOR and not is_moderator(sess):
        return Response("Forbidden", status_code=403)
    return StreamingResponse(
        live.stream(event_id, MODERATOR if view == MODERATOR else GUEST),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Moderator routes

@rt('/qa/moderator')
@require_conference_day
@require_moderator
async def get(req, sess):
    async with db_manager.AsyncSessionLocal() as db:
        events = await get_events(db)
    return _sessions_page(events, MODERATOR, sess, req)


@rt('/qa/moderator/event/{event_id}')
@require_conference_day
@require_moderator
async def get(req, sess, event_id: int):
    return await _session_page(req, sess, event_id, MODERATOR)


@rt('/qa/moderator/event/{event_id}/questions')
@require_conference_day
@require_moderator
async def get(req, sess, event_id: int, sort: str = "popular"):
    return await _list_fragment(req, event_id, sort, MODERATOR)


@rt('/qa/moderator/event/{event_id}/toggle-qa')
@require_conference_day
@require_moderator
async def post(req, sess, event_id: int):
    async with db_manager.AsyncSessionLocal() as db:
        event = await toggle_qa_active(db, event_id)
    if not event:
        return Response("Event not found", status_code=404)
    await live.publish(event_id, live.STATUS, active=event.is_qa_active)
    return SessionStatusToggle(event_id, event.is_qa_active)


async def _moderate(question_id: str, change):
    """Apply `change(question) -> QuestionUpdate`, publish it, and return the moderator card"""
    async with db_manager.AsyncSessionLocal() as db:
        question = await get_question(db, question_id)
        if not question:
            return Response("Question not found", status_code=404)
        question = await update_question(db, question_id, change(question))
    await live.publish(question.event_id, live.UPDATED, question.id)
    return QuestionCard(question, show_admin_controls=True)


@rt('/qa/moderator/question/{question_id}/toggle-visibility')
@require_conference_day
@require_moderator
async def post(req, sess, question_id: str):
    return await _moderate(question_id, lambda q: QuestionUpdate(is_visible=not q.is_visible))


@rt('/qa/moderator/question/{question_id}/toggle-answered')
@require_conference_day
@require_moderator
async def post(req, sess, question_id: str):
    return await _moderate(question_id, lambda q: QuestionUpdate(is_answered=not q.is_answered))


@rt('/qa/moderator/question/{question_id}')
@require_conference_day
@require_moderator
async def delete(req, sess, question_id: str):
    async with db_manager.AsyncSessionLocal() as db:
        question = await get_question(db, question_id)
        if not question:
            return Response("Question not found", status_code=404)
        event_id = question.event_id
        await delete_question(db, question_id)
    await live.publish(event_id, live.DELETED, question_id)
    return Response("")
