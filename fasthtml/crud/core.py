from typing import List
from db.data import SESSIONS, SPEAKERS, SPONSORS
from db.schemas import EventOut, SpeakerOut, SponsorOut


def get_session(event_id: int) -> EventOut:
    return next((event for event in SESSIONS if event.id == event_id), None)

def get_speaker(speaker_ids: int) -> SpeakerOut:
    return next((speaker for speaker in SPEAKERS if speaker.id == speaker_ids), None)

def get_sponsor(sponsor_id: int) -> SponsorOut:
    return next((sponsor for sponsor in SPONSORS if sponsor.id == sponsor_id), None)