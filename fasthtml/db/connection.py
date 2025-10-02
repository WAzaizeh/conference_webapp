import os
import re
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from dotenv import load_dotenv
from .models import Base

class DatabaseManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL', 'sqlite+aiosqlite:///./conference.db')
        print(f"Original DATABASE_URL: {database_url}")
        
        # Convert postgresql to postgresql+asyncpg for async support
        if database_url.startswith('postgresql://'):
            database_url = re.sub(r'^postgresql:', 'postgresql+asyncpg:', database_url)
            print(f"Converted to asyncpg: {database_url}")
        elif database_url.startswith('sqlite://'):
            database_url = database_url.replace('sqlite://', 'sqlite+aiosqlite://')
        
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=True)
        self.AsyncSessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        """Drop all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    async def get_session(self):
        """Get database session"""
        async with self.AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()

    async def test_connection(self):
        """Test database connection"""
        async with self.engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            return result.fetchone()

    def is_postgresql(self):
        """Check if using PostgreSQL"""
        return 'postgresql' in self.database_url

    def is_sqlite(self):
        """Check if using SQLite"""
        return 'sqlite' in self.database_url

# Global database manager instance
db_manager = DatabaseManager()