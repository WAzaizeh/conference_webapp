from fasthtml.common import *

def QuestionCard(question, show_admin_controls=False, user_liked=False):
    """Display a single question card"""
    question_id = str(question.id)
    
    # Format timestamp
    from datetime import datetime
    now = datetime.now(question.created_at.tzinfo)
    time_diff = now - question.created_at
    
    if time_diff.days > 0:
        time_ago = f"{time_diff.days}d ago"
    elif time_diff.seconds > 3600:
        time_ago = f"{time_diff.seconds // 3600}h ago"
    elif time_diff.seconds > 60:
        time_ago = f"{time_diff.seconds // 60}m ago"
    else:
        time_ago = "just now"
    
    # Build the card
    card_classes = "card bg-base-100 shadow-md mb-4"
    if not question.is_visible and show_admin_controls:
        card_classes += " border-2 border-warning"
    
    return Div(
        Div(
            # Question header
            Div(
                Span(question.nickname, cls="font-semibold text-primary"),
                Span(f" • {time_ago}", cls="text-sm text-base-content/60"),
                Span(
                    I(cls="fas fa-check-circle text-success ml-2"),
                    " Answered",
                    cls="text-sm text-success ml-2 question-answered-badge",
                    data_answered="true"
                ) if question.is_answered else None,
                Span(
                    I(cls="fas fa-eye-slash text-warning ml-2"),
                    " Hidden",
                    cls="text-sm text-warning ml-2"
                ) if not question.is_visible and show_admin_controls else None,
                cls="mb-2"
            ),
            
            # Question text
            P(question.question_text, cls="mb-4 question-text"),
            
            # Actions row
            Div(
                # Like button
                Button(
                    I(cls=f"fas fa-heart {'text-error' if user_liked else ''}"),
                    Span(str(question.likes_count), cls="ml-2", id=f"likes-{question_id}"),
                    cls=f"btn btn-sm {'btn-error' if user_liked else 'btn-ghost'}",
                    hx_post=f"/qa/question/{question_id}/like",
                    hx_target=f"#question-{question_id}",
                    hx_swap="outerHTML",
                    id=f"like-btn-{question_id}"
                ) if not show_admin_controls else Div(
                    I(cls="fas fa-heart text-error"),
                    Span(str(question.likes_count), cls="ml-2"),
                    cls="flex items-center gap-2"
                ),
                
                # Admin controls
                Div(
                    Button(
                        I(cls=f"fas fa-eye{'-slash' if question.is_visible else ''}"),
                        cls="btn btn-sm btn-ghost",
                        hx_post=f"/qa/moderator/question/{question_id}/toggle-visibility",
                        hx_target=f"#question-{question_id}",
                        hx_swap="outerHTML",
                        title="Toggle visibility"
                    ),
                    Button(
                        I(cls=f"fas fa-check {'text-success' if question.is_answered else ''}"),
                        cls="btn btn-sm btn-ghost",
                        hx_post=f"/qa/moderator/question/{question_id}/toggle-answered",
                        hx_target=f"#question-{question_id}",
                        hx_swap="outerHTML",
                        title="Mark as answered"
                    ),
                    Button(
                        I(cls="fas fa-trash text-error"),
                        cls="btn btn-sm btn-ghost",
                        hx_delete=f"/qa/moderator/question/{question_id}",
                        hx_target=f"#question-{question_id}",
                        hx_swap="outerHTML",
                        hx_confirm="Are you sure you want to delete this question?",
                        title="Delete question"
                    ),
                    cls="flex gap-2"
                ) if show_admin_controls else None,
                
                cls="flex justify-between items-center"
            ),
            
            cls="card-body"
        ),
        cls=card_classes,
        id=f"question-{question_id}",
        data_question_id=question_id  # Add this for easy querying in tests
    )

def QuestionForm(event_id: int, initial_nickname="Anonymous", is_active=True):
    """Form to submit a new question"""
    btnclass = "btn btn-primary px-6 py-2"
    if not is_active:
        btnclass += " btn-disabled"
    btnstyle = "background-color: var(--primary-color); border-color: var(--primary-color); color: white;"
    if not is_active:
        btnstyle += " opacity: 0.5; cursor: not-allowed;"
    return Div(
        Form(
            Div(
                Input(
                    type="text",
                    placeholder="Your nickname (optional)",
                    name="nickname",
                    id="nickname",
                    hx_disable="true" if not is_active else "false",
                    cls="input input-bordered rounded-sm w-full"
                ),
                cls="form-control mb-4"
            ),
            Div(
                Textarea(
                    name="question_text",
                    id="question_text",
                    placeholder="Type your question here...",
                    required=True,
                    rows="3",
                    hx_disable="true" if not is_active else "false",
                    cls="textarea textarea-bordered rounded-sm w-full",
                    style="font-size: 1rem;"
                ),
                cls="form-control mb-4"
            ),
            Div(
                Button(
                    "Submit",
                    type="submit",
                    hx_disable="true" if not is_active else "false",
                    cls=btnclass,
                    style=btnstyle
                ),
                cls="flex align-end justify-end"
            ),
            method="POST",
            action=f"/qa/event/{event_id}/submit",
            hx_post=f"/qa/event/{event_id}/submit",
            hx_target="#question-form",
            hx_swap="outerHTML"
        ),
        id="question-form",
        cls="px-6"
    )

def QuestionsListContainer(questions, show_admin_controls=False, user_likes=None):
    """Container for list of questions"""
    user_likes = user_likes or set()
    
    if not questions:
        return Div(
            Div(
                I(cls="fas fa-comments text-4xl text-base-content/30 mb-4"),
                P("No questions yet. Be the first to ask!", cls="text-base-content/60"),
                cls="text-center py-12"
            ),
            id="questions-list"
        )
    
    return Div(
        *[QuestionCard(q, show_admin_controls, str(q.id) in user_likes) for q in questions],
        id="questions-list"
    )
