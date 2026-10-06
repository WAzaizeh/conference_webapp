from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import PrayerTime

PRAYER_ORDER = ['FAJR', 'DHUHR', 'ASR', 'MAGHRIB', 'ISHA']

async def get_prayer_times(db: AsyncSession) -> List[PrayerTime]:
    """Get all prayer times, in the order they occur during the day"""
    result = await db.execute(select(PrayerTime))
    return sorted(result.scalars().all(), key=lambda p: PRAYER_ORDER.index(p.name) if p.name in PRAYER_ORDER else len(PRAYER_ORDER))
