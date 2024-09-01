from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from db.core import NotFoundError, get_db
from routers.limiter import limiter
from db.schemas import (
    SpeakerOut,
    SpeakerCreate,
    SpeakerUpdate,
    EventOut,
)
from crud.common import get_db_speaker
from crud.speakers import (
    create_db_speaker,
    update_db_speaker,
    delete_db_speaker,
    read_db_speaker_events,
)


router = APIRouter(
    prefix='/speakers',
)


@router.post('/')
@limiter.limit('1/second')
def create_speaker(request: Request, speaker: SpeakerCreate, db: Session = Depends(get_db)) -> SpeakerOut:
    db_speaker = create_db_speaker(speaker, db)
    return db_speaker


@router.get('/{speaker_id}')
@limiter.limit('10/second')
def read_speaker(request: Request, speaker_id: int, db: Session = Depends(get_db)) -> SpeakerOut:
    try:
        db_speaker = get_db_speaker(speaker_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_speaker


@router.get('/{speaker_id}/speakers')
@limiter.limit('10/second')
def read_speaker_events(request: Request, speaker_id: int, db: Session = Depends(get_db)) -> list[EventOut]:
    try:
        events = read_db_speaker_events(speaker_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return events


@router.put('/{speaker_id}')
@limiter.limit('1/second')
def update_speaker(request: Request, speaker_id: int, speaker: SpeakerUpdate, db: Session = Depends(get_db)) -> SpeakerOut:
    try:
        db_speaker = update_db_speaker(speaker_id, speaker, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_speaker


@router.delete('/{speaker_id}')
@limiter.limit('1/second')
def delete_speaker(request: Request, speaker_id: int, db: Session = Depends(get_db)) -> SpeakerOut:
    try:
        db_speaker = delete_db_speaker(speaker_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_speaker