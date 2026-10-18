from fasthtml.common import *

def FeedbackMessage(
    title: str,
    message: str,
    button_text: str,
    button_href: str,
    icon_class: str = None,
    icon_color: str = "text-primary"
):
    """Reusable message card (closed pages, thank-you notes), centred in the space below the top nav.
    Place it inside MessageScreen so it fills the page. Styles: .message-* in assets/theme-26.css"""
    return Div(
        Div(
            I(cls=f"{icon_class} {icon_color} message-icon") if icon_class else None,
            H2(title, cls="message-title"),
            P(message, cls="message-text"),
            A(button_text, href=button_href, cls="btn btn-glass btn-primary"),
            cls="message-card"
        ),
        cls="message-page"
    )


def MessageScreen(*children):
    """Page body for a FeedbackMessage: the app background, with the card centred under the top nav"""
    return Div(*children, id='page-content', cls='message-screen')
