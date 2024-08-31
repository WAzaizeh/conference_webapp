from __future__ import annotations
from typing import Optional, List
# from .automation.run import run_automations
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .core import DBEvent, DBSpeaker, NotFoundError
from .events import Event

class Speaker(BaseModel):
    id: int
    name: str
    image_url: str = None
    bio: str = None
    
    class Config:
        from_attributes = True

class SpeakerCreate(BaseModel):
    name: str

class SpeakerUpdate(BaseModel):
    pass