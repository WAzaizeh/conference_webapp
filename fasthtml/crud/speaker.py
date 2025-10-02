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

async def create_speaker(db: AsyncSession, speaker: SpeakerCreate) -> Speaker:
    """Create a new speaker"""
    db_speaker = Speaker(**speaker.dict())
    db.add(db_speaker)
    await db.commit()
    await db.refresh(db_speaker)
    return db_speaker

async def get_speaker(db: AsyncSession, speaker_id: int) -> Optional[Speaker]:
    """Get speaker by ID"""
    result = await db.execute(
        select(Speaker).options(selectinload(Speaker.events)).where(Speaker.id == speaker_id)
    )
    return result.scalar_one_or_none()

async def get_speakers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Speaker]:
    """Get all speakers with pagination"""
    result = await db.execute(
        select(Speaker).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_speaker(db: AsyncSession, speaker_id: int, speaker_update: SpeakerUpdate) -> Optional[Speaker]:
    """Update a speaker"""
    db_speaker = await get_speaker(db, speaker_id)
    if not db_speaker:
        return None
    
    update_data = speaker_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_speaker, field, value)
    
    await db.commit()
    await db.refresh(db_speaker)
    return db_speaker

async def delete_speaker(db: AsyncSession, speaker_id: int) -> bool:
    """Delete a speaker"""
    result = await db.execute(delete(Speaker).where(Speaker.id == speaker_id))
    await db.commit()
    return result.rowcount > 0
