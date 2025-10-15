from components.titled import CustomTitled
from components.navigation import BottomNav
from fasthtml.components import Div, Html
from .login_modal import LoginModal
from fasthtml.components import Button, Span, A
from .icon import Icon

def AppContainer(content: Div, active_button_index: int = None, is_moderator: bool = False, request=None) -> Div:
    """
    Main app container with auth indicator in top-right corner
    
    Args:
        content: Page content
        active_button_index: Active nav button (0-5)
        is_moderator: Whether user is authenticated moderator
        request: FastHTML request object to detect route
    """
    # Determine if we should show login UI
    show_login = False
    if request:
        path = request.url.path
        show_login = path == '/' or path.startswith('/qa') or path.startswith('/feedback')
    
    # Auth button/link in top-right corner (only on home and qa routes)
    auth_element = None
    if show_login:
        if is_moderator:
            auth_element = Div(
                Span(
                    Icon('shield-alt', cls='mr-2'),
                    "Moderator",
                    cls="badge badge-secondary mr-2"
                ),
                A(
                    Icon('sign-out-alt', cls='mr-1'),
                    "Logout",
                    href="/admin/logout",
                    cls="btn btn-error btn-sm"
                ),
                cls="flex items-center gap-2"
            )
        else:
            auth_element = Button(
                Div(
                    Icon('user-circle', cls='text-2xl'),
                    cls="tooltip tooltip-bottom",
                    data_tip="Admin Login"
                ),
                onclick="document.getElementById('login-modal').showModal()",
                cls="btn btn-circle btn-sm btn-accent"
            )
    
    return CustomTitled(
        'MAS CYP Conference 2024',
        Html(data_theme='cupcake'),
        
        # Fixed position auth indicator (only show if needed)
        Div(
            auth_element,
            cls="fixed top-4 right-4 z-50"
        ) if auth_element else Div(),
        
        # Login modal (only show if not logged in and on allowed routes)
        LoginModal() if (show_login and not is_moderator) else Div(),
        
        content,
        BottomNav(active_button_index),
    )