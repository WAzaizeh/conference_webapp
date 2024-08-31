from typing import List, Optional
from .events import Event, EventCreate, EventUpdate
from .speakers import Speaker, SpeakerCreate, SpeakerUpdate
from sqlalchemy.orm import Session
from .core import DBEvent, DBSpeaker, NotFoundError

class EventOut(Event):
    speakers: Optional[List[Speaker]] = None

class SpeakerOut(Speaker):
    events: Optional[List[Event]] = None

# Events CRUD #
def create_db_event(event: EventCreate, session: Session) -> DBEvent:
    db_event = DBEvent(**event.model_dump(exclude_none=True))
    session.add(db_event)
    session.commit()
    session.refresh(db_event)

    return db_event

def read_db_event(event_id: int, session: Session) -> DBEvent:
    db_event = session.query(DBEvent).filter(DBEvent.id == event_id).first()
    if db_event is None:
        raise NotFoundError(f"Event with id {event_id} not found.")
    return db_event

def read_db_speakers_for_event(event_id: int, session: Session) -> list[DBSpeaker]:
    return session.query(DBEvent.speakers).filter(DBEvent.id == event_id).all()

def update_db_event(event_id: int, event: EventUpdate, session: Session) -> DBEvent:
    db_event = read_db_event(event_id, session)
    for key, value in event.model_dump(exclude_none=True).events():
        setattr(db_event, key, value)
    session.commit()
    session.refresh(db_event)
    return db_event

def delete_db_event(event_id: int, session: Session) -> DBEvent:
    db_event = read_db_event(event_id, session)
    session.delete(db_event)
    session.commit()
    return db_event


# Speakers CRUD #
def create_db_speaker(speaker: SpeakerCreate, session: Session) -> DBSpeaker:
    db_speaker = DBSpeaker(**speaker.model_dump(exclude_none=True))
    session.add(db_speaker)
    session.commit()
    session.refresh(db_speaker)

    return db_speaker

def read_db_speaker(speaker_id: int, session: Session) -> DBSpeaker:
    db_speaker = session.query(DBSpeaker).filter(DBSpeaker.id == speaker_id).first()
    if db_speaker is None:
        raise NotFoundError(f"Speaker with id {speaker_id} not found.")
    return db_speaker

def update_db_speaker(speaker_id: int, speaker: SpeakerUpdate, session: Session) -> DBSpeaker:
    db_speaker = read_db_speaker(speaker_id, session)
    for key, value in speaker.model_dump(exclude_none=True).events():
        setattr(db_speaker, key, value)
    session.commit()
    session.refresh(db_speaker)
    return db_speaker

def delete_db_speaker(speaker_id: int, session: Session) -> DBSpeaker:
    db_speaker = read_db_speaker(speaker_id, session)
    session.delete(db_speaker)
    session.commit()
    return db_speaker

def read_db_events_for_speaker(speaker_id: int, session: Session) -> list[DBEvent]:
    return session.query(DBSpeaker.events).filter(DBSpeaker.id == speaker_id).all()