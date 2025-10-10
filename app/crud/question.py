from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func
from db.models import Question, QuestionLike
from db.schemas import QuestionCreate, QuestionUpdate
from typing import Optional, List, Tuple
from datetime import datetime, timezone

async def create_question(
    db: AsyncSession, 
    question: QuestionCreate, 
    ip_address: Optional[str] = None
) -> Question:
    """Create a new question"""
    db_question = Question(
        **question.model_dump(),
        is_visible=False,  # Questions hidden by default until approved
        is_answered=False,
        likes_count=0
    )
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question

async def get_question(db: AsyncSession, question_id: str) -> Optional[Question]:
    """Get question by ID"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
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
        query = query.order_by(Question.likes_count.desc(), Question.created_at.desc())
    else:  # recent
        query = query.order_by(Question.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_question(
    db: AsyncSession, 
    question_id: str, 
    question_update: QuestionUpdate
) -> Optional[Question]:
    """Update a question"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    db_question = result.scalar_one_or_none()
    
    if db_question:
        update_data = question_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_question, field, value)
        
        db_question.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(db_question)
    
    return db_question

async def delete_question(db: AsyncSession, question_id: str) -> bool:
    """Delete a question"""
    result = await db.execute(
        select(Question).where(Question.id == question_id)
    )
    db_question = result.scalar_one_or_none()
    
    if db_question:
        await db.delete(db_question)
        await db.commit()
        return True
    
    return False

async def toggle_like(
    db: AsyncSession, 
    question_id: str, 
    session_id: str
) -> Tuple[bool, int]:
    """
    Toggle like for a question
    Returns: (liked: bool, new_like_count: int)
    """
    # Check if user already liked
    result = await db.execute(
        select(QuestionLike).where(
            and_(
                QuestionLike.question_id == question_id,
                QuestionLike.session_id == session_id
            )
        )
    )
    existing_like = result.scalar_one_or_none()
    
    # Get the question
    question = await get_question(db, question_id)
    if not question:
        return False, 0
    
    if existing_like:
        # Unlike: Remove like
        await db.delete(existing_like)
        question.likes_count = max(0, question.likes_count - 1)
        liked = False
    else:
        # Like: Add like
        new_like = QuestionLike(
            question_id=question_id,
            session_id=session_id
        )
        db.add(new_like)
        question.likes_count += 1
        liked = True
    
    await db.commit()
    await db.refresh(question)
    
    return liked, question.likes_count

async def check_user_liked(
    db: AsyncSession, 
    question_id: str, 
    session_id: str
) -> bool:
    """Check if a user has liked a question"""
    result = await db.execute(
        select(func.count(QuestionLike.id)).where(
            and_(
                QuestionLike.question_id == question_id,
                QuestionLike.session_id == session_id
            )
        )
    )
    count = result.scalar()
    return count > 0
