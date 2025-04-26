from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import os.path
import pickle
import os

class GoogleCalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    TOKEN_FILE = 'token.pickle'
    CREDENTIALS_FILE = 'credentials.json'

    def __init__(self):
        """Initialize Google Calendar service with API key"""
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        """Authenticate with Google Calendar API using OAuth 2.0"""
        if os.path.exists(self.TOKEN_FILE):
            with open(self.TOKEN_FILE, 'rb') as token:
                self.creds = pickle.load(token)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                # For desktop applications, we don't need to specify redirect_uri
                # This avoids the redirect_uri_mismatch error
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_FILE, 
                    self.SCOPES
                )
                
                # Use local_server flow for desktop applications
                self.creds = flow.run_local_server(
                    port=0,  # Use a random available port
                    success_message="Authentication successful! You can close this window."
                )

            with open(self.TOKEN_FILE, 'wb') as token:
                pickle.dump(self.creds, token)

        # Disable cache since it's causing oauth2client issues
        os.environ['GOOGLE_API_USE_CLIENT_CERTIFICATE'] = 'false'
        self.service = build('calendar', 'v3', credentials=self.creds, cache_discovery=False)

    def create_event(self, summary, description, start_time, end_time, attendees=None, location=None):
        """Create a calendar event

        Args:
            summary (str): Event title
            description (str): Event description
            start_time (datetime): Event start time
            end_time (datetime): Event end time
            attendees (list, optional): List of attendee email addresses
            location (str, optional): Event location

        Returns:
            dict: Created event details
        """
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'UTC',
            },
        }

        if attendees:
            event['attendees'] = [{'email': email} for email in attendees]
        if location:
            event['location'] = location

        return self.service.events().insert(calendarId='primary', body=event).execute()

    def check_availability(self, start_time, end_time):
        """Check if there are any conflicts in the given time range

        Args:
            start_time (datetime): Start of time range
            end_time (datetime): End of time range

        Returns:
            bool: True if time slot is available, False otherwise
        """
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        return len(events_result.get('items', [])) == 0

    def find_next_available_slot(self, duration_minutes, start_from=None, working_hours=(9, 17)):
        """Find the next available time slot of specified duration

        Args:
            duration_minutes (int): Required duration in minutes
            start_from (datetime, optional): Start searching from this time
            working_hours (tuple, optional): Working hours as (start_hour, end_hour)

        Returns:
            tuple: (start_time, end_time) of available slot, or None if not found
        """
        if start_from is None:
            start_from = datetime.now()

        current_time = start_from
        max_days_to_check = 14  # Limit search to next 2 weeks

        for _ in range(max_days_to_check):
            # Reset to working hours start if outside working hours
            if current_time.hour < working_hours[0]:
                current_time = current_time.replace(hour=working_hours[0], minute=0)
            elif current_time.hour >= working_hours[1]:
                current_time = (current_time + timedelta(days=1)).replace(hour=working_hours[0], minute=0)

            end_time = current_time + timedelta(minutes=duration_minutes)
            
            if self.check_availability(current_time, end_time):
                return current_time, end_time

            current_time += timedelta(minutes=30)  # Try next 30-minute slot

        return None

    def update_event(self, event_id, **kwargs):
        """Update an existing calendar event

        Args:
            event_id (str): ID of the event to update
            **kwargs: Event fields to update

        Returns:
            dict: Updated event details
        """
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
        
        for key, value in kwargs.items():
            if key in ['start', 'end']:
                event[key]['dateTime'] = value
            else:
                event[key] = value

        return self.service.events().update(calendarId='primary', eventId=event_id, body=event).execute()

    def delete_event(self, event_id):
        """Delete a calendar event

        Args:
            event_id (str): ID of the event to delete
        """
        self.service.events().delete(calendarId='primary', eventId=event_id).execute()
