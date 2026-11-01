from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.utils.calendar_helper import calendar_helper
from app.agents.reminder_agent import reminder_agent
from app.utils.notifier import notifier
from app.utils.logger import logger

calendar_router = APIRouter(prefix="/calendar", tags=["Calendar Events"])
reminders_router = APIRouter(prefix="/reminders", tags=["Reminders"])

class CreateEventRequest(BaseModel):
    summary: str = Field(..., description="Title or summary of the meeting/event")
    start_time_iso: str = Field(..., description="Start time in ISO format (e.g. 2026-11-02T10:00:00)")
    end_time_iso: str = Field(..., description="End time in ISO format (e.g. 2026-11-02T11:00:00)")
    description: Optional[str] = Field(default="", description="Optional event description or agenda")

class CreateReminderRequest(BaseModel):
    title: str = Field(..., description="Reminder title or task")
    datetime_iso: str = Field(..., description="Due date and time in ISO format")
    notes: Optional[str] = Field(default="", description="Optional notes or details")
    send_whatsapp: bool = Field(default=True, description="Whether to send a WhatsApp notification alert")

# ----------------- Calendar Endpoints -----------------

@calendar_router.get("/events")
async def list_calendar_events(
    time_min: Optional[str] = Query(default=None, description="ISO datetime string for minimum start time"),
    time_max: Optional[str] = Query(default=None, description="ISO datetime string for maximum start time"),
    max_results: int = Query(default=20, ge=1, le=100)
):
    """Retrieve upcoming calendar events."""
    try:
        events = calendar_helper.list_events(
            time_min_iso=time_min,
            time_max_iso=time_max,
            max_results=max_results
        )
        return {
            "status": "success",
            "count": len(events),
            "events": events
        }
    except Exception as e:
        logger.error(f"Error fetching calendar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@calendar_router.post("/events")
async def create_calendar_event(request: CreateEventRequest):
    """Create a new event in Google Calendar."""
    if not request.summary.strip():
        raise HTTPException(status_code=400, detail="Event summary cannot be empty.")
        
    try:
        # Validate ISO dates
        start_dt = datetime.fromisoformat(request.start_time_iso.replace("Z", "+00:00"))
        end_dt = datetime.fromisoformat(request.end_time_iso.replace("Z", "+00:00"))
        if end_dt <= start_dt:
            raise HTTPException(status_code=400, detail="End time must be after start time.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid ISO datetime format: {ve}")

    try:
        result = calendar_helper.create_event(
            summary=request.summary.strip(),
            start_time_iso=request.start_time_iso,
            end_time_iso=request.end_time_iso,
            description=request.description or ""
        )
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create calendar event via Google API.")
            
        return {
            "status": "success",
            "event": result,
            "event_link": result.get("htmlLink", "https://calendar.google.com/"),
            "summary": request.summary,
            "start_time": request.start_time_iso
        }
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ----------------- Reminders Endpoints -----------------

@reminders_router.get("/list")
async def list_reminders():
    """Retrieve reminders from the calendar schedule."""
    try:
        events = calendar_helper.list_events(max_results=50)
        reminders = []
        for ev in events:
            summary = ev.get("summary", "")
            # Filter reminders by summary tag
            if summary.lower().startswith("reminder:") or "[reminder]" in summary.lower():
                clean_title = summary.split(":", 1)[-1].strip() if ":" in summary else summary
                start_info = ev.get("start", {})
                due_time = start_info.get("dateTime", start_info.get("date", ""))
                reminders.append({
                    "id": ev.get("id"),
                    "title": clean_title,
                    "raw_summary": summary,
                    "scheduled_time": due_time,
                    "description": ev.get("description", ""),
                    "event_link": ev.get("htmlLink")
                })
                
        return {
            "status": "success",
            "count": len(reminders),
            "reminders": reminders
        }
    except Exception as e:
        logger.error(f"Error listing reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@reminders_router.post("/create")
async def create_reminder(request: CreateReminderRequest):
    """Create a structured reminder, add to Google Calendar, and dispatch WhatsApp alert."""
    if not request.title.strip():
        raise HTTPException(status_code=400, detail="Reminder title cannot be empty.")
        
    try:
        start_dt = datetime.fromisoformat(request.datetime_iso.replace("Z", "+00:00"))
        # Default reminder duration is 30 mins
        end_dt = start_dt + timedelta(minutes=30)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid ISO datetime format: {ve}")

    summary = f"Reminder: {request.title.strip()}"
    end_iso = end_dt.isoformat()
    description = request.notes.strip() if request.notes else f"Reminder: {request.title.strip()}"

    try:
        result = calendar_helper.create_event(
            summary=summary,
            start_time_iso=request.datetime_iso,
            end_time_iso=end_iso,
            description=description
        )
        
        # WhatsApp notification
        if request.send_whatsapp:
            whatsapp_msg = f"⏰ *New Reminder Set*\n{summary}\nScheduled for: {request.datetime_iso}"
            try:
                notifier.send_whatsapp(whatsapp_msg)
            except Exception as ne:
                logger.warning(f"Could not dispatch WhatsApp alert for reminder: {ne}")

        return {
            "status": "success",
            "reminder": {
                "id": result.get("id") if result else "mock_id",
                "title": request.title.strip(),
                "scheduled_time": request.datetime_iso,
                "description": description,
                "event_link": result.get("htmlLink") if result else None
            }
        }
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))
