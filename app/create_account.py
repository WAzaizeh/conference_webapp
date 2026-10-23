"""Create a staff account. The password is read from standard input, so it can be piped from a password
manager without appearing on screen or in shell history, e.g.:
    op read "op://Private/MAS CYP - yasmeen/password" | python create_account.py yasmeen --role moderator \\
        --expires 2026-10-25T02:00 --apply
--expires is Dallas time; leave it out for an account that never expires (admins).
Prints the target database and does a dry run unless --apply is given. Existing usernames are left alone.
"""
import argparse
import asyncio
import sys
from datetime import datetime

from sqlalchemy import select

from core.conference import CONFERENCE_TZ
from db.connection import db_manager
from db.models import User
from utils.auth import ADMIN_ROLE, hash_password


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('username')
    parser.add_argument('--role', choices=[ADMIN_ROLE, 'moderator'], required=True)
    parser.add_argument('--expires', help='Dallas time, e.g. 2026-10-25T02:00')
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()

    expires_at = datetime.fromisoformat(args.expires).replace(tzinfo=CONFERENCE_TZ) if args.expires else None
    password = sys.stdin.readline().rstrip('\n')
    if len(password) < 12:
        sys.exit('refusing: the password read from standard input is shorter than 12 characters')

    print(f'target database: {db_manager.engine.url.host}')
    async with db_manager.AsyncSessionLocal() as db:
        if (await db.execute(select(User).where(User.email == args.username))).scalar_one_or_none():
            print(f'= {args.username} already exists, left unchanged')
            return
        print(f"+ {args.role} {args.username}, access {'expires ' + expires_at.strftime('%b %d %Y %I:%M %p %Z') if expires_at else 'never expires'}")
        db.add(User(email=args.username, password_hash=hash_password(password), role=args.role,
                    is_active=True, expires_at=expires_at))
        if args.apply:
            await db.commit()
            print('committed')
        else:
            await db.rollback()
            print('dry run only (pass --apply to write)')


if __name__ == '__main__':
    asyncio.run(main())
