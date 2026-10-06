from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from db.models import FeedbackSubmission
from datetime import datetime, timezone
from typing import Optional


async def get_user_feedback(db: AsyncSession, session_id: str) -> Optional[FeedbackSubmission]:
    """The visitor's most recent feedback submission, if any"""
    result = await db.execute(
        select(FeedbackSubmission)
        .where(FeedbackSubmission.session_id == session_id)
        .order_by(FeedbackSubmission.submitted_at.desc())
        .limit(1)
    )
    return result.scalar_one_or_none()


async def save_feedback(db: AsyncSession, session_id: str, submission_data: dict) -> FeedbackSubmission:
    """Create the visitor's submission, or update it if they already submitted (one row per visitor)"""
    submission = await get_user_feedback(db, session_id)
    if submission:
        submission.submission_data = submission_data
        submission.submitted_at = datetime.now(timezone.utc)
    else:
        submission = FeedbackSubmission(submission_data=submission_data, session_id=session_id)
        db.add(submission)
    await db.commit()
    await db.refresh(submission)
    return submission


async def get_feedback_count(db: AsyncSession) -> int:
    """Total number of feedback submissions"""
    result = await db.execute(select(func.count(FeedbackSubmission.id)))
    return result.scalar() or 0
