"""
Script to make an event active for testing Q&A SSE streaming.
This sets the event's start_time to now and end_time to 2 hours from now.
"""
import asyncio
from datetime import datetime, timedelta, timezone
from db.connection import db_manager
from crud.event import get_event, update_event
from db.schemas import EventUpdate
import sys

async def activate_event(event_id: int):
    """Make an event active for testing"""
    async with db_manager.AsyncSessionLocal() as db:
        # Get the event
        event = await get_event(db, event_id)
        if not event:
            print(f"❌ Event {event_id} not found")
            return False
        
        # Set times
        now = datetime.now(timezone.utc)
        start_time = now - timedelta(minutes=5)  # Started 5 minutes ago
        end_time = now + timedelta(hours=2)      # Ends in 2 hours
        
        # Update event
        update_data = EventUpdate(
            start_time=start_time,
            end_time=end_time
        )
        
        updated_event = await update_event(db, event_id, update_data)
        
        if updated_event:
            print(f"✓ Event {event_id} '{updated_event.title}' is now ACTIVE")
            print(f"  Start: {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            print(f"  End:   {end_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
            return True
        else:
            print(f"❌ Failed to update event {event_id}")
            return False

async def list_events():
    """List all events with their active status"""
    async with db_manager.AsyncSessionLocal() as db:
        from crud.event import get_events
        events = await get_events(db)
        
        now = datetime.now(timezone.utc)
        
        print("\n📅 All Events:\n")
        print(f"{'ID':<5} {'Title':<40} {'Status':<15} {'Start Time':<20}")
        print("-" * 85)
        
        for event in sorted(events, key=lambda e: e.start_time):
            is_active = event.start_time <= now <= event.end_time
            status = "🟢 ACTIVE" if is_active else "⚫ Inactive"
            
            print(f"{event.id:<5} {event.title[:38]:<40} {status:<15} {event.start_time.strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python activate_event.py list              # List all events")
        print("  python activate_event.py <event_id>        # Activate specific event")
        print("\nExample:")
        print("  python activate_event.py 1                 # Make event 1 active")
        sys.exit(1)
    
    if sys.argv[1] == "list":
        asyncio.run(list_events())
    else:
        try:
            event_id = int(sys.argv[1])
            success = asyncio.run(activate_event(event_id))
            if success:
                print("\n✓ Event is now active! You can test SSE streaming.")
                print(f"  Public: http://localhost:8080/qa/event/{event_id}")
                print(f"  Moderator: http://localhost:8080/qa/moderator/event/{event_id}")
            sys.exit(0 if success else 1)
        except ValueError:
            print(f"❌ Invalid event ID: {sys.argv[1]}")
            sys.exit(1)
