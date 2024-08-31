from enum import Enum
from typing import Optional
from datetime import datetime
# from .automation.run import run_automations
from pydantic import BaseModel

class EVENT_CATEGORY(str, Enum):
    MAIN = 'main session'
    CYP = 'College & Young Professionals'


class Event(BaseModel):
    id: int
    title: str
    start_datetime: datetime = datetime(2024, 10, 21, 10, 00)
    end_datetime: datetime = datetime(2024, 10, 21, 21, 00)
    location: str = 'Collin College Conference Center'
    category: EVENT_CATEGORY = EVENT_CATEGORY.MAIN
    description: Optional[str] = None

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    title: str


class EventUpdate(BaseModel):
    pass