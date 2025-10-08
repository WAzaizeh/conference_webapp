from fasthtml.common import *
from components.page import AppContainer
from components.feedback import (
    SingleSelectQuestion, 
    MultiSelectQuestion, 
    TextInputQuestion,
    RatingQuestion
)
from db.connection import db_manager
from db.schemas import FeedbackSubmissionCreate
from crud.feedback import create_feedback, check_recent_submission

def get_feedback_routes(rt):
    
    @rt('/feedback')
    async def get(request):
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
                Form(
                    # Overall Experience Rating
                    RatingQuestion(
                        question="How would you rate your overall conference experience?",
                        name="overall_rating",
                        max_rating=5,
                        required=True
                    ),
                    
                    # Content Quality
                    SingleSelectQuestion(
                        question="How would you rate the quality of the sessions and presentations?",
                        name="content_quality",
                        options=[
                            "Excellent",
                            "Very Good",
                            "Good",
                            "Fair",
                            "Poor"
                        ],
                        required=True
                    ),
                    
                    # Most Valuable Aspects
                    MultiSelectQuestion(
                        question="What aspects of the conference did you find most valuable? (Select all that apply)",
                        name="valuable_aspects",
                        options=[
                            "Keynote speakers",
                            "Workshop sessions",
                            "Networking opportunities",
                            "Prayer facilities",
                            "Food and refreshments",
                            "Venue and location",
                            "Event organization"
                        ]
                    ),
                    
                    # Favorite Session (Optional)
                    TextInputQuestion(
                        question="What was your favorite session or speaker?",
                        name="favorite_session",
                        placeholder="Tell us about your favorite part...",
                        required=False,
                        multiline=False
                    ),
                    
                    # Improvement Suggestions
                    TextInputQuestion(
                        question="What could we improve for future conferences?",
                        name="improvements",
                        placeholder="Your suggestions help us create better experiences...",
                        required=False,
                        multiline=True
                    ),
                    
                    # Would Attend Again
                    SingleSelectQuestion(
                        question="Would you attend future MAS conferences?",
                        name="attend_again",
                        options=[
                            "Definitely",
                            "Probably",
                            "Maybe",
                            "Probably not",
                            "Definitely not"
                        ],
                        required=True
                    ),
                    
                    # Additional Comments
                    TextInputQuestion(
                        question="Any additional comments or feedback?",
                        name="additional_comments",
                        placeholder="Share any other thoughts...",
                        required=False,
                        multiline=True
                    ),
                    
                    # Submit Button
                    Div(
                        Button(
                            "Submit Feedback",
                            type="submit",
                            cls="btn btn-primary btn-lg w-full sm:w-auto px-12"
                        ),
                        cls="flex justify-center mt-8"
                    ),
                    
                    method="POST",
                    action="/feedback/submit",
                    cls="max-w-3xl mx-auto"
                ),
                
                cls="container mx-auto px-4 py-8"
            )
        )
    
    @rt('/feedback/submit')
    async def post(request):
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
                    )
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
            )
        )
