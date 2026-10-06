from fasthtml.common import *
from components.page import AppContainer
from components.feedback_form import FeedbackForm
from components.feedback_message import FeedbackMessage
from db.connection import db_manager
from crud.feedback import get_feedback_count, get_user_feedback, save_feedback
from utils.auth import is_moderator, require_moderator, require_feedback_window
from core.app import rt
from core.visitor import visitor_id
from components.navigation import TopNav

@rt('/feedback')
@require_feedback_window
async def get(request, sess):
    """Display the feedback survey form - check if already submitted"""
    
    async with db_manager.AsyncSessionLocal() as db:
        already_submitted = await get_user_feedback(db, visitor_id(request)) is not None

    if already_submitted:
        return AppContainer(
            Div(
                TopNav('Feedback'),
                FeedbackMessage(
                    title="Already Submitted",
                    message="You've already submitted feedback. Would you like to edit your submission?",
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
@require_feedback_window
async def get(request, sess):
    """Display the feedback form with existing values for editing"""
    
    async with db_manager.AsyncSessionLocal() as db:
        existing_feedback = await get_user_feedback(db, visitor_id(request))
        
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
@require_feedback_window
async def post(request, sess):
    """Handle feedback form submission (both new and edit)"""
    
    # Get form data
    form_data = await request.form()
    
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
        await save_feedback(db, visitor_id(request), submission_data)
    
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
        total_submissions = await get_feedback_count(db)
    
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
            
            cls="container mx-auto px-4 py-8 h-full"
        ),
        is_moderator=is_moderator(sess),
        request=req  # Pass request to show moderator login on select pages
    )