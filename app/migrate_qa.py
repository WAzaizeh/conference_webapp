"""
Migration script to add Q&A tables to the database.
Run this script to add the questions and question_likes tables.
"""
import asyncio
from sqlalchemy import text
from db.connection import db_manager

async def migrate():
    """Add Q&A tables to the database"""
    
    async with db_manager.AsyncSessionLocal() as db:
        # Create questions table
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS questions (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                event_id INTEGER NOT NULL REFERENCES events(id) ON DELETE CASCADE,
                nickname VARCHAR(100) NOT NULL,
                question_text TEXT NOT NULL,
                is_visible BOOLEAN DEFAULT FALSE,
                is_answered BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                ip_address VARCHAR(45),
                likes_count INTEGER DEFAULT 0
            );
        """))
        
        # Create question_likes table
        await db.execute(text("""
            CREATE TABLE IF NOT EXISTS question_likes (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                question_id UUID NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
                session_id VARCHAR(255),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            );
        """))
        
        # Create indexes for better performance
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_event_id ON questions(event_id);
        """))
        
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_is_visible ON questions(is_visible);
        """))
        
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_created_at ON questions(created_at DESC);
        """))
        
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_likes_count ON questions(likes_count DESC);
        """))
        
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_question_likes_question_id ON question_likes(question_id);
        """))
        
        await db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_question_likes_session_id ON question_likes(session_id);
        """))
        
        await db.commit()
        print("✓ Q&A tables created successfully!")

if __name__ == "__main__":
    asyncio.run(migrate())
