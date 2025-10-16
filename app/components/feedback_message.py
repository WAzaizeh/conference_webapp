from fasthtml.common import *

def FeedbackMessage(
    title: str,
    message: str,
    button_text: str,
    button_href: str,
    icon_class: str = None,
    icon_color: str = "text-primary"
):
    """Reusable feedback message component"""
    btnclass = "btn btn-primary px-6 py-2"
    btnstyle = "background-color: var(--primary-color); border-color: var(--primary-color); color: white;"
    return Div(
        Div(
            Div(
                I(cls=f"{icon_class} text-6xl {icon_color} mb-4") if icon_class else None,
                H2(title, cls="text-3xl font-bold mb-4 text-primary"),
                P(message, cls="text-lg mb-6 text-center text-black"),
                Div(
                    A(
                        button_text,
                        href=button_href,
                        cls=btnclass,
                        style=btnstyle
                    ),
                    cls="flex justify-center"
                ),
                cls="text-center"
            ),
        ),
        cls="container min-h-screen flex items-center"
    )