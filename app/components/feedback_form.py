from .feedback import (
    RatingQuestion,
    SingleSelectQuestion,
    MultiSelectQuestion,
    TextInputQuestion
)
from fasthtml.common import Form, Div, Button

def FeedbackForm():
    return Form(
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
        )