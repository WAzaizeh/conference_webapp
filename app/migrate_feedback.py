"""
Migration script to add feedback_submissions table
Run this to add the feedback feature to your database
"""
import os
from sqlalchemy import text, create_engine
from sqlalchemy.orm import sessionmaker

# Create synchronous engine
database_url = os.getenv('DATABASE_URL')
if database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')

print(f"Connecting to: {database_url}")

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

def upgrade():
    """Add feedback_submissions table"""
    with SessionLocal() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS feedback_submissions (
                id UUID PRIMARY KEY,
                submission_data JSONB NOT NULL,
                submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                ip_address VARCHAR(45),
                user_agent TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_feedback_ip 
            ON feedback_submissions(ip_address);
            
            CREATE INDEX IF NOT EXISTS idx_feedback_submitted_at 
            ON feedback_submissions(submitted_at DESC);
        """))

        conn.commit()
        conn.close()

    print("✅ feedback_submissions table created successfully!")

def downgrade():
    """Remove feedback_submissions table"""
    with SessionLocal() as conn:
        conn.execute(text("""
            DROP TABLE IF EXISTS feedback_submissions;
        """))
        conn.commit()
        conn.close()
    
    print("✅ feedback_submissions table dropped successfully!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "downgrade":
        downgrade()
    else:
        upgrade()
