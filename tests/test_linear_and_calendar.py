from tools.linear.service import LinearService
from tools.calenders.googlecal.service import GoogleCalendarService
from datetime import datetime, timedelta
import dotenv
import os

# Load environment variables
dotenv.load_dotenv()

def test_linear_and_calendar_integration():
    """Test Linear and Google Calendar integration by creating an issue and scheduling a meeting for it"""
    print("🚀 Testing Linear and Google Calendar Integration")
    
    try:
        # Initialize services
        print("\n🔄 Initializing services...")
        linear_service = LinearService()
        calendar_service = GoogleCalendarService()
        print("✅ Services initialized successfully")
        
        # Step 1: Create a Linear issue
        print("\n📝 Creating Linear issue...")
        issue = linear_service.create_urgent_issue(
            title="AI Team Integration Testing",
            description="""
This is a test issue created to verify the integration between Linear and Google Calendar.
Priority: High
Due: Today
            """.strip(),
            team_name="Engineering",  # Replace with actual team name
            assignee_email="test@example.com"  # Replace with actual email
        )
        
        print(f"✅ Created Linear issue: {issue['title']}")
        print(f"🔗 URL: {issue.get('url', 'URL not available')}")
        print(f"👤 Assignee: {issue['assignee']['name'] if issue.get('assignee') else 'Unassigned'}")
        print(f"⚡ Priority: {issue['priority']}/4")
        
        # Step 2: Find an available time slot for a meeting
        print("\n🔍 Finding available time slot...")
        today = datetime.now()
        end_of_day = today.replace(hour=17, minute=0, second=0, microsecond=0)
        
        time_slot = calendar_service.find_next_available_slot(
            duration_minutes=30,
            start_from=today,
            working_hours=(9, 17)
        )
        
        if not time_slot:
            print("❌ No available time slots found today. Using tomorrow 10 AM.")
            tomorrow = today + timedelta(days=1)
            start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
            end_time = start_time + timedelta(minutes=30)
        else:
            start_time, end_time = time_slot
            print(f"✅ Found available slot: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
        
        # Step 3: Schedule a meeting for this issue
        print("\n📅 Scheduling meeting for this issue...")
        event = calendar_service.create_event(
            summary=f"Meeting for {issue['title']}",
            description=f"""
Discuss the issue: {issue['title']}
Linear URL: {issue.get('url', 'URL not available')}

Description:
{issue.get('description', 'No description available')}
            """.strip(),
            start_time=start_time,
            end_time=end_time,
            attendees=["test@example.com"],  # Add actual attendees
            location="Virtual"
        )
        
        event_id = event.get('id')
        event_link = event.get('htmlLink')
        
        print(f"✅ Scheduled meeting: {start_time.strftime('%Y-%m-%d %H:%M')} - {end_time.strftime('%H:%M')}")
        print(f"🔗 Meeting link: {event_link}")
        
        # Ask if user wants to clean up
        cleanup = input("\nDo you want to delete the test calendar event? (yes/no): ")
        if cleanup.lower() == 'yes':
            print("\n🗑️ Deleting test calendar event...")
            calendar_service.delete_event(event_id)
            print("✅ Calendar event deleted successfully")
        
        print("\n✅ Linear and Google Calendar integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_linear_and_calendar_integration() 