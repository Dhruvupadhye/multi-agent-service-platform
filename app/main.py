from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.utils.logger import logger
from app.utils.vector_db import vector_db
from app.routes.email_routes import router as email_router
from app.routes.media_routes import router as media_router
from app.routes.agent_routes import router as agent_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup tasks
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}...")
    
    # Initialize default ChromaDB collections
    vector_db.get_or_create_collection("email_summaries")
    vector_db.get_or_create_collection("document_chunks")
    logger.info("Default ChromaDB collections verified.")
    
    yield
    
    # Shutdown tasks
    logger.info("Shutting down core service...")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

app.include_router(email_router, prefix="/api/v1")
app.include_router(media_router, prefix="/api/v1")
app.include_router(agent_router, prefix="/api/v1")