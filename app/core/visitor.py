"""Anonymous visitor identity: one first-party cookie, assigned once and readable from any route.
Used to remember likes and feedback submissions without accounts."""
import uuid
from starlette.requests import HTTPConnection

COOKIE_NAME = 'qa_session_id'  # existing name, so likes from earlier visits still match
MAX_AGE = 60 * 60 * 24 * 365


class VisitorMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)

        existing = HTTPConnection(scope).cookies.get(COOKIE_NAME)
        scope.setdefault('state', {})['visitor_id'] = existing or str(uuid.uuid4())
        if existing:
            return await self.app(scope, receive, send)

        cookie = f"{COOKIE_NAME}={scope['state']['visitor_id']}; Path=/; Max-Age={MAX_AGE}; HttpOnly; SameSite=Lax".encode()

        async def send_with_cookie(message):
            if message['type'] == 'http.response.start':
                message = {**message, 'headers': [*message.get('headers', []), (b'set-cookie', cookie)]}
            await send(message)

        return await self.app(scope, receive, send_with_cookie)


def visitor_id(request) -> str:
    """The visitor's id for this request (assigned by VisitorMiddleware)"""
    return request.state.visitor_id
