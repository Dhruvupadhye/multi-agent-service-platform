import os
from twilio.rest import Client
from app.utils.logger import logger

class NotificationService:
    def __init__(self):
        self.sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.from_whatsapp = os.getenv("TWILIO_WHATSAPP_NUMBER")
        self.to_whatsapp = os.getenv("USER_WHATSAPP_NUMBER")
        
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