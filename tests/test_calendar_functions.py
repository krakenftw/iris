from tools.calenders.googlecal.service import GoogleCalendarService
from datetime import datetime, timedelta
import time
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

def test_calendar_operations():
    """Test all Google Calendar operations: create, read, update, and delete events"""
    print("🔄 Initializing Google Calendar service...")
    
    try:
        # Initialize the service
        calendar_service = GoogleCalendarService()
        print("✅ Authentication successful!")
        
        # Step 1: Find an available time slot
        print("\n🔍 Finding available time slot...")
        tomorrow = datetime.now() + timedelta(days=1)
        tomorrow = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)  # 10 AM tomorrow
        
        time_slot = calendar_service.find_next_available_slot(
            duration_minutes=30,
            start_from=tomorrow,
            working_hours=(9, 17)
        )
        
        if not time_slot:
            print("❌ No available time slots found. Using tomorrow 10 AM regardless.")
            start_time = tomorrow
            end_time = tomorrow + timedelta(minutes=30)
        else:
            start_time, end_time = time_slot
            print(f"✅ Found available slot: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Step 2: Create a test event
        print("\n📅 Creating test event...")
        event = calendar_service.create_event(
            summary="Test Meeting from Iris",
            description="This is a test meeting created by Iris to demonstrate calendar functionality",
            start_time=start_time,
            end_time=end_time,
            attendees=["test@example.com"],
            location="Virtual"
        )
        
        event_id = event.get('id')
        event_link = event.get('htmlLink')
        
        print(f"✅ Created event: {event.get('summary')}")
        print(f"📆 Time: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
        print(f"🔗 Link: {event_link}")
        print(f"🆔 ID: {event_id}")
        
        # Wait a moment to allow API to process
        print("\n⏳ Waiting a moment before updating the event...")
        time.sleep(2)
        
        # Step 3: Update the event
        print("\n🔄 Updating event...")
        
        # Move the meeting 30 minutes later
        new_start_time = start_time + timedelta(minutes=30)
        new_end_time = end_time + timedelta(minutes=30)
        
        updated_event = calendar_service.update_event(
            event_id=event_id,
            summary="Updated Test Meeting from Iris",
            description="This meeting was updated to demonstrate the update functionality",
            start=new_start_time,
            end=new_end_time,
            location="Virtual Conference Room"
        )
        
        print(f"✅ Updated event: {updated_event.get('summary')}")
        print(f"📆 New time: {new_start_time.strftime('%Y-%m-%d %H:%M')} - {new_end_time.strftime('%H:%M')}")
        
        # Wait a moment to allow API to process
        print("\n⏳ Waiting a moment before checking availability...")
        time.sleep(2)
        
        # Step 4: Check availability
        print("\n🔍 Checking availability for the updated time slot...")
        is_available = calendar_service.check_availability(new_start_time, new_end_time)
        print(f"👉 Time slot is {'available' if is_available else 'not available (as expected)'}")
        
        # Wait a moment to allow API to process
        print("\n⏳ Waiting a moment before deleting the event...")
        time.sleep(2)
        
        # Step 5: Delete the event
        print("\n🗑️ Deleting event...")
        
        # Ask for confirmation before deleting
        confirmation = input("Type 'yes' to delete the test event (recommended to clean up): ")
        
        if confirmation.lower() == 'yes':
            calendar_service.delete_event(event_id)
            print("✅ Event deleted successfully")
            
            # Verify the event is deleted by checking availability
            time.sleep(2)
            is_available_after_delete = calendar_service.check_availability(new_start_time, new_end_time)
            print(f"👉 Time slot is now {'available (deletion confirmed)' if is_available_after_delete else 'still not available (unexpected)'}")
        else:
            print("❌ Event deletion skipped")
        
        print("\n✅ All calendar operations tested successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_calendar_operations() 