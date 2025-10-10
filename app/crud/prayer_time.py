from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import PrayerTime
from db.schemas import (
    PrayerTimeCreate, PrayerTimeUpdate,
)

async def create_prayer_time(db: AsyncSession, prayer_time: PrayerTimeCreate) -> PrayerTime:
    """Create a new prayer time"""
    db_prayer_time = PrayerTime(**prayer_time.model_dump())
    db.add(db_prayer_time)
    await db.commit()
    await db.refresh(db_prayer_time)
    return db_prayer_time

async def get_prayer_times(db: AsyncSession) -> List[PrayerTime]:
    """Get all prayer times"""
    result = await db.execute(select(PrayerTime))
    return result.scalars().all()

async def update_prayer_time(db: AsyncSession, prayer_id: int, prayer_update: PrayerTimeUpdate) -> Optional[PrayerTime]:
    """Update a prayer time"""
    result = await db.execute(select(PrayerTime).where(PrayerTime.id == prayer_id))
    db_prayer = result.scalar_one_or_none()
    if not db_prayer:
        return None
    
    update_data = prayer_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_prayer, field, value)
    
    await db.commit()
    await db.refresh(db_prayer)
    return db_prayer
