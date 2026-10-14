"""Copy the conference content (sessions, speakers, sponsors, prayer times) from the dev database to production.
Dev is where the program is prepared and edited; this makes prod match it exactly, keeping the same ids.

Production's content tables are replaced, so anything only on prod is removed — including Q&A questions
(and their likes) on prod sessions, which are deleted with their session. Accounts, logins and feedback
are not touched. Missing tables and columns are added to prod first, so an older prod schema is fine.
Every replaced row is saved to backups/prod_<timestamp>.json before anything is written.

Usage (dry run without --apply):
    DEV_DATABASE_URL=... PROD_DATABASE_URL=... python sync_prod_from_dev.py [--apply]
"""
import asyncio
import json
import sys
from datetime import datetime
from os import getenv
from pathlib import Path
from urllib.parse import urlparse

from sqlalchemy import select, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import create_async_engine

from db.models import Base

APPLY = '--apply' in sys.argv
BACKUP_DIR = Path(__file__).parent / 'backups'

# Copied in this order (parents first) and cleared in reverse
CONTENT_TABLES = ['speakers', 'sponsors', 'prayer_times', 'events', 'event_speakers']
# Rows on prod that go away with its sessions; backed up, never copied
CASCADED_TABLES = ['questions', 'question_likes']


def engine_for(var):
    url = getenv(var)
    if not url:
        sys.exit(f'{var} is not set')
    return create_async_engine(url.replace('postgresql://', 'postgresql+asyncpg://'))


async def columns_of(conn, table):
    """column name -> is_nullable for an existing table on the connected database"""
    rows = await conn.execute(text(
        'SELECT column_name, is_nullable, column_default FROM information_schema.columns WHERE table_name = :t'),
        {'t': table})
    return {r.column_name: (r.is_nullable == 'YES' or r.column_default is not None) for r in rows}


async def align_schema(conn):
    """Create missing tables, add missing columns, and relax NOT NULL on prod-only columns we won't fill"""
    await conn.run_sync(Base.metadata.create_all)
    for name in CONTENT_TABLES:
        table = Base.metadata.tables[name]
        existing = await columns_of(conn, name)
        for col in table.columns:
            if col.name not in existing:
                col_type = col.type.compile(dialect=postgresql.dialect())
                print(f'  add column {name}.{col.name} {col_type}')
                await conn.execute(text(f'ALTER TABLE {name} ADD COLUMN {col.name} {col_type}'))
        for extra, nullable_or_default in existing.items():
            if extra not in table.columns and not nullable_or_default:
                print(f'  allow NULL in prod-only column {name}.{extra}')
                await conn.execute(text(f'ALTER TABLE {name} ALTER COLUMN {extra} DROP NOT NULL'))


async def read_all(conn, table):
    return [dict(r._mapping) for r in await conn.execute(text(f'SELECT * FROM {table}'))]


async def main():
    dev, prod = engine_for('DEV_DATABASE_URL'), engine_for('PROD_DATABASE_URL')
    print(f'from dev:  {dev.url.host}\nto prod:   {prod.url.host}')
    if dev.url.host == prod.url.host and dev.url.database == prod.url.database:
        sys.exit('DEV_DATABASE_URL and PROD_DATABASE_URL point at the same database')

    async with dev.connect() as conn:
        rows = {name: [dict(r._mapping) for r in await conn.execute(select(Base.metadata.tables[name]))]
                for name in CONTENT_TABLES}

    async with prod.begin() as conn:
        existing_tables = set((await conn.execute(text(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))).scalars())
        backup = {name: await read_all(conn, name)
                  for name in CONTENT_TABLES + CASCADED_TABLES if name in existing_tables}

        print('\n  table             prod now -> after')
        for name in CONTENT_TABLES:
            print(f'  {name:<16} {len(backup.get(name, [])):>9} -> {len(rows[name])}')
        for name in CASCADED_TABLES:
            print(f'  {name:<16} {len(backup.get(name, [])):>9} -> 0  (deleted with prod sessions)')

        if not APPLY:
            print('\nschema changes needed on prod:')
            await align_schema(conn)
            await conn.rollback()
            print('dry run only (pass --apply to write)')
            return

        BACKUP_DIR.mkdir(exist_ok=True)
        backup_file = BACKUP_DIR / f'prod_{datetime.now():%Y%m%d_%H%M%S}.json'
        backup_file.write_text(json.dumps(backup, default=str, indent=1))
        print(f'\nbacked up prod rows to {backup_file}')

        await align_schema(conn)
        for name in reversed(CONTENT_TABLES):
            await conn.execute(text(f'DELETE FROM {name}'))  # events cascade to questions and likes
        for name in CONTENT_TABLES:
            if rows[name]:
                await conn.execute(Base.metadata.tables[name].insert(), rows[name])
            if 'id' in Base.metadata.tables[name].columns:
                # New rows made on prod (e.g. in /admin/agenda) continue after the copied ids
                await conn.execute(text(
                    f"SELECT setval(pg_get_serial_sequence('{name}', 'id'), COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {name}"))
        print('prod now matches dev')

    await dev.dispose()
    await prod.dispose()


if __name__ == '__main__':
    asyncio.run(main())
