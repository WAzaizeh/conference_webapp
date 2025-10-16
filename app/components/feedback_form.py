from .feedback import (
    RatingQuestion,
    SingleSelectQuestion,
    MultiSelectQuestion,
    TextInputQuestion
)
from fasthtml.common import *

def FeedbackForm(initial_values: dict = None, is_edit: bool = False):
    """
    Feedback form component
    
    Args:
        initial_values: Dictionary of form field values to pre-populate
        is_edit: Whether this is an edit form (shows different submit text)
    """
    if initial_values is None:
        initial_values = {}
    
    def get_value(key, default=""):
        """Helper to get value from initial_values"""
        return initial_values.get(key, default)
    
    def is_checked(key, value):
        """Helper to check if checkbox should be checked"""
        field_value = initial_values.get(key)
        if isinstance(field_value, list):
            return value in field_value
        return field_value == value
    
    submit_text = "Update Feedback" if is_edit else "Submit Feedback"
    
    return Form(
            # Overall Experience Rating
            RatingQuestion(
                question="How would you rate your overall conference experience?",
                name="overall_rating",
                max_rating=5,
                required=True,
                selected_rating=get_value("overall_rating")
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
                required=True,
                selected_value=get_value("content_quality")
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
                ],
                selected_values=get_value("valuable_aspects")
            ),
            
            # Favorite Session (Optional)
            TextInputQuestion(
                question="What was your favorite session or speaker?",
                name="favorite_session",
                placeholder="Tell us about your favorite part...",
                required=False,
                multiline=False,
                value=get_value("favorite_session")
            ),
            
            # Improvement Suggestions
            TextInputQuestion(
                question="What could we improve for future conferences?",
                name="improvements",
                placeholder="Your suggestions help us create better experiences...",
                required=False,
                multiline=True,
                value=get_value("improvements")
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
                required=True,
                selected_value=get_value("attend_again")
            ),
            
            # Additional Comments
            TextInputQuestion(
                question="Any additional comments or feedback?",
                name="additional_comments",
                placeholder="Share any other thoughts...",
                required=False,
                multiline=True,
                value=get_value("additional_comments")
            ),
            
            # Submit Button
            Div(
                Button(
                    submit_text,
                    type="submit",
                    cls="btn btn-primary px-6 py-2",
                    style="background-color: var(--primary-color); border-color: var(--primary-color); color: white;"
                ),
                cls="flex mb-2 align-center justify-center"
            ),
            method="POST",
            action="/feedback/submit",
            cls="max-w-3xl mb mx-auto flex flex-col gap-4 px-6"
        )