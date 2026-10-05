from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import User
from utils.auth import hash_password
from getpass import getpass
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Create engine and session
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def reset_password(email: str, password: str):
    """Set a new password for an existing user"""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        print(f"No user with username {email} found!")
        return False

    user.password_hash = hash_password(password)
    user.is_active = True
    db.commit()
    print(f"Password reset for {email} ({user.role})")
    return True

if __name__ == "__main__":
    email = input("Username (default: admin): ") or "admin"
    password = getpass("New password: ")
    if not password:
        sys.exit("Password cannot be empty.")
    if getpass("Confirm password: ") != password:
        sys.exit("Passwords do not match.")

    reset_password(email, password)
    db.close()
