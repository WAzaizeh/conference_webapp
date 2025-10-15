import json
from datetime import datetime
from zoneinfo import ZoneInfo
from db.sync_connection import get_db
from db.models import Event, Speaker, PrayerTime, event_speakers

def parse_datetime(dt_string):
    """Parse ISO format datetime string and convert to CDT (naive)"""
    if dt_string:
        # Parse the ISO string (assumes UTC if no timezone specified)
        dt = datetime.fromisoformat(dt_string.replace('Z', '+00:00'))
        
        # If timezone-naive, assume it's already in CDT
        if dt.tzinfo is None:
            return dt
        
        # If timezone-aware, convert to CDT and make naive
        cdt = ZoneInfo('America/Chicago')
        return dt.astimezone(cdt).replace(tzinfo=None)
    
    return None

def sync_data_from_json(json_file='conference_data.json'):
    """Sync database with JSON data"""
    
    # Load JSON data
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    with get_db() as db:
        print("Starting data sync...")
        
        # Clear existing data - ORDER MATTERS!
        print("Clearing existing data...")
        # First, clear the association table
        db.execute(event_speakers.delete())
        # Then delete the related tables
        db.query(Event).delete()
        db.query(Speaker).delete()
        db.query(PrayerTime).delete()
        db.commit()
        
        # Insert speakers
        print(f"Inserting {len(data['speakers'])} speakers...")
        speaker_map = {}
        for speaker_data in data['speakers']:
            speaker = Speaker(
                id=speaker_data['id'],
                name=speaker_data['name'],
                image_url=speaker_data.get('image_url') or None,
                bio=speaker_data.get('bio') or None
            )
            db.add(speaker)
            speaker_map[speaker_data['id']] = speaker
        db.commit()
        
        # Insert events
        print(f"Inserting {len(data['events'])} events...")
        event_map = {}
        for event_data in data['events']:
            event = Event(
                id=event_data['id'],
                title=event_data['title'],
                description=event_data.get('description') or None,
                start_time=parse_datetime(event_data['start_time']),
                end_time=parse_datetime(event_data['end_time']),
                location=event_data.get('location') or None,
                category=event_data.get('category', 'MAIN'),
                is_qa_active=bool(event_data.get('is_qa_active'))
            )
            db.add(event)
            event_map[event_data['id']] = event
        db.commit()
        
        # Link events and speakers
        print(f"Linking {len(data['event_speakers'])} event-speaker relationships...")
        for link in data['event_speakers']:
            event = event_map.get(link['event_id'])
            speaker = speaker_map.get(link['speaker_id'])
            if event and speaker:
                event.speakers.append(speaker)
        db.commit()
        
        # Insert prayer times
        print(f"Inserting {len(data['prayer_times'])} prayer times...")
        for prayer_data in data['prayer_times']:
            prayer = PrayerTime(
                name=prayer_data['name'],
                time=prayer_data.get('time') or None,
                iqama=prayer_data.get('iqama') or None
            )
            db.add(prayer)
        db.commit()
        
        print("✅ Data sync completed successfully!")
        
        # Print summary
        print("\n📊 Summary:")
        print(f"  - Events: {db.query(Event).count()}")
        print(f"  - Speakers: {db.query(Speaker).count()}")
        print(f"  - Prayer Times: {db.query(PrayerTime).count()}")

if __name__ == "__main__":
    try:
        sync_data_from_json()
    except Exception as e:
        print(f"❌ Error during sync: {str(e)}")
        raise