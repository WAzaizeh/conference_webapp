from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import delete
from db.models import Event, Speaker
from db.schemas import (
    EventCreate, EventUpdate,
)
from utils.speaker_utils import get_speaker_image_url

def _enrich_event_speakers(event: Event) -> Event:
    """
    Enrich all speakers in an event with placeholder images if needed.
    This modifies the event object in place.
    """
    if event.speakers:
        for speaker in event.speakers:
            speaker.image_url = get_speaker_image_url(speaker.id, speaker.name, speaker.image_url)
    return event

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
    event = result.scalar_one_or_none()
    return _enrich_event_speakers(event) if event else None

async def get_events(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Event]:
    """Get all events with pagination"""
    result = await db.execute(
        select(Event).options(selectinload(Event.speakers)).offset(skip).limit(limit)
    )
    events =  result.scalars().all()
    return [_enrich_event_speakers(e) for e in events]

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

async def toggle_qa_active(db: AsyncSession, event_id: int) -> Optional[Event]:
    """Toggle Q&A active status for an event"""
    db_event = await get_event(db, event_id)
    if not db_event:
        return None
    
    # Toggle the is_qa_active field
    db_event.is_qa_active = not db_event.is_qa_active
    
    await db.commit()
    await db.refresh(db_event)
    return db_event