from fasthtml.common import *
from components.page import AppContainer
from components.feedback_form import FeedbackForm
from components.feedback_message import FeedbackMessage
from db.connection import db_manager
from db.schemas import FeedbackSubmissionCreate
from crud.feedback import create_feedback, check_recent_submission, get_user_feedback
from utils.auth import is_moderator, require_moderator
from sqlalchemy.future import select
from sqlalchemy import func
from db.models import FeedbackSubmission
from core.app import rt
from utils.session import get_or_create_session_id
from components.navigation import TopNav
from utils.auth import require_conference_day

@rt('/feedback')
@require_conference_day
async def get(request, sess):
    """Display the feedback survey form - check if already submitted"""
    
    # Get session ID from cookie or create new one
    session_id = get_or_create_session_id(request)
    
    async with db_manager.AsyncSessionLocal() as db:
        # Check if already submitted in last 24 hours
        has_recent = await check_recent_submission(db, session_id=session_id, hours=24)
        
    if has_recent:
        return AppContainer(
            Div(
                TopNav('Feedback'),
                FeedbackMessage(
                    title="Already Submitted",
                    message="You've already submitted feedback recently. Would you like to edit your submission?",
                    button_text="Edit Feedback",
                    button_href="/feedback/edit",
                    icon_color="text-success"
                ),
            ),
            is_moderator=is_moderator(sess),
            request=request  # Pass request to show moderator login on select pages
        )
    
    return AppContainer(
        Div(
            # Header
            Div(
                TopNav('Conference Feedback Survey'),
                P(
                    "Help us improve future events by sharing your experience!",
                    cls="text-center text-base-content/70 mb-8"
                ),
                cls="mb-8"
            ),
            
            # Feedback Form
            FeedbackForm(),
            
            id="page-content",
            cls="blue-background"
        ),
        is_moderator=is_moderator(sess),
        request=request  # Pass request to show moderator login on select pages
    )

@rt('/feedback/edit')
@require_conference_day
async def get(request, sess):
    """Display the feedback form with existing values for editing"""
    
    # Get session ID
    session_id = get_or_create_session_id(request)
    
    async with db_manager.AsyncSessionLocal() as db:
        # Get existing feedback
        existing_feedback = await get_user_feedback(db, session_id=session_id)
        
        if not existing_feedback:
            # No feedback found, redirect to regular form
            return RedirectResponse('/feedback', status_code=303)
        
        # Get the submission data
        form_values = existing_feedback.submission_data or {}
    
    return AppContainer(
        Div(
            # Header
            Div(
                TopNav('Edit Feedback'),
                H1("Edit Your Feedback", cls="text-4xl font-bold text-center mb-2"),
                P(
                    "Update your feedback submission",
                    cls="text-center text-base-content/70 mb-8"
                ),
                cls="mb-8 text-center"
            ),
            
            # Feedback Form with existing values
            FeedbackForm(initial_values=form_values, is_edit=True),
            
            cls="container mx-auto px-4 py-8"
        ),
        is_moderator=is_moderator(sess),
        request=request  # Pass request to show moderator login on select pages
    )

@rt('/feedback/submit')
@require_conference_day
async def post(request, sess):
    """Handle feedback form submission (both new and edit)"""
    
    # Get form data
    form_data = await request.form()
    
    # Get session ID from cookie or create new one
    session_id = get_or_create_session_id(request)
    
    # Process form data
    submission_data = {}
    for key, value in form_data.items():
        if key.endswith('[]'):
            # Handle multi-select checkboxes
            clean_key = key[:-2]
            if clean_key not in submission_data:
                submission_data[clean_key] = []
            submission_data[clean_key].append(value)
        else:
            submission_data[key] = value
    
    async with db_manager.AsyncSessionLocal() as db:
        # Create or update feedback submission
        feedback_create = FeedbackSubmissionCreate(submission_data=submission_data)
        await create_feedback(db, feedback_create, session_id)
    
    # Show success message
    return AppContainer(
        Div(
            TopNav('Feedback'),
            FeedbackMessage(
                icon_class="fas fa-check-circle text-success",
                title="Thank You!",
                message="Your feedback has been submitted successfully. We appreciate you taking the time to help us improve!",
                button_text="Return to Home",
                button_href="/",
                icon_color="text-success"
            ),
        ),
        is_moderator=is_moderator(sess),
        request=request  # Pass request to show moderator login on select pages
    )

@rt('/feedback/moderator')
@require_moderator
async def get(req, sess):
    """Moderator view - simple submission count"""
    async with db_manager.AsyncSessionLocal() as db:
        # Get total submission count
        result = await db.execute(
            select(func.count(FeedbackSubmission.id))
        )
        total_submissions = result.scalar() or 0
    
    return AppContainer(
        Div(
            # Header
            Div(
                TopNav('Feedback Submissions'),
                P(
                    "Total number of submitted feedback forms",
                    cls="text-base-content/70"
                ),
                cls="text-center mb-8"
            ),
            
            # Statistics Card
            Div(
                Div(
                    Div(
                        I(cls="fas fa-comment-dots text-6xl text-primary mb-4"),
                        Div(
                            Span(str(total_submissions), cls="text-6xl font-bold text-primary block mb-2"),
                            Span("Total Submissions", cls="text-xl text-base-content/70"),
                            cls="text-center"
                        ),
                        cls="flex flex-col items-center py-8"
                    ),
                    cls="card bg-base-100 shadow-xl"
                ),
                cls="max-w-md mx-auto mb-8"
            ),
            
            # Refresh Button
            Div(
                Button(
                    I(cls="fas fa-sync-alt mr-2"),
                    "Refresh Count",
                    cls="btn btn-primary btn-lg",
                    onclick="location.reload()"
                ),
                cls="text-center"
            ),
            
            cls="container mx-auto px-4 py-8"
        ),
        is_moderator=is_moderator(sess),
        request=req  # Pass request to show moderator login on select pages
    )