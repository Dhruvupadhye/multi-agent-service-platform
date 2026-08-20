import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, Query
from app.agents.composer_agent import composer_agent
from app.agents.assistant_agent import assistant_agent
from app.agents.supervisor_agent import supervisor_agent
from app.utils.voice_helper import voice_helper

router = APIRouter(prefix="/agents", tags=["Multi-Agent Orchestration"])

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
async def orchestrate_voice(file: UploadFile = File(...)):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        # 1. Save audio
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Transcribe
        transcript = voice_helper.transcribe_audio(temp_path)
        
        # 3. Hand off to the LangGraph Supervisor
        final_email = supervisor_agent.orchestrate(transcript)
        final_email["raw_transcript"] = transcript
        
        return final_email
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)