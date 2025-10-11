from fasthtml.common import *
from components.page import AppContainer
from components.qa import QuestionCard, QuestionForm, QuestionsListContainer
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
import uuid

def get_or_create_session_id(request):
    """Get existing session ID from cookie or create new one"""
    session_id = request.cookies.get('qa_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    return session_id

def get_nickname_from_cookie(request):
    """Get stored nickname from cookie"""
    return request.cookies.get('qa_nickname', 'Anonymous')

@rt('/qa')
async def get(request, sess):
    """Q&A main page - select session (accessible to everyone)"""
    async with db_manager.AsyncSessionLocal() as db:
        events = await get_events(db)
        
        # Sort events by start time
        events = sorted(events, key=lambda e: e.start_time)
        
        # Build event cards
        event_cards = []
        for event in events:
            # Check if QA is active
            is_active = event.is_qa_active
            
            # Format time
            time_str = event.start_time.strftime("%I:%M %p")
            
            card_class = "card bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            if is_active:
                card_class += " border-2 border-primary"
            
            event_cards.append(
                A(
                    Div(
                        Div(
                            Div(
                                H3(event.title, cls="card-title text-lg"),
                                Span(
                                    I(cls="fas fa-circle text-primary mr-2 animate-pulse"),
                                    "Q&A Active",
                                    cls="badge badge-primary"
                                ) if is_active else Span(
                                    "Q&A Closed",
                                    cls="badge badge-ghost"
                                ),
                                cls="flex justify-between items-start"
                            ),
                            P(
                                I(cls="far fa-clock mr-2"),
                                time_str,
                                " • ",
                                event.location or "TBA",
                                cls="text-sm text-base-content/70 mt-2"
                            ),
                            cls="card-body"
                        ),
                        cls=card_class
                    ),
                    href=f"/qa/event/{event.id}"
                )
            )
        
        return AppContainer(
            Div(
                # Header
                Div(
                    H1("Q&A Sessions", cls="text-4xl font-bold mb-2"),
                    P(
                        "Select a session to view or ask questions",
                        cls="text-base-content/70"
                    ),
                    cls="text-center mb-8"
                ),
                
                # Events grid
                Div(
                    *event_cards if event_cards else [
                        Div(
                            I(cls="fas fa-inbox text-4xl text-base-content/30 mb-4"),
                            P("No Q&A sessions available", cls="text-base-content/60"),
                            cls="text-center py-12"
                        )
                    ],
                    cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                ),
                
                cls="container mx-auto px-4 py-8"
            ),
            is_moderator=is_moderator(sess)
        )

@rt('/qa/event/{event_id}')
async def get(request, sess, event_id: int):
    """Q&A page for a specific event (accessible to everyone)"""
    session_id = get_or_create_session_id(request)
    stored_nickname = get_nickname_from_cookie(request)
    
    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        if not event:
            return Response("Event not found", status_code=404)
        
        # Get questions (default to recent)
        questions = await get_questions_by_event(db, event_id, visible_only=True, sort_by="recent")
        
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
                A(
                    I(cls="fas fa-arrow-left mr-2"),
                    "Back to Sessions",
                    href="/qa",
                    cls="btn btn-ghost mb-4"
                ),
                Div(
                    H1(event.title, cls="text-3xl font-bold mb-2"),
                    P(
                        I(cls="far fa-clock mr-2"),
                        event.start_time.strftime("%I:%M %p"),
                        " • ",
                        event.location or "TBA",
                        cls="text-base-content/70"
                    ),
                    Span(
                        I(cls="fas fa-circle text-primary mr-2 animate-pulse"),
                        "Q&A Active - Submit Questions",
                        cls="badge badge-primary badge-lg mt-2"
                    ) if is_active else Span(
                        I(cls="fas fa-lock mr-2"),
                        "Q&A Closed - View Only",
                        cls="badge badge-ghost badge-lg mt-2"
                    ),
                    cls="mb-6"
                ),
                cls="mb-8"
            ),
            
            # Question submission form (only if active)
            QuestionForm(event_id, initial_nickname=stored_nickname) if is_active else Div(
                Div(
                    I(cls="fas fa-info-circle text-info text-2xl mb-2"),
                    P("Question submissions are currently closed for this session.", cls="font-semibold"),
                    cls="alert alert-info flex flex-col items-center mb-6"
                )
            ),
            
            # Tabs for Recent/Popular
            Div(
                Div(
                    A(
                        "Recent",
                        cls="tab tab-bordered tab-active",
                        id="recent-tab",
                        hx_get=f"/qa/event/{event_id}/questions?sort=recent",
                        hx_target="#questions-list",
                        hx_swap="outerHTML"
                    ),
                    A(
                        "Popular",
                        cls="tab tab-bordered",
                        id="popular-tab",
                        hx_get=f"/qa/event/{event_id}/questions?sort=popular",
                        hx_target="#questions-list",
                        hx_swap="outerHTML"
                    ),
                    cls="tabs tabs-boxed mb-6"
                ),
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
            
            cls="container mx-auto px-4 py-8 max-w-4xl"
        ),
        is_moderator=is_moderator(sess),
    ), cookie('qa_session_id', session_id, max_age=86400*30)  # 30 days

@rt('/qa/event/{event_id}/questions')
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
            document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('tab-active'));
            document.getElementById('{sort}-tab').classList.add('tab-active');
        """)
    )

@rt('/qa/event/{event_id}/submit')
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
            Div(
                I(cls="fas fa-check-circle text-success text-2xl mb-2"),
                P("Question submitted! It will appear after moderator approval.", cls="font-semibold"),
                cls="alert alert-success mb-4 flex flex-col items-center"
            ),
            QuestionForm(event_id, initial_nickname=nickname),
            id="question-form"
        ),
        cookie('qa_nickname', nickname, max_age=86400*365),  # Remember nickname for 1 year
        cookie('qa_session_id', session_id, max_age=86400*365)
    )

@rt('/qa/question/{question_id}/like')
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
@require_moderator
async def get(req, sess, event_id: int):
    """Moderator view for Q&A"""
    async with db_manager.AsyncSessionLocal() as db:
        event = await get_event(db, event_id)
        if not event:
            return Response("Event not found", status_code=404)
        
        # Get ALL questions (including hidden)
        questions = await get_questions_by_event(db, event_id, visible_only=False, sort_by="recent")
    
    return AppContainer(
        Div(
            # Header
            Div(
                A(
                    I(cls="fas fa-arrow-left mr-2"),
                    "Back to Sessions",
                    href="/qa/moderator",
                    cls="btn btn-ghost mb-4"
                ),
                Div(
                    Div(
                        Span("Moderator View", cls="badge badge-secondary mb-2 mr-2"),
                        A(
                            I(cls="fas fa-eye mr-2"),
                            "Guest View",
                            href=f"/qa/event/{event_id}",
                            cls="btn btn-sm btn-outline",
                            target="_blank"
                        ),
                        cls="flex items-center gap-2 mb-2"
                    ),
                    H1(event.title, cls="text-3xl font-bold mb-2"),
                    P(
                        I(cls="far fa-clock mr-2"),
                        event.start_time.strftime("%I:%M %p"),
                        " • ",
                        event.location or "TBA",
                        cls="text-base-content/70 mb-2"
                    ),
                    # Q&A Activation Toggle
                    Div(
                        Button(
                            I(cls=f"fas fa-{'unlock' if event.is_qa_active else 'lock'} mr-2"),
                            "Deactivate Q&A" if event.is_qa_active else "Activate Q&A",
                            cls=f"btn btn-{'error' if event.is_qa_active else 'success'}",
                            hx_post=f"/qa/moderator/event/{event_id}/toggle-qa",
                            hx_swap="none",
                            onclick="setTimeout(() => location.reload(), 500)"
                        ),
                        Span(
                            I(cls="fas fa-circle text-success mr-2 animate-pulse"),
                            "Q&A Active",
                            cls="badge badge-success ml-2"
                        ) if event.is_qa_active else Span(
                            I(cls="fas fa-circle text-error mr-2"),
                            "Q&A Closed",
                            cls="badge badge-error ml-2"
                        ),
                        cls="flex items-center gap-2"
                    ),
                    cls="mb-6"
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
                        Span(str(sum(1 for q in questions if q.is_visible)), cls="text-3xl font-bold text-success"),
                        Span("Visible", cls="text-sm text-base-content/70"),
                        cls="stat"
                    ),
                    Div(
                        Span(str(sum(1 for q in questions if q.is_answered)), cls="text-3xl font-bold text-primary"),
                        Span("Answered", cls="text-sm text-base-content/70"),
                        cls="stat"
                    ),
                    cls="stats shadow mb-6"
                ),
            ),
            
            # Questions list
            H2("All Questions", cls="text-2xl font-bold mb-4"),
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
            
            cls="container mx-auto px-4 py-8 max-w-4xl"
        ),
        is_moderator=is_moderator(sess),
    )

@rt('/qa/moderator')
@require_moderator
async def get(req, sess):
    """Moderator main page - select session to moderate"""
    async with db_manager.AsyncSessionLocal() as db:
        events = await get_events(db)
        
        # Sort events by start time
        events = sorted(events, key=lambda e: e.start_time)
        
        # Build event cards with question counts
        event_cards = []
        for event in events:
            # Get question count for this event
            questions = await get_questions_by_event(db, event.id, visible_only=False)
            total_questions = len(questions)
            hidden_questions = sum(1 for q in questions if not q.is_visible)
            
            # Check if QA is active
            is_active = event.is_qa_active
            
            # Format time
            time_str = event.start_time.strftime("%I:%M %p")
            
            card_class = "card bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            if is_active:
                card_class += " border-2 border-success"
            
            event_cards.append(
                A(
                    Div(
                        Div(
                            Div(
                                H3(event.title, cls="card-title text-lg"),
                                Div(
                                    Span(
                                        I(cls="fas fa-circle text-success mr-2 animate-pulse"),
                                        "Active",
                                        cls="badge badge-success badge-sm"
                                    ) if is_active else Span(
                                        I(cls="fas fa-circle text-error mr-2"),
                                        "Closed",
                                        cls="badge badge-error badge-sm"
                                    ),
                                    Span(
                                        I(cls="fas fa-question-circle mr-1"),
                                        str(total_questions),
                                        cls="badge badge-ghost badge-sm ml-2"
                                    ),
                                    Span(
                                        I(cls="fas fa-eye-slash mr-1"),
                                        str(hidden_questions),
                                        cls="badge badge-warning badge-sm ml-2"
                                    ) if hidden_questions > 0 else None,
                                    cls="flex gap-2"
                                ),
                                cls="flex justify-between items-start flex-wrap gap-2"
                            ),
                            P(
                                I(cls="far fa-clock mr-2"),
                                time_str,
                                " • ",
                                event.location or "TBA",
                                cls="text-sm text-base-content/70 mt-2"
                            ),
                            cls="card-body"
                        ),
                        cls=card_class
                    ),
                    href=f"/qa/moderator/event/{event.id}"
                )
            )
        
        return AppContainer(
            Div(
                # Header
                Div(
                    Span("Moderator Panel", cls="badge badge-secondary badge-lg mb-4"),
                    H1("Q&A Session Management", cls="text-4xl font-bold mb-2"),
                    P(
                        "Select a session to moderate questions and control Q&A activation",
                        cls="text-base-content/70"
                    ),
                    cls="text-center mb-8"
                ),
                
                # Events grid
                Div(
                    *event_cards if event_cards else [
                        Div(
                            I(cls="fas fa-inbox text-4xl text-base-content/30 mb-4"),
                            P("No events available", cls="text-base-content/60"),
                            cls="text-center py-12 col-span-full"
                        )
                    ],
                    cls="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                ),
                
                cls="container mx-auto px-4 py-8"
            ),
            is_moderator=is_moderator(sess)
        )

@rt('/qa/moderator/event/{event_id}/toggle-qa')
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
