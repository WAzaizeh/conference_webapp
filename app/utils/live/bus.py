"""Cross-instance messaging over Postgres LISTEN/NOTIFY.

publish() sends a small JSON notification through the normal (pooled) connection. Each app instance
that has live subscribers keeps one LISTEN connection on the direct endpoint (Neon's pooler does
not support LISTEN) and hands every notification, in order, to `on_message`. The listener starts
with the first subscriber and stops after IDLE_SECONDS without any, so the database can sleep.
"""
import asyncio
import json
import logging
import os
from urllib.parse import urlparse

import asyncpg
from sqlalchemy import text

from db.connection import db_manager

CHANNEL = 'qa_live'
IDLE_SECONDS = 60
CHECK_INTERVAL = 5
MAX_BACKOFF = 30

log = logging.getLogger(__name__)


def direct_dsn() -> str:
    """asyncpg DSN for LISTEN: DATABASE_URL_DIRECT, else the app's URL with Neon's '-pooler' removed"""
    url = os.getenv('DATABASE_URL_DIRECT') or db_manager.database_url
    url = url.replace('postgresql+asyncpg://', 'postgresql://', 1)
    host = urlparse(url).hostname or ''
    return url.replace(host, host.replace('-pooler', ''), 1)


class PostgresBus:
    def __init__(self, on_message, has_subscribers):
        self._on_message = on_message            # async callable(payload: dict)
        self._has_subscribers = has_subscribers  # callable() -> bool
        self._inbox: asyncio.Queue = asyncio.Queue()
        self._task = None
        self._ready = asyncio.Event()            # set while LISTEN is active on this instance

    async def publish(self, payload: dict):
        notified = False
        try:
            async with db_manager.engine.begin() as conn:
                await conn.execute(text('SELECT pg_notify(:channel, :payload)'),
                                   {'channel': CHANNEL, 'payload': json.dumps(payload, separators=(',', ':'))})
            notified = True
        except Exception:
            log.exception('live: NOTIFY failed')
        # Without an active listener here, local subscribers would miss it: deliver directly.
        # Messages are idempotent, so a rare double delivery is harmless.
        if not (notified and self._ready.is_set()):
            await self._on_message(payload)

    def ensure_running(self):
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())

    async def wait_ready(self, timeout: float = 5):
        try:
            await asyncio.wait_for(self._ready.wait(), timeout)
        except asyncio.TimeoutError:
            log.warning('live: listener not ready; using local delivery only')

    def _notified(self, _connection, _pid, _channel, payload):  # asyncpg listener signature
        self._inbox.put_nowait(payload)

    async def _consume(self):
        while True:
            payload = await self._inbox.get()
            try:
                await self._on_message(json.loads(payload))
            except Exception:
                log.exception('live: failed to handle %s', payload)

    async def _run(self):
        consumer = asyncio.create_task(self._consume())
        backoff = 1
        try:
            while self._has_subscribers():
                conn = None
                try:
                    conn = await asyncpg.connect(direct_dsn(), timeout=10)
                    await conn.add_listener(CHANNEL, self._notified)
                    self._ready.set()
                    backoff = 1
                    if await self._listen_until_idle(conn):
                        return
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    log.warning('live: listener error (%s); retrying in %ss', exc, backoff)
                finally:
                    self._ready.clear()
                    if conn is not None and not conn.is_closed():
                        await conn.close()
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, MAX_BACKOFF)
        finally:
            consumer.cancel()

    async def _listen_until_idle(self, conn) -> bool:
        """Returns True when idle long enough to stop, False if the connection dropped"""
        idle = 0
        while not conn.is_closed():
            await asyncio.sleep(CHECK_INTERVAL)
            idle = 0 if self._has_subscribers() else idle + CHECK_INTERVAL
            if idle >= IDLE_SECONDS:
                return True
        return False
