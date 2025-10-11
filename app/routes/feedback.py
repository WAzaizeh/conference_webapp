from fasthtml.common import *
from components.page import AppContainer
from components.feedback_form import FeedbackForm
from db.connection import db_manager
from db.schemas import FeedbackSubmissionCreate
from crud.feedback import create_feedback, check_recent_submission
from utils.auth import is_moderator, require_moderator
from sqlalchemy.future import select
from sqlalchemy import func
from db.models import FeedbackSubmission
from core.app import rt
    
@rt('/feedback')
async def get(request, sess):
    """Display the feedback survey form"""
    return AppContainer(
        Div(
            # Header
            Div(
                H1("Conference Feedback Survey", cls="text-4xl font-bold text-center mb-2"),
                P(
                    "Help us improve future events by sharing your experience!",
                    cls="text-center text-base-content/70 mb-8"
                ),
                cls="mb-8"
            ),
            
            # Feedback Form
            FeedbackForm(),
            
            cls="container mx-auto px-4 py-8"
        ),
        is_moderator=is_moderator(sess)
    )

@rt('/feedback/submit')
async def post(request, sess):
    """Handle feedback form submission"""
    
    # Get form data
    form_data = await request.form()
    
    # Get client IP address
    ip_address = request.client.host if hasattr(request, 'client') else None
    user_agent = request.headers.get('user-agent', '')
    
    # Check for recent submission from this IP
    async with db_manager.AsyncSessionLocal() as db:
        # Check if already submitted in last 24 hours
        has_recent = await check_recent_submission(db, ip_address, hours=24)
        
        if has_recent:
            return AppContainer(
                Div(
                    Div(
                        Div(
                            I(cls="fas fa-exclamation-circle text-6xl text-warning mb-4"),
                            H2("Already Submitted", cls="text-3xl font-bold mb-4"),
                            P(
                                "You've already submitted feedback recently. Thank you for your input!",
                                cls="text-lg mb-6"
                            ),
                            A(
                                "Return to Home",
                                href="/",
                                cls="btn btn-primary"
                            ),
                            cls="text-center"
                        ),
                        cls="card bg-base-100 shadow-xl p-8 max-w-md mx-auto"
                    ),
                    cls="container mx-auto px-4 py-16"
                ),
                is_moderator=is_moderator(sess)
            )
        
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
        
        # Create feedback submission
        feedback_create = FeedbackSubmissionCreate(submission_data=submission_data)
        await create_feedback(db, feedback_create, ip_address, user_agent)
    
    # Show success AppContainer
    return AppContainer(
        Div(
            Div(
                Div(
                    I(cls="fas fa-check-circle text-6xl text-success mb-4"),
                    H2("Thank You!", cls="text-3xl font-bold mb-4"),
                    P(
                        "Your feedback has been submitted successfully. We appreciate you taking the time to help us improve!",
                        cls="text-lg mb-6 text-center"
                    ),
                    Div(
                        A(
                            "Return to Home",
                            href="/",
                            cls="btn btn-primary"
                        ),
                        cls="flex justify-center"
                    ),
                    cls="text-center"
                ),
                cls="card bg-base-100 shadow-xl p-8 max-w-md mx-auto"
            ),
            cls="container mx-auto px-4 py-16"
        ),
        is_moderator=is_moderator(sess)
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
                Span("Moderator Panel", cls="badge badge-secondary badge-lg mb-4"),
                H1("Feedback Submissions", cls="text-4xl font-bold mb-2"),
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
        is_moderator=is_moderator(sess)
    )