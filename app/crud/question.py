from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete, update, and_, desc, func
from datetime import datetime
from db.models import Question, QuestionLike
from db.schemas import QuestionCreate, QuestionUpdate, QuestionLikeCreate
import uuid

async def create_question(
    db: AsyncSession, 
    question: QuestionCreate,
    ip_address: Optional[str] = None
) -> Question:
    """Create a new question"""
    db_question = Question(
        **question.dict(),
        ip_address=ip_address
    )
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question

async def get_question(db: AsyncSession, question_id: str) -> Optional[Question]:
    """Get question by ID"""
    result = await db.execute(
        select(Question).where(Question.id == uuid.UUID(question_id))
    )
    return result.scalar_one_or_none()

async def get_questions_by_event(
    db: AsyncSession, 
    event_id: int,
    visible_only: bool = True,
    sort_by: str = "recent"  # "recent" or "popular"
) -> List[Question]:
    """Get all questions for an event"""
    query = select(Question).where(Question.event_id == event_id)
    
    if visible_only:
        query = query.where(Question.is_visible == True)
    
    if sort_by == "popular":
        query = query.order_by(desc(Question.likes_count), desc(Question.created_at))
    else:  # recent
        query = query.order_by(desc(Question.created_at))
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_question(
    db: AsyncSession, 
    question_id: str, 
    question_update: QuestionUpdate
) -> Optional[Question]:
    """Update a question"""
    db_question = await get_question(db, question_id)
    if not db_question:
        return None
    
    update_data = question_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_question, field, value)
    
    await db.commit()
    await db.refresh(db_question)
    return db_question

async def delete_question(db: AsyncSession, question_id: str) -> bool:
    """Delete a question"""
    result = await db.execute(
        delete(Question).where(Question.id == uuid.UUID(question_id))
    )
    await db.commit()
    return result.rowcount > 0

async def toggle_like(
    db: AsyncSession,
    question_id: str,
    session_id: str
) -> tuple[bool, int]:
    """
    Toggle like for a question. Returns (liked, new_count)
    liked=True means like was added, False means like was removed
    """
    # Check if already liked
    result = await db.execute(
        select(QuestionLike).where(
            and_(
                QuestionLike.question_id == uuid.UUID(question_id),
                QuestionLike.session_id == session_id
            )
        )
    )
    existing_like = result.scalar_one_or_none()
    
    if existing_like:
        # Remove like
        await db.execute(
            delete(QuestionLike).where(QuestionLike.id == existing_like.id)
        )
        # Decrement count
        await db.execute(
            update(Question)
            .where(Question.id == uuid.UUID(question_id))
            .values(likes_count=Question.likes_count - 1)
        )
        await db.commit()
        
        # Get updated count
        question = await get_question(db, question_id)
        return False, question.likes_count if question else 0
    else:
        # Add like
        db_like = QuestionLike(
            question_id=uuid.UUID(question_id),
            session_id=session_id
        )
        db.add(db_like)
        
        # Increment count
        await db.execute(
            update(Question)
            .where(Question.id == uuid.UUID(question_id))
            .values(likes_count=Question.likes_count + 1)
        )
        await db.commit()
        
        # Get updated count
        question = await get_question(db, question_id)
        return True, question.likes_count if question else 0

async def check_user_liked(
    db: AsyncSession,
    question_id: str,
    session_id: str
) -> bool:
    """Check if a user has liked a question"""
    result = await db.execute(
        select(QuestionLike).where(
            and_(
                QuestionLike.question_id == uuid.UUID(question_id),
                QuestionLike.session_id == session_id
            )
        )
    )
    return result.scalar_one_or_none() is not None
