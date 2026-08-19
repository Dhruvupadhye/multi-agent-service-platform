import os
from app.config import settings
from twilio.rest import Client
from dotenv import load_dotenv
from app.utils.logger import logger

load_dotenv()  # Load environment variables from .env file

class NotificationService:
    def __init__(self):
    # Fetching directly from your validated config!
        self.sid = settings.TWILIO_ACCOUNT_SID
        self.auth_token = settings.TWILIO_AUTH_TOKEN
        self.from_whatsapp = settings.TWILIO_WHATSAPP_NUMBER
        self.to_whatsapp = settings.USER_WHATSAPP_NUMBER
        
        if self.sid and self.auth_token:
            self.client = Client(self.sid, self.auth_token)
        else:
            self.client = None
            logger.warning("Twilio credentials missing. Running in Mock Notification Mode.")

    def send_whatsapp(self, message_body: str):
        if self.client and self.to_whatsapp:
            try:
                msg = self.client.messages.create(
                    body=message_body,
                    from_=self.from_whatsapp,
                    to=self.to_whatsapp
                )
                logger.info(f"WhatsApp Notification Sent: {msg.sid}")
                return True
            except Exception as e:
                logger.error(f"Failed to send WhatsApp message: {str(e)}")
                return False
        else:
            logger.info(f"[MOCK NOTIFICATION SENT]:\n{message_body}")
            return True

notifier = NotificationService()