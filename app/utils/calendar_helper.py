import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.utils.logger import logger

# We request permission specifically to manage calendar events
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
TOKEN_FILE = 'calendar_token.json'

class CalendarHelper:
    def __init__(self):
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        # Look for the dedicated calendar token
        if os.path.exists(TOKEN_FILE):
            self.creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
            
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if os.path.exists('credentials.json'):
                    # This will trigger the browser popup for permission
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    
                    # Save the new token for future runs
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(self.creds.to_json())
                else:
                    logger.warning("credentials.json not found. Calendar API will not work.")

    def create_event(self, summary: str, start_time_iso: str, end_time_iso: str, description: str = ""):
        if not self.creds:
            logger.warning("No credentials available to create calendar event. Returning mock event for testing.")
            return {
                "id": "mock_event_id",
                "summary": summary,
                "htmlLink": "https://calendar.google.com/calendar/r/eventedit",
                "status": "confirmed"
            }

        try:
            service = build('calendar', 'v3', credentials=self.creds)
            
            event = {
                'summary': summary,
                'description': description,
                'start': {
                    'dateTime': start_time_iso,
                    'timeZone': 'Asia/Kolkata',  # Explicitly enforce IST
                },
                'end': {
                    'dateTime': end_time_iso,
                    'timeZone': 'Asia/Kolkata',  # Explicitly enforce IST
                },
            }

            event_result = service.events().insert(calendarId='primary', body=event).execute()
            logger.info(f"Event created successfully: {event_result.get('htmlLink')}")
            return event_result
        except Exception as e:
            logger.error(f"Error creating calendar event: {e}")
            return None

    def list_events(self, time_min_iso: str = None, time_max_iso: str = None, max_results: int = 10):
        if not self.creds:
            logger.warning("No credentials available. Returning mock calendar events for testing.")
            from datetime import datetime, timedelta
            now = datetime.now()
            return [
                {
                    "id": "mock_event_1",
                    "summary": "Team Sync & Status Review",
                    "start": {"dateTime": f"{now.strftime('%Y-%m-%d')}T10:00:00+05:30"},
                    "end": {"dateTime": f"{now.strftime('%Y-%m-%d')}T11:00:00+05:30"},
                    "description": "Weekly status review with the engineering team.",
                    "htmlLink": "https://calendar.google.com/calendar/r"
                },
                {
                    "id": "mock_event_2",
                    "summary": "Project Milestone Meeting with Professor",
                    "start": {"dateTime": f"{(now + timedelta(days=1)).strftime('%Y-%m-%d')}T14:00:00+05:30"},
                    "end": {"dateTime": f"{(now + timedelta(days=1)).strftime('%Y-%m-%d')}T15:00:00+05:30"},
                    "description": "Review architecture and progress of multi-agent platform.",
                    "htmlLink": "https://calendar.google.com/calendar/r"
                }
            ]

        try:
            service = build('calendar', 'v3', credentials=self.creds)
            kwargs = {
                'calendarId': 'primary',
                'maxResults': max_results,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            if time_min_iso:
                kwargs['timeMin'] = time_min_iso
            if time_max_iso:
                kwargs['timeMax'] = time_max_iso
                
            events_result = service.events().list(**kwargs).execute()
            return events_result.get('items', [])
        except Exception as e:
            logger.error(f"Error fetching calendar events: {e}")
            return []

calendar_helper = CalendarHelper()