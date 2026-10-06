"""Subscribers connected to this app instance, grouped by Q&A session and view."""
import asyncio
from collections import defaultdict
from typing import Dict, Set, Tuple

from components.qa import GUEST, MODERATOR  # view names are defined once, with the Q&A components
VIEWS = (GUEST, MODERATOR)

Key = Tuple[int, str]


class LocalHub:
    def __init__(self):
        self._subscribers: Dict[Key, Set[asyncio.Queue]] = defaultdict(set)

    def add(self, event_id: int, view: str) -> asyncio.Queue:
        queue = asyncio.Queue(maxsize=100)
        self._subscribers[(event_id, view)].add(queue)
        return queue

    def remove(self, event_id: int, view: str, queue: asyncio.Queue):
        subscribers = self._subscribers.get((event_id, view))
        if subscribers is not None:
            subscribers.discard(queue)
            if not subscribers:
                del self._subscribers[(event_id, view)]

    def count(self) -> int:
        return sum(len(s) for s in self._subscribers.values())

    def views(self, event_id: int) -> Set[str]:
        """Views with at least one subscriber for this session on this instance"""
        return {view for (eid, view) in self._subscribers if eid == event_id}

    def deliver(self, event_id: int, view: str, message: str):
        """Queue a formatted SSE message for every matching subscriber"""
        for queue in list(self._subscribers.get((event_id, view), ())):
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                self._drop(event_id, view, queue)

    def _drop(self, event_id: int, view: str, queue: asyncio.Queue):
        """A subscriber 100 messages behind: end its stream (None) so the browser reconnects and re-syncs"""
        self.remove(event_id, view, queue)
        while not queue.empty():
            queue.get_nowait()
        queue.put_nowait(None)
