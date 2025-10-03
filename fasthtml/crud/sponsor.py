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

async def create_sponsor(db: AsyncSession, sponsor: SponsorCreate) -> Sponsor:
    """Create a new sponsor"""
    db_sponsor = Sponsor(**sponsor.dict())
    db.add(db_sponsor)
    await db.commit()
    await db.refresh(db_sponsor)
    return db_sponsor

async def get_sponsors(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Sponsor]:
    """Get all sponsors with pagination"""
    result = await db.execute(
        select(Sponsor).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def get_sponsor(db: AsyncSession, sponsor_id: int) -> Optional[Sponsor]:
    """Get a sponsor by ID"""
    result = await db.execute(select(Sponsor).where(Sponsor.id == sponsor_id))
    return result.scalar_one_or_none()

async def update_sponsor(db: AsyncSession, sponsor_id: int, sponsor_update: SponsorUpdate) -> Optional[Sponsor]:
    """Update a sponsor"""
    result = await db.execute(select(Sponsor).where(Sponsor.id == sponsor_id))
    db_sponsor = result.scalar_one_or_none()
    if not db_sponsor:
        return None
    
    update_data = sponsor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_sponsor, field, value)
    
    await db.commit()
    await db.refresh(db_sponsor)
    return db_sponsor

async def delete_sponsor(db: AsyncSession, sponsor_id: int) -> bool:
    """Delete a sponsor"""
    result = await db.execute(delete(Sponsor).where(Sponsor.id == sponsor_id))
    await db.commit()
    return result.rowcount > 0
