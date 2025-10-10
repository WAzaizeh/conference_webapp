from pydantic import BaseModel, Field, UUID4
from datetime import datetime
from typing import Optional, List, Dict, Any

# Event schemas
class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    category: Optional[str] = "MAIN"

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None
    is_qa_active: Optional[bool] = None

class Event(EventBase):
    id: int
    is_qa_active: bool = False
    created_at: datetime
    updated_at: datetime
    speakers: List['Speaker'] = []
    
    class Config:
        from_attributes = True

# Speaker schemas
class SpeakerBase(BaseModel):
    name: str
    image_url: Optional[str] = None
    bio: Optional[str] = None

class SpeakerCreate(SpeakerBase):
    pass

class SpeakerUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    bio: Optional[str] = None

class Speaker(SpeakerBase):
    id: int
    events: List['Event'] = []
    
    class Config:
        from_attributes = True

# Prayer Time schemas
class PrayerTimeBase(BaseModel):
    name: str
    time: Optional[str] = None
    iqama: Optional[str] = None

class PrayerTimeCreate(PrayerTimeBase):
    pass

class PrayerTimeUpdate(BaseModel):
    name: Optional[str] = None
    time: Optional[str] = None
    iqama: Optional[str] = None

class PrayerTime(PrayerTimeBase):
    id: int
    
    class Config:
        from_attributes = True

# Sponsor schemas
class SponsorBase(BaseModel):
    name: str
    image_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None

class SponsorCreate(SponsorBase):
    pass

class SponsorUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    facebook: Optional[str] = None
    instagram: Optional[str] = None
    twitter: Optional[str] = None

class Sponsor(SponsorBase):
    id: int
    
    class Config:
        from_attributes = True

# User schemas
class UserBase(BaseModel):
    email: str
    role: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: UUID4
    is_active: bool
    created_at: datetime
    last_login_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Question schemas
class QuestionCreate(BaseModel):
    event_id: int
    nickname: str = "Anonymous"
    question_text: str

class QuestionUpdate(BaseModel):
    nickname: Optional[str] = None
    question_text: Optional[str] = None
    is_visible: Optional[bool] = None
    is_answered: Optional[bool] = None

class Question(BaseModel):
    id: UUID4
    event_id: int
    nickname: str
    question_text: str
    is_visible: bool
    is_answered: bool
    likes_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Feedback schemas
class FeedbackSubmissionCreate(BaseModel):
    submission_data: Dict[str, Any]

class FeedbackSubmission(BaseModel):
    id: UUID4
    submission_data: Dict[str, Any]
    submitted_at: datetime
    session_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True