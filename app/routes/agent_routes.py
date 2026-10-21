import os
import shutil
import tempfile
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Query
from pydantic import BaseModel
from app.agents.composer_agent import composer_agent
from app.agents.assistant_agent import assistant_agent
from app.agents.supervisor_agent import supervisor_agent
from app.utils.voice_helper import voice_helper
from app.utils.logger import logger

router = APIRouter(prefix="/agents", tags=["Multi-Agent Orchestration"])

class TextCommandRequest(BaseModel):
    command: str
    session_id: Optional[str] = "default"

@router.post("/voice-compose-email/")
async def voice_compose_email(file: UploadFile = File(...)):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = composer_agent.compose_from_voice(temp_path)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.get("/ask-assistant/")
async def ask_assistant(query: str = Query(..., description="Ask a question about your uploaded documents or general topics")):
    return assistant_agent.answer_query(query)

@router.post("/orchestrate-voice/")
async def orchestrate_voice(
    file: UploadFile = File(...),
    session_id: Optional[str] = Query("default")
):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # 1. Save audio to disk
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Transcribe voice input
        transcript = voice_helper.transcribe_audio(temp_path)
        clean_transcript = transcript.strip() if transcript else ""
        
        # 3. Guard against empty audio transcriptions
        if not clean_transcript:
            logger.warning("Empty or unintelligible voice transcription received.")
            return {
                "intent": "INVALID_OR_EMPTY",
                "response_type": "clarification",
                "direct_answer": "No speech detected. Please speak clearly into the microphone and record your command again.",
                "action_result": "No speech detected. Please record your command again.",
                "final_email": None,
                "event_link": None,
                "data": None,
                "raw_transcript": "",
                "confidence": 0.0,
                "requires_clarification": True,
                "clarification_question": "No speech detected. Please speak clearly into the microphone and record your command again."
            }
        
        # 4. Hand off to the LangGraph Supervisor
        result = supervisor_agent.orchestrate(clean_transcript, session_id=session_id)
        result["raw_transcript"] = clean_transcript
        
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/orchestrate-text/")
async def orchestrate_text(request: TextCommandRequest):
    """Direct text orchestration endpoint for testing and text-based interactions."""
    clean_command = request.command.strip() if request.command else ""
    if not clean_command:
        return {
            "intent": "INVALID_OR_EMPTY",
            "response_type": "clarification",
            "direct_answer": "No command provided. Please enter a request.",
            "action_result": "No command provided.",
            "final_email": None,
            "event_link": None,
            "data": None,
            "raw_transcript": "",
            "confidence": 0.0,
            "requires_clarification": True,
            "clarification_question": "No command provided. Please enter a request."
        }
    
    result = supervisor_agent.orchestrate(clean_command, session_id=request.session_id)
    result["raw_transcript"] = clean_command
    return result