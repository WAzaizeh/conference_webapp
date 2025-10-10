from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.models import Speaker
from db.schemas import SpeakerCreate, SpeakerUpdate

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
    return result.scalar_one_or_none()

async def get_speakers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Speaker]:
    """Get all speakers with pagination"""
    result = await db.execute(
        select(Speaker).options(selectinload(Speaker.events)).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def update_speaker(db: AsyncSession, speaker_id: int, speaker_update: SpeakerUpdate) -> Optional[Speaker]:
    """Update a speaker"""
    result = await db.execute(select(Speaker).where(Speaker.id == speaker_id))
    db_speaker = result.scalar_one_or_none()
    
    if db_speaker:
        update_data = speaker_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_speaker, field, value)
        
        await db.commit()
        await db.refresh(db_speaker)
    
    return db_speaker

async def delete_speaker(db: AsyncSession, speaker_id: int) -> bool:
    """Delete a speaker"""
    result = await db.execute(select(Speaker).where(Speaker.id == speaker_id))
    db_speaker = result.scalar_one_or_none()
    
    if db_speaker:
        await db.delete(db_speaker)
        await db.commit()
        return True
    
    return False
