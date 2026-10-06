from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from db.models import Speaker
from db.schemas import SpeakerCreate
from utils.speaker_utils import get_speaker_image_url

def _enrich_speaker_image(speaker: Speaker) -> Speaker:
    """
    Enrich speaker with placeholder image URL if needed.
    This modifies the speaker object in place.
    """
    speaker.image_url = get_speaker_image_url(speaker.id, speaker.name, speaker.image_url)
    return speaker

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
    return _enrich_speaker_image(speaker) if speaker else None

async def get_speakers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Speaker]:
    """Get all speakers with pagination"""
    result = await db.execute(
        select(Speaker).options(selectinload(Speaker.events)).offset(skip).limit(limit)
    )
    speakers = result.scalars().all()
    return [_enrich_speaker_image(s) for s in speakers]
