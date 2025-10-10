from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from enum import Enum

class EVENT_CATEGORY(str, Enum):
    MAIN = "MAIN"
    WORKSHOP = "WORKSHOP"
    BREAK = "BREAK"

class PRAYER_NAME(str, Enum):
    FAJR = "FAJR"
    DHUHR = "DHUHR"
    ASR = "ASR"
    MAGHRIB = "MAGHRIB"
    ISHA = "ISHA"

# ==================== SPEAKER SCHEMAS ====================

class SpeakerBase(BaseModel):
    name: str
    image_url: Optional[str] = ""
    bio: Optional[str] = ""

class SpeakerCreate(SpeakerBase):
    pass

class SpeakerUpdate(BaseModel):
    name: Optional[str] = None
    image_url: Optional[str] = None
    bio: Optional[str] = None

class SpeakerOut(SpeakerBase):
    id: int
    
    class Config:
        from_attributes = True

# ==================== EVENT SCHEMAS ====================

class EventBase(BaseModel):
    title: str
    description: Optional[str] = ""
    start_time: datetime
    end_time: datetime
    location: Optional[str] = ""
    category: EVENT_CATEGORY = EVENT_CATEGORY.MAIN

class EventCreate(EventBase):
    speaker_ids: Optional[List[int]] = []

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[EVENT_CATEGORY] = None
    speaker_ids: Optional[List[int]] = None

class EventOut(EventBase):
    id: int
    speakers: List[int] = []
    
    class Config:
        from_attributes = True

# ==================== PRAYER TIME SCHEMAS ====================

class PrayerTimeBase(BaseModel):
    name: PRAYER_NAME
    time: str
    iqama: str

class PrayerTimeCreate(PrayerTimeBase):
    pass

class PrayerTimeUpdate(BaseModel):
    name: Optional[PRAYER_NAME] = None
    time: Optional[str] = None
    iqama: Optional[str] = None

class PrayerTimeOut(PrayerTimeBase):
    id: int
    
    class Config:
        from_attributes = True

# ==================== SPONSOR SCHEMAS ====================

class SponsorBase(BaseModel):
    name: str
    image_url: Optional[str] = ""
    description: Optional[str] = ""
    website: Optional[str] = ""
    facebook: Optional[str] = ""
    instagram: Optional[str] = ""
    twitter: Optional[str] = ""

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

class SponsorOut(SponsorBase):
    id: int
    
    class Config:
        from_attributes = True

# ==================== FEEDBACK SCHEMAS ====================

class FeedbackSubmissionCreate(BaseModel):
    submission_data: dict

class FeedbackSubmissionOut(BaseModel):
    id: str
    submission_data: dict
    submitted_at: datetime
    ip_address: Optional[str] = None
    
    class Config:
        from_attributes = True

# ==================== Q&A SCHEMAS ====================

class QuestionCreate(BaseModel):
    event_id: int
    nickname: str
    question_text: str

class QuestionUpdate(BaseModel):
    is_visible: Optional[bool] = None
    is_answered: Optional[bool] = None

class QuestionOut(BaseModel):
    id: str
    event_id: int
    nickname: str
    question_text: str
    is_visible: bool
    is_answered: bool
    created_at: datetime
    likes_count: int
    
    class Config:
        from_attributes = True

class QuestionLikeCreate(BaseModel):
    question_id: str
    session_id: str