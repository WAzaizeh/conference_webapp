from pathlib import PurePosixPath

COMING_SOON_PATH = '/coming-soon'

# Static files must stay reachable so the coming soon page can load its assets
STATIC_EXTS = {
    '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.webp',
    '.css', '.js', '.map', '.woff', '.woff2', '.ttf', '.otf',
}


def _is_static(path: str) -> bool:
    return path.startswith('/assets/') or PurePosixPath(path).suffix.lower() in STATIC_EXTS


class ComingSoonGate:
    """Serve the coming soon page for every request except static assets."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] not in ('http', 'websocket'):
            return await self.app(scope, receive, send)

        path = scope['path']
        if path == COMING_SOON_PATH or _is_static(path):
            return await self.app(scope, receive, send)

        if scope['type'] == 'websocket':
            return await send({'type': 'websocket.close', 'code': 1008})

        scope = {**scope, 'path': COMING_SOON_PATH, 'raw_path': COMING_SOON_PATH.encode(), 'method': 'GET', 'query_string': b''}
        return await self.app(scope, receive, send)
