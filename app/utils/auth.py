from passlib.context import CryptContext
from fasthtml.common import RedirectResponse
from functools import wraps
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from db.models import User
from datetime import datetime, date
from zoneinfo import ZoneInfo
import os

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

def is_moderator(sess):
    """Check if user is a moderator"""
    return sess.get('admin_auth', False)

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
        result = result.where(User.role == 'admin')
    
    result = await db.execute(result)
    return result.scalar_one_or_none()

def is_conference_day():
    """Check if current date is conference day (Oct 18, 2025 CDT)"""
    # Allow bypass for testing
    if os.getenv('ENVIRONMENT') != 'development':
        return True
    
    cdt = ZoneInfo('America/Chicago')
    current_date = datetime.now(cdt).date()
    conference_date = date(2025, 10, 18)
    return current_date == conference_date

def require_conference_day(f):
    """Decorator to require access only on conference day"""
    @wraps(f)
    async def async_wrapper(req, sess, *args, **kwargs):
        if not is_conference_day():
            # Calculate time until conference
            from fasthtml.components import Div
            from components.page import AppContainer
            from components.feedback_message import FeedbackMessage
            from components.navigation import TopNav
            
            cdt = ZoneInfo('America/Chicago')
            now = datetime.now(cdt)
            conference_datetime = datetime(2025, 10, 18, 0, 0, 0, tzinfo=cdt)
            time_delta = conference_datetime - now
            
            # Calculate days and hours
            total_hours = int(time_delta.total_seconds() / 3600)
            days = total_hours // 24
            hours = total_hours % 24
            
            # Build the time message
            if days > 0 and hours > 0:
                time_msg = f"That's {days} day{'s' if days > 1 else ''} and {hours} hour{'s' if hours != 1 else ''} away."
            elif days > 0:
                time_msg = f"That's {days} day{'s' if days > 1 else ''} away."
            elif hours > 0:
                time_msg = f"That's {hours} hour{'s' if hours != 1 else ''} away."
            else:
                time_msg = "The conference starts very soon!"
            
            return AppContainer(
                Div(
                    TopNav('Coming Soon'),
                    FeedbackMessage(
                        icon_class="fas fa-calendar-day text-primary",
                        title="See You Soon!",
                        message=f"Available on conference day. {time_msg}",
                        button_text="Return to Home",
                        button_href="/",
                        icon_color="text-primary"
                    ),
                ),
                is_moderator=False,
                request=req
            )
        
        if asyncio.iscoroutinefunction(f):
            return await f(req, sess, *args, **kwargs)
        else:
            return f(req, sess, *args, **kwargs)
    
    return async_wrapper