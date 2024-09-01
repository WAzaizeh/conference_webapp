from fastapi import APIRouter, HTTPException, Request
from fastapi.params import Depends
from sqlalchemy.orm import Session
from db.core import NotFoundError, get_db
from routers.limiter import limiter
from db.schemas import (
    EventOut,
    EventCreate,
    EventUpdate,
    SpeakerOut,
)
from crud.common import get_db_event
from crud.events import (
    create_db_event,
    update_db_event,
    delete_db_event,
    read_db_event_speakers
)


router = APIRouter(
    prefix='/events',
)


@router.post('/')
@limiter.limit('1/second')
def create_event(
    request: Request, event: EventCreate, db: Session = Depends(get_db)
) -> EventOut:
    db_event = create_db_event(event, db)
    return db_event


@router.get('/{event_id}')
@limiter.limit('10/second')
def read_event(request: Request, event_id: int, db: Session = Depends(get_db)) -> EventOut:
    try:
        db_event = get_db_event(event_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_event


@router.get('/{event_id}/speakers')
@limiter.limit('10/second')
def read_event_speakers(
    request: Request, event_id: int, db: Session = Depends(get_db)
) -> list[SpeakerOut]:
    try:
        speakers = read_db_event_speakers(event_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return speakers


@router.put('/{event_id}')
@limiter.limit('1/second')
def update_event(request: Request, event_id: int, event: EventUpdate, db: Session = Depends(get_db)) -> EventOut:
    try:
        db_event = update_db_event(event_id, event, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_event


@router.delete('/{event_id}')
@limiter.limit('1/second')
def delete_event(request: Request, event_id: int, db: Session = Depends(get_db)) -> EventOut:
    try:
        db_event = delete_db_event(event_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_event