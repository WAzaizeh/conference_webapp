from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from db.core import get_db, NotFoundError
from db.models import (
    SpeakerOut,
    SpeakerCreate,
    SpeakerUpdate,
    create_db_speaker,
    delete_db_speaker,
    read_db_speaker,
    update_db_speaker,
    read_db_events_for_speaker
)


router = APIRouter(
    prefix='/speakers',
)


@router.post('')
def create_speaker(
    speaker: SpeakerCreate, db: Session = Depends(get_db)
) -> SpeakerOut:
    db_speaker = create_db_speaker(speaker, db)
    return SpeakerOut(**db_speaker.__dict__)


@router.get('/{speaker_id}')
def read_speaker(speaker_id: int, db: Session = Depends(get_db)) -> SpeakerOut:
    try:
        db_speaker = read_db_speaker(speaker_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return SpeakerOut(**db_speaker.__dict__)


@router.put('/{speaker_id}')
def update_speaker(
    speaker_id: int,
    speaker: SpeakerUpdate,
    db: Session = Depends(get_db),
) -> SpeakerOut:
    try:
        db_speaker = update_db_speaker(speaker_id, speaker, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return SpeakerOut(**db_speaker.__dict__)


@router.delete('/{speaker_id}')
def delete_speaker(speaker_id: int, db: Session = Depends(get_db)) -> SpeakerOut:
    try:
        db_speaker = delete_db_speaker(speaker_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return SpeakerOut(**db_speaker.__dict__)

@router.get('/{speaker_id}/events')
def read_events_for_speaker(speaker_id: int, db: Session = Depends(get_db)):
    try:
        db_events = read_db_events_for_speaker(speaker_id, db)
    except NotFoundError as e:
        raise HTTPException(status_code=404) from e
    return db_events