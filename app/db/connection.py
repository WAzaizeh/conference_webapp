import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from .models import Base

class DatabaseManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        
        database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')

        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_pre_ping=True,  # Verify connections before using them
            pool_size=5,  # Number of connections to maintain
            max_overflow=10,  # Additional connections when pool is full
            pool_recycle=3600,  # Recycle connections after 1 hour
            pool_timeout=30,  # Timeout for getting connection from pool
            connect_args={
                "server_settings": {
                    "application_name": "mas_cyp_conference"
                },
                "command_timeout": 60,  # Command timeout in seconds
            }
        )
        self.AsyncSessionLocal = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def create_tables(self):
        """Create all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

# Global database manager instance
db_manager = DatabaseManager()