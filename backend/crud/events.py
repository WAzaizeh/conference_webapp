from sqlalchemy.orm import Session
from db.models import DBEvent
from .common import get_db_event, get_db_speaker, _get_db_event
from db.schemas import (
    EventOut,
    EventCreate,
    EventUpdate,
    SpeakerOut,
)

def create_db_event(event: EventCreate, db: Session) -> EventOut:
    db_event = DBEvent(**event.model_dump(exclude={'speaker_ids'}))
    if event.speaker_ids:
        db_event.speakers = [get_db_speaker(speaker_id, db) for speaker_id in event.speaker_ids]
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return EventOut(**db_event.__dict__)

def update_db_event(event_id: int, event: EventUpdate, db: Session) -> EventOut:
    db_event = _get_db_event(event_id, db)
    if not db_event:
        return None
    update_data = event.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_event, key, value)
    if 'speaker_ids' in update_data:
        db_event.speakers = [get_db_speaker(speaker_id, db) for speaker_id in update_data['speaker_ids']]
    db.commit()
    db.refresh(db_event)
    return EventOut(**db_event.__dict__)

def delete_db_event(event_id: int, db: Session) -> EventOut:
    db_event = _get_db_event(event_id, db)
    if db_event:
        db.delete(db_event)
        db.commit()
    return EventOut(**db_event.__dict__)

def read_db_event_speakers(event_id: int, db: Session) -> list[SpeakerOut]:
    db_event = get_db_event(event_id, db)
    if db_event:
        return [SpeakerOut(**speaker.__dict__) for speaker in db_event.speakers]
    return []