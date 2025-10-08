from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db.models import FeedbackSubmission
from db.schemas import FeedbackSubmissionCreate
from typing import Optional
import uuid
from datetime import datetime, timedelta

async def create_feedback(
    db: AsyncSession, 
    feedback_data: FeedbackSubmissionCreate,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> FeedbackSubmission:
    """Create a new feedback submission"""
    feedback = FeedbackSubmission(
        id=uuid.uuid4(),
        submission_data=feedback_data.submission_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback

async def check_recent_submission(
    db: AsyncSession,
    ip_address: str,
    hours: int = 24
) -> bool:
    """Check if there's a recent submission from this IP address"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours)
    
    result = await db.execute(
        select(FeedbackSubmission)
        .where(FeedbackSubmission.ip_address == ip_address)
        .where(FeedbackSubmission.submitted_at > cutoff_time)
    )
    
    return result.scalar_one_or_none() is not None

async def get_all_feedback(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> list[FeedbackSubmission]:
    """Get all feedback submissions (admin only)"""
    result = await db.execute(
        select(FeedbackSubmission)
        .order_by(FeedbackSubmission.submitted_at.desc())
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

async def get_feedback_count(db: AsyncSession) -> int:
    """Get total count of feedback submissions"""
    result = await db.execute(
        select(func.count(FeedbackSubmission.id))
    )
    return result.scalar_one()

async def get_feedback_by_id(
    db: AsyncSession,
    feedback_id: str
) -> Optional[FeedbackSubmission]:
    """Get a specific feedback submission by ID"""
    result = await db.execute(
        select(FeedbackSubmission)
        .where(FeedbackSubmission.id == feedback_id)
    )
    return result.scalar_one_or_none()
