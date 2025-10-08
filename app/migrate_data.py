import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db.models import Base, Event, Speaker, PrayerTime, Sponsor, event_speakers


# Create synchronous engine
database_url = os.getenv('DATABASE_URL')
if database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg2://')

print(f"Connecting to: {database_url}")

engine = create_engine(database_url)
SessionLocal = sessionmaker(bind=engine)

def migrate_data():
    # Create tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    
    try:
        # Clear existing data
        print("Clearing existing data...")
        session.execute(text("DELETE FROM event_speakers"))
        session.execute(text("DELETE FROM events"))
        session.execute(text("DELETE FROM speakers"))
        session.execute(text("DELETE FROM prayer_times"))
        session.execute(text("DELETE FROM sponsors"))
        session.commit()
        
        # Add speakers
        print("Adding speakers...")
        for speaker_data in SPEAKERS:
            speaker = Speaker(
                id=speaker_data.id,
                name=speaker_data.name,
                image_url=speaker_data.image_url,
                bio=speaker_data.bio
            )
            session.add(speaker)
        session.commit()
        print(f"Added {len(SPEAKERS)} speakers")
        
        # Add events
        print("Adding events...")
        for event_data in SESSIONS:
            event = Event(
                id=event_data.id,
                title=event_data.title,
                description=event_data.description,
                start_time=event_data.start_time,
                end_time=event_data.end_time,
                location=event_data.location,
                category=event_data.category.value
            )
            session.add(event)
        session.commit()
        print(f"Added {len(SESSIONS)} events")
        
        # Add event-speaker relationships
        print("Adding event-speaker relationships...")
        for event_data in SESSIONS:
            if event_data.speakers:
                for speaker_id in event_data.speakers:
                    session.execute(text(
                        "INSERT INTO event_speakers (event_id, speaker_id) VALUES (:event_id, :speaker_id)"
                    ), {"event_id": event_data.id, "speaker_id": speaker_id})
        session.commit()
        
        # Add prayer times
        print("Adding prayer times...")
        for prayer_data in PRAYER_TIMES:
            prayer = PrayerTime(
                id=prayer_data.id,
                name=prayer_data.name.value,
                time=prayer_data.time,
                iqama=prayer_data.iqama
            )
            session.add(prayer)
        session.commit()
        print(f"Added {len(PRAYER_TIMES)} prayer times")
        
        # Add sponsors
        print("Adding sponsors...")
        for sponsor_data in SPONSORS:
            sponsor = Sponsor(
                id=sponsor_data.id,
                name=sponsor_data.name,
                image_url=sponsor_data.image_url,
                description=sponsor_data.description,
                website=sponsor_data.website,
                facebook=sponsor_data.facebook,
                instagram=sponsor_data.instagram,
                twitter=sponsor_data.twitter
            )
            session.add(sponsor)
        session.commit()
        print(f"Added {len(SPONSORS)} sponsors")
        
        # Verify data
        print("\nVerifying data...")
        speaker_count = session.execute(text("SELECT COUNT(*) FROM speakers")).scalar()
        event_count = session.execute(text("SELECT COUNT(*) FROM events")).scalar()
        prayer_count = session.execute(text("SELECT COUNT(*) FROM prayer_times")).scalar()
        sponsor_count = session.execute(text("SELECT COUNT(*) FROM sponsors")).scalar()
        
        print(f"Speakers: {speaker_count}")
        print(f"Events: {event_count}")
        print(f"Prayer times: {prayer_count}")
        print(f"Sponsors: {sponsor_count}")
        
        print("\nMigration completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    migrate_data()