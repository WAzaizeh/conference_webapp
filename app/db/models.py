from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

# Association table for many-to-many relationship between events and speakers
event_speakers = Table(
    'event_speakers',
    Base.metadata,
    Column('event_id', Integer, ForeignKey('events.id'), primary_key=True),
    Column('speaker_id', Integer, ForeignKey('speakers.id'), primary_key=True)
)

class Event(Base):
    __tablename__ = 'events'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(255))
    category = Column(String(50), default='MAIN')
    
    # Many-to-many relationship with speakers
    speakers = relationship("Speaker", secondary=event_speakers, back_populates="events")

class Speaker(Base):
    __tablename__ = 'speakers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    image_url = Column(String(500))
    bio = Column(Text)
    
    # Many-to-many relationship with events
    events = relationship("Event", secondary=event_speakers, back_populates="speakers")

class PrayerTime(Base):
    __tablename__ = 'prayer_times'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # DHUHR, ASR, MAGHRIB, ISHA
    time = Column(String(20))  # Prayer time
    iqama = Column(String(20))  # Iqama time

class Sponsor(Base):
    __tablename__ = 'sponsors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    image_url = Column(String(500))
    description = Column(Text)
    website = Column(String(500))
    facebook = Column(String(500))
    instagram = Column(String(500))
    twitter = Column(String(500))

# User and Session models for authentication
class User(Base):
    __tablename__ = 'users'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'moderator', 'admin'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True))

class Session(Base):
    __tablename__ = 'sessions'
    
    id = Column(String(255), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")

class AuditLog(Base):
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='SET NULL'))
    action = Column(String(255), nullable=False)
    entity = Column(String(100))
    entity_id = Column(String(100))
    meta = Column(Text)  # JSON data
    ts = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")

class FeedbackSubmission(Base):
    __tablename__ = 'feedback_submissions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    submission_data = Column(JSON, nullable=False)  # Store all survey responses as JSON
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    ip_address = Column(String(45))  # To track submissions and prevent duplicates
    user_agent = Column(Text)  # Additional tracking