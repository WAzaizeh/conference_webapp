from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum
from pydantic.config import ConfigDict

class EVENT_CATEGORY(str, Enum):
    MAIN = 'main session'
    CYP = 'College & Young Professionals'

class EventBase(BaseModel):
    id: Optional[int] = None
    title: str
    start_time: datetime
    end_time: datetime
    location: str
    category: EVENT_CATEGORY
    description: Optional[str] = None

class EventCreate(EventBase):
    start_time: datetime = datetime(2024, 10, 21, 10, 0)
    end_time: datetime = datetime(2024, 10, 21, 21, 0)
    location: str = 'Colin College Conference Center'
    category: EVENT_CATEGORY = EVENT_CATEGORY.MAIN
    description: Optional[str] = None
    speaker_ids: Optional[List[int]] = []

class EventUpdate(EventBase):
    title: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[EVENT_CATEGORY] = None
    description: Optional[str] = None
    speaker_ids: Optional[List[int]] = None

class EventOut(EventBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    speakers: Optional[List[int]] = []

class SpeakerBase(BaseModel):
    id: Optional[int] = None
    name: str
    image_url: Optional[str] = None
    bio: Optional[str] = None

class SpeakerCreate(SpeakerBase):
    event_ids: Optional[List[int]] = None

class SpeakerUpdate(SpeakerBase):
    event_ids: Optional[List[int]] = None

class SpeakerOut(SpeakerBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    events: Optional[List[int]] = []

class PRAYER_NAME(str, Enum):
    FAJR = 'Fajr'
    DHUHR = 'Dhuhr'
    ASR = 'Asr'
    MAGHRIB = 'Maghrib'
    ISHA = 'Isha'
class PrayerTime(BaseModel):
    id: Optional[int] = None
    name: PRAYER_NAME
    time: datetime