from datetime import datetime, timedelta
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.utils.calendar_helper import calendar_helper
from app.utils.notifier import notifier
from app.utils.logger import logger

# Define the exact JSON structure we need to send to Google Calendar
class EventDetails(BaseModel):
    summary: str = Field(description="Title or summary of the meeting/event")
    start_time_iso: str = Field(description="Start time in ISO 8601 format (e.g., 2024-05-20T16:00:00)")
    end_time_iso: str = Field(description="End time in ISO 8601 format (e.g., 2024-05-20T17:00:00)")
    description: str = Field(default="", description="Additional details for the event, default to empty string if none")

class ReminderAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model="gpt-4o-mini")
        self.parser = JsonOutputParser(pydantic_object=EventDetails)
        
        self.prompt = PromptTemplate(
            template="""You are a calendar assistant. Extract the event details from the user's natural language request.
            Assume meetings are 1 hour long unless specified otherwise.
            
            CRITICAL: The current date and time is {current_datetime}. 
            Use this to calculate relative terms like "tomorrow", "next Monday", or "this afternoon".
            
            User Request: {request}
            
            Format Instructions:
            {format_instructions}
            """,
            input_variables=["request", "current_datetime"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        self.chain = self.prompt | self.llm | self.parser

    def _fallback_parse_event(self, user_request: str) -> dict:
        """Heuristic event parser when LLM is unavailable or in offline testing."""
        now = datetime.now()
        target_date = now
        if "tomorrow" in user_request.lower():
            target_date = now + timedelta(days=1)
        elif "friday" in user_request.lower():
            days_ahead = (4 - now.weekday()) % 7
            target_date = now + timedelta(days=days_ahead if days_ahead > 0 else 7)
            
        # Check for time (e.g., 3 PM, 10 AM, 15:00)
        hour = 10
        time_match = re.search(r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', user_request.lower())
        if time_match:
            h = int(time_match.group(1))
            ampm = time_match.group(3)
            if ampm == "pm" and h < 12:
                h += 12
            elif ampm == "am" and h == 12:
                h = 0
            hour = h

        start_dt = target_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        end_dt = start_dt + timedelta(hours=1)
        
        clean_summary = re.sub(r'^(schedule|create|set|remind me to|a meeting|an event|calendar event for|at|tomorrow|\d+\s*(am|pm)?)+', '', user_request, flags=re.IGNORECASE).strip()
        if not clean_summary:
            clean_summary = "Scheduled Meeting"
            
        return {
            "summary": clean_summary.capitalize(),
            "start_time_iso": start_dt.isoformat(),
            "end_time_iso": end_dt.isoformat(),
            "description": user_request
        }

    def schedule_event(self, user_request: str) -> dict:
        logger.info(f"Reminder Agent parsing scheduling request: {user_request}")
        current_dt = datetime.now().isoformat()
        
        try:
            event_data = self.chain.invoke({
                "request": user_request,
                "current_datetime": current_dt
            })
        except Exception as e:
            logger.warning(f"LLM parsing failed ({e}). Using heuristic parsing.")
            event_data = self._fallback_parse_event(user_request)
            
        logger.info(f"Parsed Event Data: {event_data}")
        
        result = calendar_helper.create_event(
            summary=event_data["summary"],
            start_time_iso=event_data["start_time_iso"],
            end_time_iso=event_data["end_time_iso"],
            description=event_data.get("description", "")
        )
        
        if result:
            return {
                "status": "success", 
                "event_link": result.get("htmlLink", "https://calendar.google.com/"), 
                "summary": event_data["summary"],
                "start_time": event_data["start_time_iso"]
            }
        else:
            return {"status": "error", "message": "Failed to create event via Google Calendar API"}

    def list_events(self, user_request: str) -> dict:
        """Retrieve and format existing meetings or calendar events."""
        logger.info(f"Reminder Agent retrieving calendar events for request: {user_request}")
        events = calendar_helper.list_events()
        
        if not events:
            return {
                "status": "success",
                "summary": "You have no upcoming meetings scheduled.",
                "events": []
            }
            
        formatted_items = []
        for ev in events:
            summary = ev.get("summary", "Untitled Meeting")
            start = ev.get("start", {}).get("dateTime", ev.get("start", {}).get("date", "Unknown time"))
            desc = ev.get("description", "")
            desc_str = f" - {desc}" if desc else ""
            formatted_items.append(f"• {summary} at {start}{desc_str}")
            
        summary_text = "Here are your scheduled meetings:\n" + "\n".join(formatted_items)
        return {
            "status": "success",
            "summary": summary_text,
            "events": events
        }

    def set_reminder(self, user_request: str) -> dict:
        """Create a reminder notification and schedule."""
        logger.info(f"Reminder Agent setting reminder: {user_request}")
        current_dt = datetime.now().isoformat()
        
        try:
            event_data = self.chain.invoke({
                "request": user_request,
                "current_datetime": current_dt
            })
        except Exception as e:
            logger.warning(f"LLM reminder parsing failed ({e}). Using heuristic parsing.")
            event_data = self._fallback_parse_event(user_request)
            
        summary = event_data.get("summary", "Reminder")
        if not summary.lower().startswith("reminder:"):
            summary = f"Reminder: {summary}"
            
        result = calendar_helper.create_event(
            summary=summary,
            start_time_iso=event_data["start_time_iso"],
            end_time_iso=event_data["end_time_iso"],
            description=f"Automated reminder for: {user_request}"
        )
        
        # Trigger WhatsApp notification for the reminder
        whatsapp_msg = f"⏰ *New Reminder Set*\n{summary}\nScheduled for: {event_data['start_time_iso']}"
        notifier.send_whatsapp(whatsapp_msg)
        
        event_link = result.get("htmlLink", "https://calendar.google.com/") if result else None
        
        return {
            "status": "success",
            "summary": f"Reminder successfully created for: '{summary}'.",
            "event_link": event_link,
            "scheduled_time": event_data["start_time_iso"]
        }

reminder_agent = ReminderAgent()