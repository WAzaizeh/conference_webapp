from fasthtml.common import *
from components.page import AppContainer
from components.qa import QuestionCard, QuestionForm, QuestionsListContainer, SessionStatusTag
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
            
            card_class = "timeline-box p-6 flex flex-col justify-evenly"
            if is_active:
                card_class += " border-2 border-primary"
            
            event_cards.append(
                A(
                    Div(
                        Div(
                            Div(
                                H3(event.title, cls="text-base font-medium"),
                                SessionStatusTag(is_active, text_cls="text-xs"),
                                cls="flex justify-between gap-4 items-start"
                            ),
                            P(
                                I(cls="far fa-clock mr-2"),
                                time_str,
                                " • ",
                                event.location or "TBA",
                                cls="text-sm text-base-content/70 mt-2"
                            ),
                        ),
                        cls=card_class
                    ),
                    href=f"/qa/event/{event.id}"
                )
            )
        
        return AppContainer(
            Div(
                # Header
                TopNav('Q&A Sessions'),
                Div(
                    
                    P(
                        "Select a session to view or ask questions",
                        cls="text-sm"
                    ),
                    cls="text-center mb-8"
                ),
                
                # Events grid
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
            request=request  # Pass request to show moderator login on select pages
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
            
            # Question submission form (only if active)
            # TODO: Disable form if not active
            QuestionForm(event_id, initial_nickname=stored_nickname, is_active=is_active),
            
            # Tabs for Recent/Popular
            Div(
                Div(
                    A(
                        "Recent",
                        cls="rounded-none px-4 border-b-2 font-semibold",
                        id="recent-tab",
                        hx_get=f"/qa/event/{event_id}/questions?sort=recent",
                        hx_target="#questions-list",
                        hx_swap="outerHTML",
                        style="border-color: var(--primary-color);"
                    ),
                    A(
                        "Popular",
                        cls="rounded-none px-4 text-base-content/70",
                        id="popular-tab",
                        hx_get=f"/qa/event/{event_id}/questions?sort=popular",
                        hx_target="#questions-list",
                        hx_swap="outerHTML",
                    ),
                    cls="flex justify-start border-b border-base-300"
                ),
                cls="px-6",
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
        request=request,  # Pass request to show moderator login on select pages
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
            
            QuestionForm(event_id, initial_nickname=nickname, show_success=True),
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
                TopNav('Q&A Session'),
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
        request=req  # Pass request to show moderator login on select pages
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
                    TopNav("Q&A Session Management"),
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
            is_moderator=is_moderator(sess),
            request=req  # Pass request to show moderator login on select pages
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
