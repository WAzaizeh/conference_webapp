from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime
from db.models import Event, Speaker

async def get_events_by_date_range(
    db: AsyncSession, 
    start_date: datetime, 
    end_date: datetime
) -> List[Event]:
    """Get events within a date range"""
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.speakers))
        .where(Event.start_time >= start_date)
        .where(Event.end_time <= end_date)
        .order_by(Event.start_time)
    )
    return result.scalars().all()

async def search_events(db: AsyncSession, query: str) -> List[Event]:
    """Search events by title or description"""
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.speakers))
        .where(Event.title.ilike(f"%{query}%") | Event.description.ilike(f"%{query}%"))
    )
    return result.scalars().all()

async def get_speaker_events(db: AsyncSession, speaker_id: int) -> List[Event]:
    """Get all events for a specific speaker"""
    result = await db.execute(
        select(Event)
        .options(selectinload(Event.speakers))
        .join(Event.speakers)
        .where(Speaker.id == speaker_id)
    )
    return result.scalars().all()