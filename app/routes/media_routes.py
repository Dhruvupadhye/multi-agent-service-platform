import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.agents.document_agent import document_agent
from app.utils.voice_helper import voice_helper

router = APIRouter(prefix="/media", tags=["Document & Voice Agents"])

@router.post("/upload-document/")
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = document_agent.process_and_summarize(temp_path, file.filename)
        return result
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@router.post("/transcribe-voice/")
async def transcribe_voice(file: UploadFile = File(...)):
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, file.filename)
    
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        transcript = voice_helper.transcribe_audio(temp_path)
        return {"filename": file.filename, "transcript": transcript}
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)