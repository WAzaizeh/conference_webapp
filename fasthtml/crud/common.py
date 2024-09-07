from sqlalchemy.orm import Session
from db.models import DBEvent, DBSpeaker
from db.schemas import EventOut, SpeakerOut

def _get_db_event(event_id: int, db: Session) -> DBEvent:
    db_event = db.query(DBEvent).filter(DBEvent.id == event_id).first()
    if db_event is None:
        raise FileNotFoundError(f'Event with id {event_id} not found')
    return db_event

def get_db_event(event_id: int, db: Session) -> EventOut:
    db_event = _get_db_event(event_id, db)
    return EventOut(**db_event.__dict__)

def _get_all_db_events(db: Session) -> list[DBEvent]:
    return db.query(DBEvent).all()

def get_all_db_events(db: Session) -> list[EventOut]:
    db_events = _get_all_db_events(db)
    return [EventOut(**event.__dict__) for event in db_events]

def _get_db_speaker(speaker_id: int, db: Session) -> DBSpeaker:
    db_speaker = db.query(DBSpeaker).filter(DBSpeaker.id == speaker_id).first()
    if db_speaker is None:
        raise FileNotFoundError(f'Speaker with id {speaker_id} not found')
    return db_speaker

def get_db_speaker(speaker_id: int, db: Session)-> SpeakerOut:
    db_speaker = _get_db_speaker(speaker_id, db)
    return SpeakerOut(**db_speaker.__dict__)

def _get_all_db_speakers(db: Session) -> list[DBSpeaker]:
    return db.query(DBSpeaker).all()

def get_all_db_speakers(db: Session) -> list[SpeakerOut]:
    db_speakers = _get_all_db_speakers(db)
    return [SpeakerOut(**speaker.__dict__) for speaker in db_speakers]