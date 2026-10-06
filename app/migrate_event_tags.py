"""Add events.tags and fill it from the old events.category (+ title for tracks and keynotes).
Safe to re-run: only sessions with no tags are filled. The category column is kept, unused.
Usage: python migrate_event_tags.py [--apply]   (dry run without --apply)
"""
import asyncio
import json
import sys
from urllib.parse import urlparse

from sqlalchemy import text

from db.connection import db_manager
from utils.tags import tags_from_category

APPLY = '--apply' in sys.argv


async def main():
    print(f'target database: {urlparse(db_manager.database_url).hostname}')
    async with db_manager.engine.begin() as conn:
        columns = set((await conn.execute(text(
            "SELECT column_name FROM information_schema.columns WHERE table_name = 'events'"))).scalars())
        print('add column events.tags' if 'tags' not in columns else 'events.tags already exists')
        if 'tags' not in columns and APPLY:
            await conn.execute(text("ALTER TABLE events ADD COLUMN tags JSON NOT NULL DEFAULT '[]'"))

        if 'category' not in columns:
            print('no category column to convert')
        else:
            has_tags = 'tags' in columns or APPLY
            query = 'SELECT id, title, category FROM events' + (" WHERE tags::text = '[]'" if has_tags else '')
            rows = (await conn.execute(text(query + ' ORDER BY start_time'))).all()
            for row in rows:
                tags = tags_from_category(row.category, row.title)
                print(f'  {row.id:>4} {row.category or "":<16} -> {tags}  {row.title[:60]}')
                if APPLY:
                    await conn.execute(text('UPDATE events SET tags = CAST(:tags AS JSON) WHERE id = :id'),
                                       {'tags': json.dumps(tags), 'id': row.id})

        if not APPLY:
            print('dry run only (pass --apply to write)')
            await conn.rollback()


asyncio.run(main())
