from passlib.context import CryptContext
from fasthtml.common import RedirectResponse
from functools import wraps

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
    async def wrapper(req, sess, *args, **kwargs):
        if not is_moderator(sess):
            return admin_login_redir(req.url.path)
        return await f(req, sess, *args, **kwargs)
    return wrapper