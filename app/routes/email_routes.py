from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.utils.gmail_helper import gmail_helper
from app.agents.email_agent import email_agent

router = APIRouter(prefix="/emails", tags=["Email Agent"])

class DirectEmailInput(BaseModel):
    subject: str
    body: str


@router.post("/fetch-and-process")
async def fetch_and_process():
    emails = gmail_helper.fetch_unread_emails()
    processed_summaries = email_agent.process_emails(emails)
    return {
        "status": "success",
        "processed_count": len(processed_summaries),
        "data": processed_summaries
    }

@router.post("/classify-single")
async def classify_single(email: DirectEmailInput):
    category = email_agent.classify(f"{email.subject} {email.body}")
    if category == "spam":
        return {"category": category, "action": "discarded"}
    
    summary = email_agent.summarize(email.body)
    return {"category": category, "summary": summary}