from passlib.context import CryptContext
from fasthtml.common import RedirectResponse
from functools import wraps
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from db.models import User
from core import conference

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Status code 303 is a redirect that can change POST to GET,
# so it's appropriate for a login page.
def admin_login_redir(to='/'): 
    return RedirectResponse('/admin_login?redir=' + to, status_code=303)

def hash_password(password: str) -> str:
    """Hash a password for storing."""
    # Ensure password is a string and truncate if needed (bcrypt limit is 72 bytes)
    if isinstance(password, str):
        password = password.encode('utf-8')[:72].decode('utf-8')
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against one provided by user."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        print(f"Password verification error: {e}")
        return False

ADMIN_ROLE = 'admin'  # may edit the agenda; any other active account (e.g. 'moderator') moderates only


def log_in(sess, user):
    sess['admin_auth'] = True
    sess['user_id'] = str(user.id)
    sess['role'] = user.role


def log_out(sess):
    for key in ('admin_auth', 'user_id', 'role'):
        sess.pop(key, None)


def is_moderator(sess):
    """Logged in with any staff account"""
    return sess.get('admin_auth', False)


def is_admin(sess):
    """Logged in with an admin account"""
    return is_moderator(sess) and sess.get('role') == ADMIN_ROLE

def require_moderator(f):
    """Decorator to require moderator authentication"""
    @wraps(f)
    async def async_wrapper(req, sess, *args, **kwargs):
        if not is_moderator(sess):
            return admin_login_redir(req.url.path)
        
        if asyncio.iscoroutinefunction(f):
            return await f(req, sess, *args, **kwargs)
        else:
            return f(req, sess, *args, **kwargs)
    
    return async_wrapper


def require_admin(f):
    """Decorator: admins only; other staff see a message, visitors go to the login page"""
    @wraps(f)
    async def wrapper(req, sess, *args, **kwargs):
        if not is_moderator(sess):
            return admin_login_redir(req.url.path)
        if not is_admin(sess):
            return _message_page(req, 'Admins Only', 'Admins only', 'Only admin accounts can change the agenda.', 'fa-lock')
        result = f(req, sess, *args, **kwargs)
        return await result if asyncio.iscoroutine(result) else result
    return wrapper

async def get_user_by_email(db: AsyncSession, email: str, require_admin: bool = False) -> Optional[User]:
    """
    Get user by email address
    
    Args:
        db: Async database session
        email: User's email address
        require_admin: If True, only return admin users

    Returns:
        User object if found and active, None otherwise
    """
    result = select(User).where(
            User.email == email,
            User.is_active == True
        )

    # Add role filter only if require_admin is True
    if require_admin:
        result = result.where(User.role == ADMIN_ROLE)
    
    result = await db.execute(result)
    return result.scalar_one_or_none()

def _message_page(req, nav_title: str, title: str, message: str, icon: str):
    """Full page with a short message and a link home (closed windows, missing permissions)"""
    from fasthtml.components import Div
    from components.page import AppContainer
    from components.feedback_message import FeedbackMessage, MessageScreen
    from components.navigation import TopNav

    return AppContainer(
        MessageScreen(
            TopNav(nav_title),
            FeedbackMessage(
                icon_class=f"fas {icon} text-primary",
                title=title,
                message=message,
                button_text="Return to Home",
                button_href="/",
                icon_color="text-primary"
            ),
        ),
        is_moderator=False,
        request=req
    )


def _closed_page(req, title: str, message: str):
    """Shown when a date-limited page is accessed outside its window"""
    heading = "See You Soon!" if conference.now() < conference.INTERACTIVE_OPENS else "Thank You!"
    return _message_page(req, title, heading, message, 'fa-calendar-day')


def _time_until_start() -> str:
    hours = max(0, int((conference.INTERACTIVE_OPENS - conference.now()).total_seconds() // 3600))
    days, hours = divmod(hours, 24)
    parts = [f"{n} {unit}{'s' if n != 1 else ''}" for n, unit in ((days, 'day'), (hours, 'hour')) if n]
    return f"That's {' and '.join(parts)} away." if parts else "Opening very soon!"


def require_window(is_open, title: str, closed_message: str):
    """Decorator factory: serve the route only while `is_open()` is true.
    Arguments are passed through untouched; FastHTML supplies the request first."""
    def decorator(f):
        @wraps(f)
        async def wrapper(*args, **kwargs):
            if not is_open():
                if conference.now() < conference.INTERACTIVE_OPENS:
                    message = f"Available on conference day. {_time_until_start()}"
                else:
                    message = closed_message
                return _closed_page(args[0] if args else None, title, message)
            result = f(*args, **kwargs)
            return await result if asyncio.iscoroutine(result) else result
        return wrapper
    return decorator


# Kept for existing call sites; both are unrestricted off production (see conference.RESTRICT_DATES)
is_conference_day = conference.is_conference_day
require_conference_day = require_window(conference.is_conference_day, 'Coming Soon', 'Q&A has closed for this year.')
require_feedback_window = require_window(conference.is_feedback_open, 'Feedback', 'The feedback survey has closed.')
