from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, func, update
from db.models import Question, QuestionLike
from db.schemas import QuestionCreate, QuestionUpdate
from typing import Optional, List, Set, Tuple
from datetime import datetime, timezone

async def create_question(db: AsyncSession, question: QuestionCreate) -> Question:
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
    sort_by: str = "popular"  # "recent" or "popular"
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
    Toggle the visitor's like on a question.
    The count is recomputed from like rows in one UPDATE, so simultaneous likes are never lost.
    Returns: (liked, new_like_count)
    """
    result = await db.execute(
        select(QuestionLike).where(
            and_(
                QuestionLike.question_id == question_id,
                QuestionLike.session_id == session_id
            )
        )
    )
    existing_like = result.scalars().first()

    if existing_like:
        await db.delete(existing_like)
    else:
        db.add(QuestionLike(question_id=question_id, session_id=session_id))
    await db.flush()

    like_count = (
        select(func.count(QuestionLike.id))
        .where(QuestionLike.question_id == question_id)
        .scalar_subquery()
    )
    result = await db.execute(
        update(Question)
        .where(Question.id == question_id)
        .values(likes_count=like_count)
        .returning(Question.likes_count)
    )
    likes = result.scalar_one()
    await db.commit()
    return not existing_like, likes


async def get_liked_question_ids(db: AsyncSession, event_id: int, session_id: str) -> Set[str]:
    """Ids of the questions in this session that the visitor has liked (one query)"""
    result = await db.execute(
        select(QuestionLike.question_id)
        .join(Question, Question.id == QuestionLike.question_id)
        .where(Question.event_id == event_id, QuestionLike.session_id == session_id)
    )
    return {str(question_id) for question_id in result.scalars()}
