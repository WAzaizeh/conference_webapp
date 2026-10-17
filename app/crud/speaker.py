from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.models import Event, Speaker, event_speakers
from db.schemas import SpeakerCreate

async def create_speaker(db: AsyncSession, speaker: SpeakerCreate) -> Speaker:
    """Create a new speaker"""
    db_speaker = Speaker(**speaker.model_dump())
    db.add(db_speaker)
    await db.commit()
    await db.refresh(db_speaker)
    return db_speaker

async def get_speaker(db: AsyncSession, speaker_id: int) -> Optional[Speaker]:
    """Get speaker by ID"""
    result = await db.execute(
        select(Speaker).options(selectinload(Speaker.events)).where(Speaker.id == speaker_id)
    )
    speaker = result.scalar_one_or_none()
    return speaker

async def get_speakers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Speaker]:
    """Get all speakers with pagination, in program order: by their first session (then id);
    speakers without a session come last"""
    first_session = (
        select(event_speakers.c.speaker_id, func.min(Event.start_time).label('starts'))
        .join(Event, Event.id == event_speakers.c.event_id)
        .group_by(event_speakers.c.speaker_id)
        .subquery()
    )
    result = await db.execute(
        select(Speaker)
        .outerjoin(first_session, first_session.c.speaker_id == Speaker.id)
        .options(selectinload(Speaker.events))
        .order_by(first_session.c.starts.asc().nulls_last(), Speaker.id)
        .offset(skip).limit(limit)
    )
    speakers = result.scalars().all()
    return speakers
