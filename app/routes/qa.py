from fasthtml.common import *
from components.page import AppContainer
from components.qa import (
    QuestionCard,
    QuestionForm,
    QuestionsListContainer,
    SessionStatusTag,
    SessionCard,
    SessionStatusToggle
)
from db.connection import db_manager
from db.schemas import QuestionCreate, QuestionUpdate
from crud.question import (
    create_question, 
    get_questions_by_event, 
    get_question,
    update_question,
    delete_question,
    toggle_like,
    check_user_liked
)
from crud.event import get_event, get_events, toggle_qa_active
from utils.sse_manager import sse_manager
from utils.auth import is_moderator, require_moderator
from core.app import rt
import asyncio
from utils.session import get_or_create_session_id
from components.navigation import TopNav
from utils.auth import require_conference_day

def get_nickname_from_cookie(request):
    """Get stored nickname from cookie"""
    return request.cookies.get('qa_nickname', 'Anonymous')

@rt('/qa')
@require_conference_day
async def get(request, sess):
    """Q&A main page - select session (accessible to everyone)"""
    async with db_manager.AsyncSessionLocal() as db:
        events = await get_events(db)
        
        # Sort events by start time
        events = sorted(events, key=lambda e: e.start_time)
        
        # Build event cards - guest view
        event_cards = [SessionCard(event, is_moderator=False) for event in events]
        
        return AppContainer(
            Div(
                TopNav('Q&A Sessions'),
                Div(
                    P(
                        "Select a session to view or ask questions",
                        cls="text-sm"
                    ),
                    cls="text-center mb-8"
                ),
                Div(
                    *event_cards if event_cards else [
                        Div(
                            I(cls="fas fa-inbox text-4xl text-base-content/30 mb-4"),
                            P("No Q&A sessions available", cls="text-base-content/60"),
                            cls="timeline-box"
                        )
                    ],
                    cls="flex flex-col gap-4"
                ),
                id='page-content',
                cls='container mx-auto px-4 py-8 blue-background'
            ),
            is_moderator=is_moderator(sess),
            request=request
        )

@rt('/qa/event/{event_id}')
@require_conference_day
async def get(request, sess, event_id: int):
    """Q&A page for a specific event (accessible to everyone)"""
    session_id = get_or_create_session_id(request)
    stored_nickname = get_nickname_from_cookie(request)
    
    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        if not event:
            return Response("Event not found", status_code=404)
        
        # Get questions (default to recent)
        questions = await get_questions_by_event(db, event_id, visible_only=True, sort_by="popular")
        
        # Check which questions user has liked
        user_likes = set()
        for q in questions:
            if await check_user_liked(db, str(q.id), session_id):
                user_likes.add(str(q.id))
    
    # Check if QA is active
    is_active = event.is_qa_active
    
    return AppContainer(
        Div(
            # Header
            Div(
                TopNav('Q&A Session'),
                Div(
                    H1(event.title, cls="text-lg font-bold"),
                    Div(
                        I(cls="far fa-clock text-base-content/70"),
                        P(
                            event.start_time.strftime("%I:%M %p"),
                            " • ",
                            event.location or "TBA",
                            cls="text-base-content/70",
                        ),
                        cls="flex items-center gap-2",
                    ),
                    SessionStatusTag(is_active),
                    cls="flex flex-col gap-2 px-6"
                ),
                cls="mb-4"
            ),
            
            # Question submission form
            QuestionForm(event_id, initial_nickname=stored_nickname, is_active=is_active),
            
            # Tabs for Recent/Popular
            Div(
                Div(
                    A(
                        "Popular",
                        role="tab",
                        cls="tab tab-active [--tab-bg:#D6ECF6] [--tab-hover:bg:#D6ECF6]",
                        id="popular-tab",
                        hx_get=f"/qa/event/{event_id}/questions?sort=popular",
                        hx_target="#questions-list",
                        hx_swap="outerHTML"
                    ),
                    A(
                        "Recent",
                        role="tab",
                        cls="tab",
                        id="recent-tab",
                        hx_get=f"/qa/event/{event_id}/questions?sort=recent",
                        hx_target="#questions-list",
                        hx_swap="outerHTML"
                    ),
                    role="tablist",
                    cls="tabs tabs-lifted"
                ),
                cls="px-6"
            ),
            
            # Questions list
            QuestionsListContainer(questions, user_likes=user_likes),
            
            # SSE connection for live updates
            Script(f"""
                if (typeof(EventSource) !== "undefined") {{
                    const eventSource = new EventSource('/qa/event/{event_id}/stream');
                    
                    eventSource.addEventListener('question_update', function(e) {{
                        const data = JSON.parse(e.data);
                        // Trigger HTMX refresh of questions list to show new/updated questions
                        htmx.ajax('GET', '/qa/event/{event_id}/questions?sort=recent', {{
                            target: '#questions-list',
                            swap: 'outerHTML'
                        }});
                    }});
                    
                    eventSource.onerror = function(e) {{
                        console.error('SSE error:', e);
                        eventSource.close();
                    }};
                    
                    // Cleanup on page unload
                    window.addEventListener('beforeunload', function() {{
                        eventSource.close();
                    }});
                }}
            """),
            id='page-content',
            cls='white-background'
        ),
        is_moderator=is_moderator(sess),
        request=request,
    ), cookie('qa_session_id', session_id, max_age=86400*30)

@rt('/qa/event/{event_id}/questions')
@require_conference_day
async def get(request, event_id: int, sort: str = "recent"):
    """Get questions list (for tab switching) - accessible to everyone"""
    session_id = get_or_create_session_id(request)
    
    async with db_manager.AsyncSessionLocal() as db:
        questions = await get_questions_by_event(db, event_id, visible_only=True, sort_by=sort)
        
        # Check which questions user has liked
        user_likes = set()
        for q in questions:
            if await check_user_liked(db, str(q.id), session_id):
                user_likes.add(str(q.id))
    
    # Update tab active state and return components directly
    return (
        QuestionsListContainer(questions, user_likes=user_likes),
        Script(f"""
            (function() {{
                // Update tab active states and custom colors
                document.querySelectorAll('.tab').forEach(tab => {{
                    tab.classList.remove('tab-active');
                    tab.style.setProperty('--tab-bg', '');
                    tab.style.setProperty('--tab-hover', '');
                }});
                
                const activeTab = document.getElementById('{sort}-tab');
                if (activeTab) {{
                    activeTab.classList.add('tab-active');
                    activeTab.style.setProperty('--tab-bg', '#D6ECF6');
                    activeTab.style.setProperty('--tab-hover', '#D6ECF6');
                }}
            }})();
        """)
    )

@rt('/qa/event/{event_id}/submit')
@require_conference_day
async def post(request, event_id: int):
    """Submit a new question - only if Q&A is active"""
    form_data = await request.form()
    session_id = get_or_create_session_id(request)
    
    async with db_manager.AsyncSessionLocal() as db:
        # Validate event exists and QA is active
        event = await get_event(db, event_id)
        if not event:
            return Div(
                P("Event not found", cls="text-error"),
                cls="alert alert-error"
            )
        
        if not event.is_qa_active:
            return Div(
                P("Q&A is currently closed for this session", cls="text-error"),
                cls="alert alert-error mb-4"
            )
        
        # Get nickname and save to cookie
        nickname = form_data.get('nickname', 'Anonymous').strip() or 'Anonymous'
        
        # Create question
        question_create = QuestionCreate(
            event_id=event_id,
            nickname=nickname,
            question_text=form_data.get('question_text', '').strip()
        )
        
        if not question_create.question_text:
            return Div(
                P("Question cannot be empty", cls="text-error"),
                cls="alert alert-error mb-4"
            )
        
        question = await create_question(db, question_create)
        
        # Broadcast update via SSE
        await sse_manager.send_question_update(
            event_id,
            {
                "id": str(question.id),
                "nickname": question.nickname,
                "question_text": question.question_text,
                "is_visible": question.is_visible,
                "is_answered": question.is_answered,
                "likes_count": question.likes_count,
                "created_at": question.created_at.isoformat()
            },
            "created"
        )
    
    # Return success message and reset form
    return (
        Div(
            
            QuestionForm(event_id, initial_nickname=nickname, show_success=True),
            id="question-form"
        ),
        cookie('qa_nickname', nickname, max_age=86400*365),  # Remember nickname for 1 year
        cookie('qa_session_id', session_id, max_age=86400*365)
    )

@rt('/qa/question/{question_id}/like')
@require_conference_day
async def post(request, question_id: str):
    """Toggle like on a question - accessible to everyone"""
    session_id = get_or_create_session_id(request)
    
    async with db_manager.AsyncSessionLocal() as db:
        question = await get_question(db, question_id)
        if not question:
            return Response("Question not found", status_code=404)
        
        # Toggle like
        liked, new_count = await toggle_like(db, question_id, session_id)
        
        # Broadcast like update via SSE
        await sse_manager.send_question_update(
            question.event_id,
            {
                "id": str(question.id),
                "likes_count": new_count
            },
            "like_updated"
        )
        
        # Refresh question to get updated data
        question = await get_question(db, question_id)
        user_liked = await check_user_liked(db, question_id, session_id)
    
    return (
        QuestionCard(question, show_admin_controls=False, user_liked=user_liked),
        cookie('qa_session_id', session_id, max_age=86400*30)  # 30 days
    )

@rt('/qa/event/{event_id}/stream')
@require_conference_day
async def get(request, event_id: int):
    """SSE endpoint for live updates - accessible to everyone"""
    async def event_stream():
        queue = await sse_manager.subscribe(event_id)
        try:
            # Send initial connection message
            yield "event: connected\ndata: {\"status\": \"connected\"}\n\n"
            
            # Keep connection alive with periodic pings
            while True:
                try:
                    # Wait for message with timeout
                    message = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield message.format()
                except asyncio.TimeoutError:
                    # Send keepalive ping
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.unsubscribe(event_id, queue)
    
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

# Moderator routes - require authentication via decorator
@rt('/qa/moderator/event/{event_id}')
@require_conference_day
@require_moderator
async def get(req, sess, event_id: int):
    """Moderator view for Q&A"""
    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        if not event:
            return Response("Event not found", status_code=404)
        
        # Get ALL questions (including hidden)
        questions = await get_questions_by_event(db, event_id, visible_only=False, sort_by="popular")
    
    return AppContainer(
        Div(
            # Header
            Div(
                TopNav('Q&A Moderator'),
                Div(
                    Div(
                        A(
                            I(cls="fas fa-eye mr-2"),
                            "Guest View",
                            href=f"/qa/event/{event_id}",
                            cls="btn btn-sm",
                            style="background-color: var(--primary-color); border-color: var(--primary-color); color: white;",
                            target="_blank"
                        ),
                        cls="flex items-center gap-2 mb-2"
                    ),
                    H1(event.title, cls="text-lg font-bold mb-2"),
                    P(
                        I(cls="far fa-clock mr-2"),
                        event.start_time.strftime("%I:%M %p"),
                        " • ",
                        event.location or "TBA",
                        cls="text-base-content/70 mb-2"
                    ),
                    # Q&A Activation Toggle
                    SessionStatusToggle(event_id, event.is_qa_active),
                    cls="mb-6 px-6"
                ),
                cls="mb-8"
            ),
            
            # Stats
            Div(
                Div(
                    Div(
                        Span(str(len(questions)), cls="text-3xl font-bold"),
                        Span("Total Questions", cls="text-sm text-base-content/70"),
                        cls="stat"
                    ),
                    Div(
                        Span(str(sum(1 for q in questions if q.is_visible)), cls="text-3xl font-bold"),
                        Span("Visible", cls="text-sm text-base-content/70"),
                        cls="stat",
                        style="color: #00A651;"
                    ),
                    Div(
                        Span(str(sum(1 for q in questions if q.is_answered)), cls="text-3xl font-bold"),
                        Span("Answered", cls="text-sm text-base-content/70"),
                        cls="stat",
                        style="color: var(--primary-color);"
                    ),
                    cls="stats shadow mb-6"
                ),
                cls="px-6"
            ),
            
            # Tabs for Recent/Popular
            Div(
                Div(
                    A(
                        "Popular",
                        role="tab",
                        cls="tab tab-active [--tab-bg:#D6ECF6] [--tab-hover:bg:#D6ECF6]",
                        id="popular-tab",
                        hx_get=f"/qa/moderator/event/{event_id}/questions?sort=popular",
                        hx_target="#questions-list",
                        hx_swap="outerHTML"
                    ),
                    A(
                        "Recent",
                        role="tab",
                        cls="tab",
                        id="recent-tab",
                        hx_get=f"/qa/moderator/event/{event_id}/questions?sort=recent",
                        hx_target="#questions-list",
                        hx_swap="outerHTML"
                    ),
                    role="tablist",
                    cls="tabs tabs-lifted"
                ),
                cls="px-6"
            ),

            # Questions list
            QuestionsListContainer(questions, show_admin_controls=True),
            
            # SSE connection for live updates
            Script(f"""
                if (typeof(EventSource) !== "undefined") {{
                    const eventSource = new EventSource('/qa/event/{event_id}/stream');
                    
                    eventSource.addEventListener('question_update', function(e) {{
                        const data = JSON.parse(e.data);
                        // Refresh questions list to show all updates (new, visibility, answered, likes)
                        location.reload();
                    }});
                    
                    eventSource.onerror = function(e) {{
                        console.error('SSE error:', e);
                        eventSource.close();
                    }};
                    
                    // Cleanup on page unload
                    window.addEventListener('beforeunload', function() {{
                        eventSource.close();
                    }});
                }}
            """),
            
            id='page-content',
            cls='white-background'
        ),
        is_moderator=is_moderator(sess),
        request=req
    )

@rt('/qa/moderator/event/{event_id}/questions')
@require_conference_day
@require_moderator
async def get(req, sess, event_id: int, sort: str = "recent"):
    """Get questions list for moderator (for tab switching) - includes hidden questions"""
    async with db_manager.AsyncSessionLocal() as db:
        # Get ALL questions (including hidden)
        questions = await get_questions_by_event(db, event_id, visible_only=False, sort_by=sort)
    
    # Update tab active state and return components directly
    return (
        QuestionsListContainer(questions, show_admin_controls=True),
        Script(f"""
            (function() {{
                // Update tab active states and custom colors
                document.querySelectorAll('.tab').forEach(tab => {{
                    tab.classList.remove('tab-active');
                    tab.style.setProperty('--tab-bg', '');
                    tab.style.setProperty('--tab-hover', '');
                }});
                
                const activeTab = document.getElementById('{sort}-tab');
                if (activeTab) {{
                    activeTab.classList.add('tab-active');
                    activeTab.style.setProperty('--tab-bg', '#D6ECF6');
                    activeTab.style.setProperty('--tab-hover', '#D6ECF6');
                }}
            }})();
        """)
    )

@rt('/qa/moderator')
@require_conference_day
@require_moderator
async def get(req, sess):
    """Moderator main page - select session to moderate"""
    async with db_manager.AsyncSessionLocal() as db:
        events = await get_events(db)
        
        # Sort events by start time
        events = sorted(events, key=lambda e: e.start_time)
        
        # Build event cards - moderator view (same appearance, different href)
        event_cards = [SessionCard(event, is_moderator=True) for event in events]
        
        return AppContainer(
            Div(
                TopNav("Q&A Sessions"),
                Div(
                    P(
                        "Select a session to view or ask questions",
                        cls="text-sm"
                    ),
                    cls="text-center mb-8"
                ),
                Div(
                    *event_cards if event_cards else [
                        Div(
                            I(cls="fas fa-inbox text-4xl text-base-content/30 mb-4"),
                            P("No Q&A sessions available", cls="text-base-content/60"),
                            cls="timeline-box"
                        )
                    ],
                    cls="flex flex-col gap-4"
                ),
                id='page-content',
                cls='container mx-auto px-4 py-8 blue-background'
            ),
            is_moderator=is_moderator(sess),
            request=req
        )

@rt('/qa/moderator/event/{event_id}/toggle-qa')
@require_conference_day
@require_moderator
async def post(req, sess, event_id: int):
    """Toggle Q&A activation status"""
    async with db_manager.AsyncSessionLocal() as db:
        event = await toggle_qa_active(db, event_id)
        if not event:
            return Response("Event not found", status_code=404)
    
    # Return success response (page will reload via onclick handler)
    return Response("OK")

@rt('/qa/moderator/question/{question_id}/toggle-visibility')
@require_conference_day
@require_moderator
async def post(req, sess, question_id: str):
    """Toggle question visibility"""
    async with db_manager.AsyncSessionLocal() as db:
        question = await get_question(db, question_id)
        if not question:
            return Response("Question not found", status_code=404)
        
        # Toggle visibility
        update_data = QuestionUpdate(is_visible=not question.is_visible)
        question = await update_question(db, question_id, update_data)
        
        # Broadcast update via SSE
        await sse_manager.send_question_update(
            question.event_id,
            {
                "id": str(question.id),
                "is_visible": question.is_visible
            },
            "updated"
        )
    
    return QuestionCard(question, show_admin_controls=True)

@rt('/qa/moderator/question/{question_id}/toggle-answered')
@require_conference_day
@require_moderator
async def post(req, sess, question_id: str):
    """Toggle question answered status"""
    async with db_manager.AsyncSessionLocal() as db:
        question = await get_question(db, question_id)
        if not question:
            return Response("Question not found", status_code=404)
        
        # Toggle answered status
        update_data = QuestionUpdate(is_answered=not question.is_answered)
        question = await update_question(db, question_id, update_data)
        
        # Broadcast update via SSE
        await sse_manager.send_question_update(
            question.event_id,
            {
                "id": str(question.id),
                "is_answered": question.is_answered
            },
            "updated"
        )
    
    return QuestionCard(question, show_admin_controls=True)

@rt('/qa/moderator/question/{question_id}')
@require_conference_day
@require_moderator
async def delete(req, sess, question_id: str):
    """Delete a question"""
    async with db_manager.AsyncSessionLocal() as db:
        question = await get_question(db, question_id)
        if not question:
            return Response("Question not found", status_code=404)
        
        event_id = question.event_id
        
        # Delete question
        await delete_question(db, question_id)
        
        # Broadcast update via SSE
        await sse_manager.send_question_update(
            event_id,
            {"id": question_id},
            "deleted"
        )
    
    # Return empty response to remove the card
    return Response("")
