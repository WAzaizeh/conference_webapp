from datetime import datetime
from fasthtml.common import *
from db.models import Event

GUEST, MODERATOR = 'guest', 'moderator'
SORTS = ('popular', 'recent')


def list_url(event_id: int, view: str) -> str:
    return f"/qa/moderator/event/{event_id}/questions" if view == MODERATOR else f"/qa/event/{event_id}/questions"


def _time_ago(created_at: datetime) -> str:
    seconds = int((datetime.now(created_at.tzinfo) - created_at).total_seconds())
    if seconds >= 86400:
        return f"{seconds // 86400}d ago"
    if seconds >= 3600:
        return f"{seconds // 3600}h ago"
    if seconds >= 60:
        return f"{seconds // 60}m ago"
    return "just now"


def QuestionCard(question, show_admin_controls=False, user_liked=False):
    """A single question. Data attributes let the live script sort, count and patch cards."""
    question_id = str(question.id)
    likes = Span(str(question.likes_count), cls="ml-2", id=f"likes-{question_id}")

    if show_admin_controls:
        like_area = Div(I(cls="fas fa-heart text-error"), likes, cls="flex items-center gap-2")
    else:
        like_area = Button(
            I(cls="fas fa-heart"),
            likes,
            cls=f"btn btn-sm text-primary qa-like{' liked' if user_liked else ''}",
            hx_post=f"/qa/question/{question_id}/like",
            hx_target=f"#question-{question_id}",
            hx_swap="outerHTML",
            hx_disabled_elt="this",
            aria_pressed=str(user_liked).lower(),
            title="Like",
        )

    admin_controls = Div(
        Button(
            I(cls=f"fas fa-eye{'-slash' if question.is_visible else ''}"),
            cls="btn btn-sm btn-ghost",
            hx_post=f"/qa/moderator/question/{question_id}/toggle-visibility",
            hx_target=f"#question-{question_id}",
            hx_swap="outerHTML",
            title="Hide" if question.is_visible else "Approve (show to guests)"
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
    ) if show_admin_controls else None

    return Div(
        Div(
            Span(question.nickname, cls="font-semibold text-black"),
            Span(f" • {_time_ago(question.created_at)}", cls="text-sm text-base-content/60"),
            Span(I(cls="fas fa-check-circle text-success ml-2"), " Answered",
                 cls="text-sm text-success ml-2") if question.is_answered else None,
            Span(I(cls="fas fa-eye-slash text-warning ml-2"), " Pending approval",
                 cls="text-sm text-warning ml-2") if not question.is_visible and show_admin_controls else None,
            cls="mb-2"
        ),
        P(question.question_text, cls="mb-4 question-text text-black whitespace-pre-line"),
        Div(like_area, admin_controls, cls="flex justify-between items-center"),
        cls="timeline-box" + (" border-2 border-warning" if not question.is_visible and show_admin_controls else ""),
        style="padding: 16px;",
        id=f"question-{question_id}",
        data_question_id=question_id,
        data_likes=str(question.likes_count),
        data_created=question.created_at.isoformat(),
        data_visible=str(question.is_visible).lower(),
        data_answered=str(question.is_answered).lower(),
    )


def SessionStatusTag(is_active: bool, text_cls="text-sm", **kwargs):
    """Active / Inactive indicator for a session's Q&A"""
    color = "text-green" if is_active else "text-inactive"
    return Div(
        I(cls=f"fas fa-circle {color}"),
        P("Active" if is_active else "Inactive", cls=color),
        cls=f"{text_cls} flex items-center gap-2",
        **kwargs
    )


def SessionStatusToggle(event_id: int, is_active: bool):
    """Moderator button that opens or closes Q&A; swaps itself with the server's response"""
    color = 'var(--red)' if is_active else 'var(--green)'
    return Button(
        I(cls=f"fas {'fa-lock' if is_active else 'fa-unlock'} mr-2"),
        "Close Q&A" if is_active else "Open Q&A",
        cls="btn btn-sm self-start",
        style=f"background-color: {color}; border-color: {color}; color: white;",
        hx_post=f"/qa/moderator/event/{event_id}/toggle-qa",
        hx_target="this",
        hx_swap="outerHTML",
        hx_disabled_elt="this",
        id="qa-status",
        title=f"Click to {'close' if is_active else 'open'} Q&A"
    )


def QuestionForm(event_id: int, initial_nickname="", is_active=True, message=None):
    """Question submission form; disabled while the session's Q&A is closed"""
    disabled = not is_active
    return Div(
        Form(
            Div(
                Input(type="text", placeholder="Your nickname (optional)", name="nickname",
                      value=initial_nickname if initial_nickname != "Anonymous" else "",
                      maxlength="50", disabled=disabled, cls="input input-bordered rounded-sm w-full"),
                cls="form-control mb-4"
            ),
            Div(
                Textarea(name="question_text", placeholder="Type your question here...", required=True,
                         rows="3", maxlength="500", disabled=disabled,
                         cls="textarea textarea-bordered rounded-sm w-full", style="font-size: 1rem;"),
                cls="form-control mb-4"
            ),
            Div(
                Div(I(cls="fas fa-check-circle text-green text-lg"), P(message, cls="text-green font-semibold"),
                    cls="qa-flash flex flex-row gap-2 items-center") if message else Span(),
                Button("Submit", type="submit", disabled=disabled, cls="btn btn-primary px-6 py-2"),
                cls="flex flex-row items-center justify-between gap-4"
            ),
            hx_post=f"/qa/event/{event_id}/submit",
            hx_target="#question-form",
            hx_swap="outerHTML",
            hx_disabled_elt="find button[type=submit]",
        ),
        id="question-form",
        cls="px-6"
    )


def QuestionsListContainer(questions, show_admin_controls=False, user_likes=None, sort="popular"):
    """List of questions; `data-sort` tells the live script which tab is showing"""
    user_likes = user_likes or set()
    cards = [QuestionCard(q, show_admin_controls, str(q.id) in user_likes) for q in questions]
    empty = Div(
        I(cls="fas fa-comments text-4xl text-base-content/30 mb-4"),
        P("No questions yet. Be the first to ask!", cls="text-base-content/60"),
        cls="text-center py-12 qa-empty",
        style="display: none;" if cards else None,
    )
    return Div(
        empty, *cards,
        id="questions-list",
        data_sort=sort,
        style="height: 100%;",
        cls="blue-background p-4 flex flex-col gap-4 mb-8",
    )


def QuestionTabs(event_id: int, view: str, sort: str = "popular"):
    url = list_url(event_id, view)
    return Div(
        Div(
            *[A(name.title(), role="tab", id=f"{name}-tab",
                cls="tab" + (" tab-active" if name == sort else ""),
                hx_get=f"{url}?sort={name}", hx_target="#questions-list", hx_swap="outerHTML")
              for name in SORTS],
            role="tablist",
            cls="tabs tabs-lifted"
        ),
        cls="px-6"
    )


def ModeratorStats(questions):
    """Counts the live script keeps current from the cards on the page"""
    def stat(value, label, key, style=None):
        return Div(Span(str(value), cls="text-3xl font-bold", id=f"qa-stat-{key}"),
                   Span(label, cls="text-sm text-base-content/70"), cls="stat", style=style)
    return Div(
        Div(
            stat(len(questions), "Total Questions", "total"),
            stat(sum(q.is_visible for q in questions), "Visible", "visible", "color: #00A651;"),
            stat(sum(q.is_answered for q in questions), "Answered", "answered", "color: var(--primary-color);"),
            cls="stats shadow mb-6"
        ),
        cls="px-6"
    )


def QAPage(event: Event, questions, view: str, user_likes=None, nickname="", sort="popular"):
    """Q&A page body shared by guests and moderators; `#qa-live` configures the live script"""
    is_mod = view == MODERATOR
    header = Div(
        A(I(cls="fas fa-eye mr-2"), "Guest View", href=f"/qa/event/{event.id}",
          cls="btn btn-sm btn-primary self-start", target="_blank") if is_mod else None,
        H1(event.title, cls="text-lg font-bold"),
        Div(
            I(cls="far fa-clock text-base-content/70"),
            P(event.start_time.strftime("%I:%M %p"), " • ", event.location or "TBA", cls="text-base-content/70"),
            cls="flex items-center gap-2",
        ),
        SessionStatusToggle(event.id, event.is_qa_active) if is_mod else SessionStatusTag(event.is_qa_active, id="qa-status"),
        cls="flex flex-col gap-2 px-6 mb-4"
    )
    return Div(
        header,
        ModeratorStats(questions) if is_mod else QuestionForm(event.id, nickname, event.is_qa_active),
        QuestionTabs(event.id, view, sort),
        QuestionsListContainer(questions, show_admin_controls=is_mod, user_likes=user_likes, sort=sort),
        id="qa-live",
        data_event_id=str(event.id),
        data_view=view,
        data_list_url=list_url(event.id, view),
    )


def SessionCard(event: Event, is_moderator: bool = False):
    """Session card linking to the guest or moderator Q&A page"""
    card_class = "timeline-box p-6 flex flex-col justify-evenly"
    if event.is_qa_active:
        card_class += " border-2 border-primary"

    return A(
        Div(
            Div(
                Div(
                    H3(event.title, cls="text-base font-medium"),
                    SessionStatusTag(event.is_qa_active, text_cls="text-xs"),
                    cls="flex justify-between gap-4 items-start"
                ),
                P(
                    I(cls="far fa-clock mr-2"),
                    event.start_time.strftime("%I:%M %p"),
                    " • ",
                    event.location or "TBA",
                    cls="text-sm text-base-content/70 mt-2"
                ),
            ),
            cls=card_class
        ),
        href=f"/qa/moderator/event/{event.id}" if is_moderator else f"/qa/event/{event.id}"
    )
