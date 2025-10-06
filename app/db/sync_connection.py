import os
import re
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from .models import Base
from contextlib import contextmanager

# Load .env.dev only for local development
if not os.getenv('K_SERVICE'):  # Not running on Cloud Run
    load_dotenv('dev.env')

class SyncDatabaseManager:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        print(f"Original DATABASE_URL: {database_url}")

        database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')

        self.database_url = database_url
        self.engine = create_engine(database_url, echo=True)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables"""
        Base.metadata.drop_all(bind=self.engine)

    def test_connection(self):
        """Test database connection"""
        with self.engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return result.fetchone()

    def is_postgresql(self):
        """Check if using PostgreSQL"""
        return 'postgresql' in self.database_url

    def is_sqlite(self):
        """Check if using SQLite"""
        return 'sqlite' in self.database_url

# Global sync database manager instance
sync_db_manager = SyncDatabaseManager()

@contextmanager
def get_db():
    """Context manager for database sessions"""
    db = sync_db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()