"""Turns bus notifications into SSE messages for this instance's subscribers.

Each notification is rendered at most once per instance and view, then fanned out locally, so a
moderator approving a question costs one database read per instance instead of one per phone.
"""
import asyncio
import json
from fasthtml.common import to_xml

from components.qa import QuestionCard, SessionStatusTag, SessionStatusToggle
from crud.question import get_question
from db.connection import db_manager
from .hub import GUEST, MODERATOR, LocalHub

# Actions published by routes
CREATED, UPDATED, DELETED, LIKED, STATUS = 'created', 'updated', 'deleted', 'liked', 'status'

LIKE_BATCH_SECONDS = 1.0


def sse(name: str, data: dict) -> str:
    return f"event: {name}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n"


class Renderer:
    def __init__(self, hub: LocalHub):
        self.hub = hub
        self._pending_likes = {}   # event_id -> {question_id: likes}
        self._flushes = {}         # event_id -> scheduled flush task

    async def handle(self, payload: dict):
        event_id, action = payload['event_id'], payload['action']
        views = self.hub.views(event_id)
        if not views:
            return

        if action == LIKED:
            self._batch_like(event_id, payload['question_id'], payload['likes'])
        elif action == DELETED:
            self._send(event_id, views, 'remove', {'id': payload['question_id']})
        elif action == STATUS:
            self._send_status(event_id, views, payload['active'])
        elif action in (CREATED, UPDATED):
            await self._send_question(event_id, views, action, payload['question_id'])

    def _send(self, event_id: int, views, name: str, data: dict):
        message = sse(name, data)
        for view in views:
            self.hub.deliver(event_id, view, message)

    async def _send_question(self, event_id: int, views, action: str, question_id: str):
        async with db_manager.AsyncSessionLocal() as db:
            question = await get_question(db, question_id)
        if question is None:
            self._send(event_id, views, 'remove', {'id': question_id})
            return

        if MODERATOR in views:
            card = to_xml(QuestionCard(question, show_admin_controls=True))
            self.hub.deliver(event_id, MODERATOR, sse('card', {'id': question_id, 'html': card}))

        # Guests never see unapproved questions; newly created ones are always unapproved
        if GUEST in views and action == UPDATED:
            if question.is_visible:
                card = to_xml(QuestionCard(question, show_admin_controls=False))
                self.hub.deliver(event_id, GUEST, sse('card', {'id': question_id, 'html': card}))
            else:
                self.hub.deliver(event_id, GUEST, sse('remove', {'id': question_id}))

    def _send_status(self, event_id: int, views, active: bool):
        if GUEST in views:
            tag = to_xml(SessionStatusTag(active, id='qa-status'))
            self.hub.deliver(event_id, GUEST, sse('status', {'active': active, 'html': tag}))
        if MODERATOR in views:
            toggle = to_xml(SessionStatusToggle(event_id, active))
            self.hub.deliver(event_id, MODERATOR, sse('status', {'active': active, 'html': toggle}))

    def _batch_like(self, event_id: int, question_id: str, likes: int):
        """Collect like counts for a second, then send only the latest count per question"""
        self._pending_likes.setdefault(event_id, {})[question_id] = likes
        if event_id not in self._flushes:
            self._flushes[event_id] = asyncio.create_task(self._flush_likes(event_id))

    async def _flush_likes(self, event_id: int):
        await asyncio.sleep(LIKE_BATCH_SECONDS)
        self._flushes.pop(event_id, None)
        counts = self._pending_likes.pop(event_id, {})
        views = self.hub.views(event_id)
        for question_id, likes in counts.items():
            self._send(event_id, views, 'likes', {'id': question_id, 'likes': likes})
