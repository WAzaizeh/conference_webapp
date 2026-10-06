"""Live Q&A updates.

Routes call `publish()` after changing data; `stream()` feeds one browser's Server-Sent Events
connection. Messages cross Cloud Run instances through Postgres (see bus.py) and are rendered once
per instance (see render.py).
"""
import asyncio
from typing import Optional

from .bus import PostgresBus
from .hub import GUEST, MODERATOR, VIEWS, LocalHub
from .render import CREATED, DELETED, LIKED, STATUS, UPDATED, Renderer, sse

KEEPALIVE_SECONDS = 15
RECONNECT_MS = 3000

hub = LocalHub()
_renderer = Renderer(hub)
_bus = PostgresBus(_renderer.handle, has_subscribers=lambda: hub.count() > 0)


async def publish(event_id: int, action: str, question_id: Optional[str] = None, **extra):
    """Announce a change to every connected browser on every instance"""
    payload = {'event_id': event_id, 'action': action, **extra}
    if question_id is not None:
        payload['question_id'] = str(question_id)
    await _bus.publish(payload)


async def stream(event_id: int, view: str):
    """Async generator of SSE text for one browser connection"""
    queue = hub.add(event_id, view)
    try:
        _bus.ensure_running()
        await _bus.wait_ready()
        yield f'retry: {RECONNECT_MS}\n\n'
        yield sse('connected', {})  # the browser re-syncs its list on every (re)connect
        while True:
            try:
                message = await asyncio.wait_for(queue.get(), KEEPALIVE_SECONDS)
            except asyncio.TimeoutError:
                yield ': keepalive\n\n'
                continue
            if message is None:  # dropped as too slow; the browser reconnects
                return
            yield message
    finally:
        hub.remove(event_id, view, queue)


__all__ = ['publish', 'stream', 'GUEST', 'MODERATOR', 'VIEWS',
           'CREATED', 'UPDATED', 'DELETED', 'LIKED', 'STATUS']
