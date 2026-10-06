from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.models import Sponsor

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
