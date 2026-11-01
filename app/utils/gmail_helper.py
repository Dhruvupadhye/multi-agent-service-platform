import os.path
import time
import base64
from email.message import EmailMessage
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
                {
                    "id": "mock_unread_1",
                    "subject": "Urgent: Server Maintenance Scheduled Tonight",
                    "sender": "devops@company.com",
                    "date": "2026-10-20 09:30 AM",
                    "body": "Server upgrade and security patching scheduled tonight at 11 PM. Expected downtime is 30 minutes."
                },
                {
                    "id": "mock_unread_2",
                    "subject": "Coffee catchup and project discussion",
                    "sender": "sarah.lead@company.com",
                    "date": "2026-10-20 11:15 AM",
                    "body": "Hey! Let us meet at 4 PM in the 3rd floor cafeteria to align on the multi-agent UI architecture."
                },
                {
                    "id": "mock_unread_3",
                    "subject": "Quarterly OKR Planning Session Invitation",
                    "sender": "director@company.com",
                    "date": "2026-10-19 03:00 PM",
                    "body": "Please review the attached Q4 planning deck and prepare your team objectives by this Friday."
                }
            ]
        
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            results = service.users().messages().list(userId='me', q="is:unread", maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            email_data = []
            for msg in messages:
                m = service.users().messages().get(userId='me', id=msg['id']).execute()
                snippet = m.get('snippet', '')
                headers = {h['name'].lower(): h['value'] for h in m.get('payload', {}).get('headers', [])}
                email_data.append({
                    "id": msg['id'],
                    "subject": headers.get('subject', snippet[:40] or "No Subject"),
                    "sender": headers.get('from', 'Unknown Sender'),
                    "date": headers.get('date', ''),
                    "body": snippet
                })
                
            return email_data
        except Exception as e:
            logger.error(f"Error fetching unread emails: {e}")
            return []

    def search_emails(self, query: str = "", max_results: int = 10):
        if not self.creds:
            logger.warning("No Gmail credentials available. Searching mock email data.")
            mock_inbox = [
                {
                    "id": "mock_email_1",
                    "subject": "Internship Offer Letter - AI Engineering",
                    "sender": "recruiter@techcorp.com",
                    "body": "Congratulations! We are delighted to extend you an offer for the AI Engineering Internship position starting next month.",
                    "date": "2026-10-15 10:00 AM"
                },
                {
                    "id": "mock_email_2",
                    "subject": "Meeting with Professor Regarding Project Milestone",
                    "sender": "professor@university.edu",
                    "body": "Let us schedule a discussion on Monday at 2 PM to go over your multi-agent architecture and thesis progress.",
                    "date": "2026-10-18 02:30 PM"
                },
                {
                    "id": "mock_email_3",
                    "subject": "Urgent: Server Maintenance Scheduled Tonight",
                    "sender": "devops@company.com",
                    "body": "Server maintenance and upgrade window will take place tonight starting at 11 PM UTC.",
                    "date": "2026-10-20 09:30 AM"
                },
                {
                    "id": "mock_email_4",
                    "subject": "Team Meeting Notes and Action Items",
                    "sender": "lead@company.com",
                    "body": "Here are the notes from last Monday's team sync regarding upcoming product release timelines.",
                    "date": "2026-10-14 05:00 PM"
                },
                {
                    "id": "mock_email_5",
                    "subject": "Client Presentation Feedback and Next Steps",
                    "sender": "client-success@client.com",
                    "body": "Great presentation yesterday! The client executive board is impressed with the automated workflow demo.",
                    "date": "2026-10-12 11:20 AM"
                }
            ]
            q_clean = query.strip().lower()
            if not q_clean:
                return mock_inbox[:max_results]
                
            q_terms = [t for t in q_clean.split() if len(t) > 1]
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
            q = query if query.strip() else "label:INBOX"
            results = service.users().messages().list(userId='me', q=q, maxResults=max_results).execute()
            messages = results.get('messages', [])
            
            email_data = []
            for msg in messages:
                m = service.users().messages().get(userId='me', id=msg['id']).execute()
                snippet = m.get('snippet', '')
                headers = {h['name'].lower(): h['value'] for h in m.get('payload', {}).get('headers', [])}
                email_data.append({
                    "id": msg['id'],
                    "subject": headers.get('subject', snippet[:40] or "No Subject"),
                    "sender": headers.get('from', 'Unknown Sender'),
                    "date": headers.get('date', ''),
                    "body": snippet
                })
                
            return email_data
        except Exception as e:
            logger.error(f"Error searching emails via Gmail API: {e}")
            return []

    def send_email(self, to: str, subject: str, body: str) -> dict:
        """Send an email using Gmail API or return a structured confirmation in Mock Mode."""
        if not self.creds:
            logger.warning(f"No Gmail credentials available. Simulating email dispatch to {to}.")
            return {
                "status": "sent",
                "id": f"mock_sent_{int(time.time())}",
                "to": to,
                "subject": subject,
                "message": f"Email successfully dispatched to {to} (Mock Mode active)."
            }

        try:
            msg = EmailMessage()
            msg.set_content(body)
            msg['To'] = to
            msg['Subject'] = subject
            
            raw_bytes = msg.as_bytes()
            raw_b64 = base64.urlsafe_b64encode(raw_bytes).decode()
            
            service = build('gmail', 'v1', credentials=self.creds)
            sent_msg = service.users().messages().send(userId='me', body={'raw': raw_b64}).execute()
            msg_id = sent_msg.get('id', f"sent_{int(time.time())}")
            logger.info(f"Email sent successfully. Message ID: {msg_id}")
            return {
                "status": "sent",
                "id": msg_id,
                "to": to,
                "subject": subject,
                "message": f"Email successfully dispatched to {to}."
            }
        except Exception as e:
            logger.error(f"Error sending email via Gmail API: {e}")
            raise RuntimeError(f"Gmail dispatch failed: {str(e)}")

gmail_helper = GmailHelper()
