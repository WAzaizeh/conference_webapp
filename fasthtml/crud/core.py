from typing import List
from db.schemas import EventOut, SpeakerOut
from db.data import SESSIONS, SPEAKERS

def get_session(event_id: int) -> EventOut:
    return next((event for event in SESSIONS if event.id == event_id), None)

def get_speaker(speaker_ids: List[int]) -> SpeakerOut:
    return next((speaker for speaker in SPEAKERS if speaker.id == speaker_ids), None)