from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, and_
from db.models import FeedbackSubmission
from db.schemas import FeedbackSubmissionCreate
from datetime import datetime, timedelta, timezone
from typing import Optional

async def create_feedback(
    db: AsyncSession, 
    feedback: FeedbackSubmissionCreate, 
    session_id: Optional[str] = None
) -> FeedbackSubmission:
    """Create a new feedback submission"""
    db_feedback = FeedbackSubmission(
        submission_data=feedback.submission_data,
        session_id=session_id,
        created_at=datetime.now(timezone.utc)
    )
    db.add(db_feedback)
    await db.commit()
    await db.refresh(db_feedback)
    return db_feedback

async def check_recent_submission(
    db: AsyncSession, 
    session_id: Optional[str] = None,
    hours: int = 24
) -> bool:
    """Check if there's a recent submission from this session"""
    if not session_id:
        return False
    
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    result = await db.execute(
        select(func.count(FeedbackSubmission.id)).where(
            and_(
                FeedbackSubmission.session_id == session_id,
                FeedbackSubmission.created_at > cutoff_time
            )
        )
    )
    count = result.scalar()
    return count > 0

async def get_feedback_by_session(
    db: AsyncSession,
    session_id: str
) -> Optional[FeedbackSubmission]:
    """Get feedback submission by session ID"""
    result = await db.execute(
        select(FeedbackSubmission)
        .where(FeedbackSubmission.session_id == session_id)
        .order_by(FeedbackSubmission.created_at.desc())
    )
    return result.scalar_one_or_none()

async def update_feedback(
    db: AsyncSession,
    feedback_id: str,
    feedback_data: dict
) -> Optional[FeedbackSubmission]:
    """Update an existing feedback submission"""
    result = await db.execute(
        select(FeedbackSubmission).where(FeedbackSubmission.id == feedback_id)
    )
    db_feedback = result.scalar_one_or_none()
    
    if db_feedback:
        db_feedback.submission_data = feedback_data
        db_feedback.created_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_feedback)
    
    return db_feedback

async def get_feedback_count(db: AsyncSession) -> int:
    """Get total count of feedback submissions"""
    result = await db.execute(
        select(func.count(FeedbackSubmission.id))
    )
    return result.scalar() or 0

async def get_user_feedback(
    db: AsyncSession,
    session_id: str
) -> Optional[FeedbackSubmission]:
    """Get the most recent feedback submission for a session"""
    result = await db.execute(
        select(FeedbackSubmission)
        .where(FeedbackSubmission.session_id == session_id)
        .order_by(FeedbackSubmission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()
