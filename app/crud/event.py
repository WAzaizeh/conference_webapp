from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, update
from datetime import datetime
from db.models import Event, Speaker, PrayerTime, Sponsor, User, Session, AuditLog
from db.schemas import (
    EventOut, EventCreate, EventUpdate,
    SpeakerOut, SpeakerCreate, SpeakerUpdate,
    PrayerTimeOut, PrayerTimeCreate, PrayerTimeUpdate,
    SponsorOut, SponsorCreate, SponsorUpdate
)

async def create_event(db: AsyncSession, event: EventCreate) -> Event:
    """Create a new event"""
    db_event = Event(**event.dict(exclude={'speaker_ids'}))
    
    # Add speakers if provided
    if event.speaker_ids:
        speakers = await db.execute(select(Speaker).where(Speaker.id.in_(event.speaker_ids)))
        db_event.speakers = speakers.scalars().all()
    
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def get_event(db: AsyncSession, event_id: int) -> Optional[Event]:
    """Get event by ID"""
    result = await db.execute(
        select(Event).options(selectinload(Event.speakers)).where(Event.id == event_id)
    )
    return result.scalar_one_or_none()

async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get all events with pagination"""
    result = await db.execute(
        select(Event).options(selectinload(Event.speakers)).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_event(db: AsyncSession, event_id: int, event_update: EventUpdate) -> Optional[Event]:
    """Update an event"""
    db_event = await get_event(db, event_id)
    if not db_event:
        return None
    
    update_data = event_update.dict(exclude_unset=True, exclude={'speaker_ids'})
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    # Update speakers if provided
    if event_update.speaker_ids is not None:
        speakers = await db.execute(select(Speaker).where(Speaker.id.in_(event_update.speaker_ids)))
        db_event.speakers = speakers.scalars().all()
    
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def delete_event(db: AsyncSession, event_id: int) -> bool:
    """Delete an event"""
    result = await db.execute(delete(Event).where(Event.id == event_id))
    await db.commit()
    return result.rowcount > 0