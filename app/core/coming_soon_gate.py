from pathlib import PurePosixPath
from starlette.requests import HTTPConnection

PREVIEW_SUFFIX = '-26'
PREVIEW_COOKIE = 'preview_26'
PREVIEW_MAX_AGE = 60 * 60 * 24 * 60  # 60 days
COMING_SOON_PATH = '/coming-soon'

# Static files must stay reachable so the coming soon page can load its assets
STATIC_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.css', '.js', '.map', '.woff', '.woff2', '.ttf', '.otf',
}


def _is_static(path: str) -> bool:
    return path.startswith('/assets/') or PurePosixPath(path).suffix.lower() in STATIC_EXTS


class ComingSoonGate:
    """
    Serve the coming soon page for every request, except:
    - static assets and the coming soon page itself
    - any URL ending in "-26": the suffix is stripped (/agenda-26 -> /agenda, /-26 -> /)
      and a preview cookie is set so normal in-app links keep working afterwards
    - requests that already carry the preview cookie
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] not in ('http', 'websocket'):
            return await self.app(scope, receive, send)

        path = scope['path']

        if path.endswith(PREVIEW_SUFFIX):
            real_path = path[:-len(PREVIEW_SUFFIX)] or '/'
            scope = {**scope, 'path': real_path, 'raw_path': real_path.encode()}
            return await self.app(scope, receive, self._with_preview_cookie(send))

        if (
            path == COMING_SOON_PATH
            or _is_static(path)
            or HTTPConnection(scope).cookies.get(PREVIEW_COOKIE) == '1'
        ):
            return await self.app(scope, receive, send)

        if scope['type'] == 'websocket':
            return await send({'type': 'websocket.close', 'code': 1008})

        scope = {**scope, 'path': COMING_SOON_PATH, 'raw_path': COMING_SOON_PATH.encode(), 'method': 'GET', 'query_string': b''}
        return await self.app(scope, receive, send)

    @staticmethod
    def _with_preview_cookie(send):
        cookie = f'{PREVIEW_COOKIE}=1; Path=/; Max-Age={PREVIEW_MAX_AGE}; HttpOnly; SameSite=Lax'.encode()

        async def wrapped(message):
            if message['type'] == 'http.response.start':
                message = {**message, 'headers': [*message.get('headers', []), (b'set-cookie', cookie)]}
            await send(message)
        return wrapped
