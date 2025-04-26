from tools.calenders.googlecal.service import GoogleCalendarService
from datetime import datetime, timedelta
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

def test_calendar_auth():
    """Test Google Calendar authentication and basic functionality"""
    print("Initializing Google Calendar service...")
    
    try:
        # Initialize the service (this will trigger OAuth flow if needed)
        calendar_service = GoogleCalendarService()
        print("✅ Authentication successful!")
        
        # Test listing upcoming events
        print("\nChecking upcoming events...")
        now = datetime.utcnow()
        end_time = now + timedelta(days=7)  # Looking 7 days ahead
        
        events_result = calendar_service.service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=end_time.isoformat() + 'Z',
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if events:
            print(f"Found {len(events)} upcoming events:")
            for event in events[:3]:  # Show up to 3 events
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"- {start}: {event['summary']}")
            if len(events) > 3:
                print(f"  ...and {len(events) - 3} more")
        else:
            print("No upcoming events found.")
            
        # Test finding available time slot
        print("\nFinding next available time slot...")
        time_slot = calendar_service.find_next_available_slot(
            duration_minutes=30,
            working_hours=(9, 17)
        )
        
        if time_slot:
            start, end = time_slot
            print(f"✅ Found available slot: {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%H:%M')}")
        else:
            print("❌ No available time slots found in the next 14 days.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        print("\nPlease follow the instructions in google_oauth_setup.md to configure your OAuth credentials.")
        return False

if __name__ == "__main__":
    test_calendar_auth() 