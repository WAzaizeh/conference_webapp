from sqlalchemy.orm import selectinload
from .sync_connection import sync_db_manager
from .models import Event, Speaker, PrayerTime, Sponsor
from .schemas import Event, Speaker, PrayerTime, Sponsor, EVENT_CATEGORY, PRAYER_NAME

class DatabaseService:
    """Service for database operations"""
    
    def __init__(self):
        self.db_manager = sync_db_manager

    async def get_all_events(self):
        """Get all events with speakers"""
        async with self.db_manager.AsyncSessionLocal() as session:
            try:
                events = await session.execute(
                    session.query(Event).options(selectinload(Event.speakers))
                )
                events = events.scalars().all()
                return [
                    Event(
                        id=event.id,
                        title=event.title,
                        description=event.description,
                        start_time=event.start_time,
                        end_time=event.end_time,
                        location=event.location,
                        category=EVENT_CATEGORY(event.category),
                        speakers=[speaker.id for speaker in event.speakers]
                    ) for event in events
                ]
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_all_speakers(self):
        """Get all speakers"""
        async with self.db_manager.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    session.query(Speaker)
                )
                speakers = result.scalars().all()
                return [
                    Speaker(
                        id=speaker.id,
                        name=speaker.name,
                        image_url=speaker.image_url,
                        bio=speaker.bio
                    ) for speaker in speakers
                ]
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_all_prayer_times(self):
        """Get all prayer times"""
        async with self.db_manager.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    session.query(PrayerTime)
                )
                prayer_times = result.scalars().all()
                return [
                    PrayerTime(
                        id=prayer.id,
                        name=PRAYER_NAME(prayer.name),
                        time=prayer.time,
                        iqama=prayer.iqama
                    ) for prayer in prayer_times
                ]
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_all_sponsors(self):
        """Get all sponsors"""
        async with self.db_manager.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    session.query(Sponsor)
                )
                sponsors = result.scalars().all()
                return [
                    Sponsor(
                        id=sponsor.id,
                        name=sponsor.name,
                        image_url=sponsor.image_url,
                        description=sponsor.description,
                        website=sponsor.website,
                        facebook=sponsor.facebook,
                        instagram=sponsor.instagram,
                        twitter=sponsor.twitter
                    ) for sponsor in sponsors
                ]
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_speaker_by_id(self, speaker_id: int):
        """Get speaker by ID"""
        async with self.db_manager.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    session.query(Speaker).filter(Speaker.id == speaker_id)
                )
                speaker = result.scalar_one_or_none()
                if speaker:
                    return Speaker(
                        id=speaker.id,
                        name=speaker.name,
                        image_url=speaker.image_url,
                        bio=speaker.bio
                    )
                return None
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_event_by_id(self, event_id: int):
        """Get event by ID"""
        async with self.db_manager.AsyncSessionLocal() as session:
            try:
                result = await session.execute(
                    session.query(Event)
                    .options(selectinload(Event.speakers))
                    .filter(Event.id == event_id)
                )
                event = result.scalar_one_or_none()
                if event:
                    return Event(
                        id=event.id,
                        title=event.title,
                        description=event.description,
                        start_time=event.start_time,
                        end_time=event.end_time,
                        location=event.location,
                        category=EVENT_CATEGORY(event.category),
                        speakers=[speaker.id for speaker in event.speakers]
                    )
                return None
            except Exception as e:
                await session.rollback()
                raise e

# Global service instance
db_service = DatabaseService()