from sqlalchemy.orm import Session
from db.models import DBSpeaker
from .common import get_db_speaker, get_db_event
from db.schemas import (
    SpeakerOut,
    EventOut,
    SpeakerCreate,
    SpeakerUpdate,
)

def create_db_speaker(speaker: SpeakerCreate, db: Session) -> SpeakerOut:
    db_speaker = DBSpeaker(**speaker.model_dumps(exclude={'event_ids'}))
    if speaker.event_ids:
        db_speaker.events = [get_db_event(event_id, db) for event_id in speaker.event_ids]
    db.add(db_speaker)
    db.commit()
    db.refresh(db_speaker)
    return SpeakerOut(**db_speaker.__dict__)

def update_db_speaker(speaker_id: int, speaker: SpeakerUpdate, db: Session) -> SpeakerOut:
    db_speaker = get_db_speaker(speaker_id, db)
    if not db_speaker:
        return None
    update_data = speaker.model_dumps(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_speaker, key, value)
    if 'event_ids' in update_data:
        db_speaker.events = [get_db_event(event_id, db) for event_id in update_data['event_ids']]
    db.commit()
    db.refresh(db_speaker)
    return SpeakerOut(**db_speaker.__dict__)

def delete_db_speaker(speaker_id: int, db: Session) -> SpeakerOut:
    db_speaker = get_db_speaker(speaker_id, db)
    if db_speaker:
        db.delete(db_speaker)
        db.commit()
    return SpeakerOut(**db_speaker.__dict__)

def read_db_speaker_events(speaker_id: int, db: Session) -> list[EventOut]:
    db_speaker = get_db_speaker(speaker_id, db)
    if db_speaker:
        return [EventOut(**event.__dict__) for event in db_speaker.events]
    return []