from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import User, Base
from utils.auth import hash_password
import os
from dotenv import load_dotenv

load_dotenv()

# Create engine and session
DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

def create_admin_user(email: str, password: str, role: str = 'admin'):
    """Create a new admin user"""
    # Check if user exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"User with email {email} already exists!")
        return
    
    # Debug: print password length
    print(f"Password length: {len(password)} characters, {len(password.encode('utf-8'))} bytes")
    
    # Hash the password
    password_hash = hash_password(password)
    print(f"Hash created successfully, length: {len(password_hash)}")


    # Create new user
    user = User(
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    print(f"Admin user created successfully: {email}")

if __name__ == "__main__":
    email = input("Enter admin email: ")
    password = input("Enter password: ")
    role = input("Enter role (default: admin): ") or "admin"
    
    create_admin_user(email, password, role)
    db.close()