import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.utils.logger import logger

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']

class GmailHelper:
    def __init__(self):
        self.creds = None
        self._authenticate()

    def _authenticate(self):
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if os.path.exists('credentials.json'):
                    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                    self.creds = flow.run_local_server(port=0)
                    with open('token.json', 'w') as token:
                        token.write(self.creds.to_json())
                else:
                    logger.warning("credentials.json not found. Gmail API calls will run in Mock Mode.")

    def fetch_unread_emails(self, max_results: int = 5):
        if not self.creds:
            # Fallback Mock Data for testing when credentials.json is missing
            return [
                {"id": "1", "subject": "Urgent: Server Maintenance", "body": "Server upgrade scheduled tonight at 11 PM."},
                {"id": "2", "subject": "Coffee catchup", "body": "Hey, let us meet at 4 PM in the cafeteria."},
                {"id": "3", "subject": "YOU WON $10,000", "body": "Click link now to claim fast!"}
            ]
        
        service = build('gmail', 'v1', credentials=self.creds)
        results = service.users().messages().list(userId='me', q="is:unread", maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        email_data = []
        for msg in messages:
            m = service.users().messages().get(userId='me', id=msg['id']).execute()
            snippet = m.get('snippet', '')
            email_data.append({"id": msg['id'], "subject": snippet[:30], "body": snippet})
            
        return email_data

gmail_helper = GmailHelper()