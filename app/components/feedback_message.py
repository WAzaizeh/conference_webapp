from fasthtml.common import *

def FeedbackMessage(
    icon_class: str,
    title: str,
    message: str,
    button_text: str,
    button_href: str,
    icon_color: str = "text-primary"
):
    """Reusable feedback message component"""
    return Div(
        Div(
            Div(
                I(cls=f"{icon_class} text-6xl {icon_color} mb-4"),
                H2(title, cls="text-3xl font-bold mb-4"),
                P(message, cls="text-lg mb-6 text-center"),
                Div(
                    A(
                        button_text,
                        href=button_href,
                        cls="btn btn-primary"
                    ),
                    cls="flex justify-center"
                ),
                cls="text-center"
            ),
            cls="card bg-base-100 shadow-xl p-8 max-w-md mx-auto"
        ),
        cls="container mx-auto px-4 py-16 min-h-screen flex items-center"
    )