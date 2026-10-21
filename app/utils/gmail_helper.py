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
        
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().messages().list(userId='me', q="is:unread", maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            email_data = []
            for msg in messages:
                m = service.users().messages().get(userId='me', id=msg['id']).execute()
                snippet = m.get('snippet', '')
                email_data.append({"id": msg['id'], "subject": snippet[:30], "body": snippet})
                
            return email_data
        except Exception as e:
            logger.error(f"Error fetching unread emails: {e}")
            return []

    def search_emails(self, query: str, max_results: int = 5):
        if not self.creds:
            logger.warning("No Gmail credentials available. Searching mock email data.")
            mock_inbox = [
                {
                    "id": "mock_email_1",
                    "subject": "Internship Offer Letter - AI Engineering",
                    "sender": "recruiter@techcorp.com",
                    "body": "Congratulations! We are delighted to extend you an offer for the AI Engineering Internship position starting next month.",
                    "date": "2026-10-15"
                },
                {
                    "id": "mock_email_2",
                    "subject": "Meeting with Professor Regarding Project Milestone",
                    "sender": "professor@university.edu",
                    "body": "Let us schedule a discussion on Monday at 2 PM to go over your multi-agent architecture and thesis progress.",
                    "date": "2026-10-18"
                },
                {
                    "id": "mock_email_3",
                    "subject": "Urgent: Server Maintenance Scheduled Tonight",
                    "sender": "devops@company.com",
                    "body": "Server maintenance and upgrade window will take place tonight starting at 11 PM UTC.",
                    "date": "2026-10-20"
                },
                {
                    "id": "mock_email_4",
                    "subject": "Team Meeting Notes and Action Items",
                    "sender": "lead@company.com",
                    "body": "Here are the notes from last Monday's team sync regarding upcoming product release timelines.",
                    "date": "2026-10-14"
                }
            ]
            q_terms = [t.lower() for t in query.split() if len(t) > 2]
            if not q_terms:
                return mock_inbox[:max_results]
            
            matches = []
            for mail in mock_inbox:
                haystack = f"{mail['subject']} {mail['body']} {mail['sender']}".lower()
                if any(term in haystack for term in q_terms):
                    matches.append(mail)
                    
            return matches[:max_results] if matches else mock_inbox[:max_results]

        try:
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            email_data = []
            for msg in messages:
                m = service.users().messages().get(userId='me', id=msg['id']).execute()
                snippet = m.get('snippet', '')
                headers = {h['name'].lower(): h['value'] for h in m.get('payload', {}).get('headers', [])}
                email_data.append({
                    "id": msg['id'],
                    "subject": headers.get('subject', snippet[:30]),
                    "sender": headers.get('from', 'Unknown'),
                    "date": headers.get('date', ''),
                    "body": snippet
                })
                
            return email_data
        except Exception as e:
            logger.error(f"Error searching emails via Gmail API: {e}")
            return []

gmail_helper = GmailHelper()