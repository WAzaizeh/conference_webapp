"""Add is_qa_active field to events table and session_id to feedback_submissions"""
import asyncio
from sqlalchemy import text
from db.connection import db_manager

async def migrate():
    """Add is_qa_active column to events and session_id to feedback_submissions"""
    async with db_manager.AsyncSessionLocal() as db:
        try:
            # Add is_qa_active, created_at, updated_at to events
            await db.execute(text(
                "ALTER TABLE events ADD COLUMN IF NOT EXISTS is_qa_active BOOLEAN DEFAULT FALSE"
            ))
            await db.execute(text(
                "ALTER TABLE events ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
            ))
            await db.execute(text(
                "ALTER TABLE events ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP"
            ))

            # Add session_id to feedback_submissions
            await db.execute(text(
                "ALTER TABLE feedback_submissions ADD COLUMN IF NOT EXISTS session_id VARCHAR(255)"
            ))
            
            await db.commit()
            print("✅ Migration completed successfully")
        except Exception as e:
            await db.rollback()
            print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    asyncio.run(migrate())