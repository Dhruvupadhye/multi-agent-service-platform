import os
import shutil
import tempfile
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.agents.document_agent import document_agent
from app.utils.voice_helper import voice_helper
from app.utils.vector_db import vector_db
from app.utils.logger import logger

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

@router.get("/documents")
async def list_documents():
    """Retrieve indexed documents from the ChromaDB vector database."""
    try:
        collection = vector_db.get_or_create_collection("document_chunks")
        data = collection.get(include=["metadatas", "documents"])
        metadatas = data.get("metadatas", []) or []
        docs = data.get("documents", []) or []
        
        # Group by source/filename
        grouped: Dict[str, Dict[str, Any]] = {}
        for idx, meta in enumerate(metadatas):
            if not meta:
                continue
            source = meta.get("source", "Unknown Document")
            page = meta.get("page", 0)
            
            if source not in grouped:
                snippet = docs[idx][:250] if idx < len(docs) else ""
                grouped[source] = {
                    "filename": source,
                    "total_chunks": 1,
                    "max_page": page,
                    "preview": snippet
                }
            else:
                grouped[source]["total_chunks"] += 1
                if page > grouped[source]["max_page"]:
                    grouped[source]["max_page"] = page
                    
        doc_list = [
            {
                "filename": item["filename"],
                "total_chunks": item["total_chunks"],
                "pages": item["max_page"] + 1,
                "preview": item["preview"]
            }
            for item in grouped.values()
        ]
        
        return {
            "status": "success",
            "count": len(doc_list),
            "documents": doc_list
        }
    except Exception as e:
        logger.error(f"Error listing indexed documents: {e}")
        return {
            "status": "success",
            "count": 0,
            "documents": []
        }

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
