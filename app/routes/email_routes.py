from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.utils.gmail_helper import gmail_helper
from app.agents.email_agent import email_agent
from app.agents.composer_agent import composer_agent
from app.utils.logger import logger

router = APIRouter(prefix="/emails", tags=["Email Agent"])

class DirectEmailInput(BaseModel):
    subject: str
    body: str

class ComposeEmailRequest(BaseModel):
    prompt: str = Field(..., description="Instructions or prompt for drafting an email")
    recipient_hint: Optional[str] = Field(default=None, description="Optional recipient name or hint")

class SendEmailRequest(BaseModel):
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Subject of the email")
    body: str = Field(..., description="Content of the email")

@router.get("/list")
async def list_emails(
    q: Optional[str] = Query(default="", description="Search query string or empty for recent emails"),
    max_results: int = Query(default=10, ge=1, le=50)
):
    """Retrieve emails from Gmail with metadata (sender, subject, date, body snippet)."""
    try:
        emails = gmail_helper.search_emails(query=q, max_results=max_results)
        return {
            "status": "success",
            "count": len(emails),
            "data": emails
        }
    except Exception as e:
        logger.error(f"Error listing emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compose")
async def compose_email(request: ComposeEmailRequest):
    """Generate a structured, professional email draft from natural language instructions."""
    try:
        draft = composer_agent.compose_draft(request.prompt)
        if request.recipient_hint and not draft.get("recipient_hint"):
            draft["recipient_hint"] = request.recipient_hint
        return {
            "status": "success",
            "draft": draft
        }
    except Exception as e:
        logger.error(f"Error generating email draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/send")
async def send_email(request: SendEmailRequest):
    """Dispatch an email via Gmail API."""
    if not request.to.strip() or "@" not in request.to:
        raise HTTPException(status_code=400, detail="A valid recipient email address is required.")
    if not request.subject.strip():
        raise HTTPException(status_code=400, detail="Email subject cannot be empty.")
    if not request.body.strip():
        raise HTTPException(status_code=400, detail="Email body cannot be empty.")

    try:
        result = gmail_helper.send_email(
            to=request.to.strip(),
            subject=request.subject.strip(),
            body=request.body.strip()
        )
        return result
    except Exception as e:
        logger.error(f"Error dispatching email: {e}")
        raise HTTPException(status_code=500, detail=str(e))

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
