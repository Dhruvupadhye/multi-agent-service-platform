from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from app.utils.calendar_helper import calendar_helper
from app.utils.logger import logger

# Define the exact JSON structure we need to send to Google Calendar
class EventDetails(BaseModel):
    summary: str = Field(description="Title or summary of the meeting/event")
    start_time_iso: str = Field(description="Start time in ISO 8601 format (e.g., 2024-05-20T16:00:00)")
    end_time_iso: str = Field(description="End time in ISO 8601 format (e.g., 2024-05-20T17:00:00)")
    description: str = Field(description="Additional details for the event, default to empty string if none")

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

    def schedule_event(self, user_request: str) -> dict:
        logger.info(f"Reminder Agent parsing request: {user_request}")
        
        # Grab the exact current time so the AI calculates days accurately
        current_dt = datetime.now().isoformat()
        
        try:
            # 1. Parse natural language into structured JSON
            event_data = self.chain.invoke({
                "request": user_request,
                "current_datetime": current_dt
            })
            logger.info(f"Parsed Event Data: {event_data}")
            
            # 2. Create the event using our CalendarHelper
            result = calendar_helper.create_event(
                summary=event_data["summary"],
                start_time_iso=event_data["start_time_iso"],
                end_time_iso=event_data["end_time_iso"],
                description=event_data.get("description", "")
            )
            
            if result:
                return {
                    "status": "success", 
                    "event_link": result.get("htmlLink"), 
                    "summary": event_data["summary"]
                }
            else:
                return {"status": "error", "message": "Failed to create event via Google API"}
                
        except Exception as e:
            logger.error(f"Error in Reminder Agent: {e}")
            return {"status": "error", "message": str(e)}

reminder_agent = ReminderAgent()