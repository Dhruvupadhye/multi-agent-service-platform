import os
import chromadb
from chromadb.config import Settings as ChromaSettings
from app.config import settings
from app.utils.logger import logger

class VectorDBClient:
    def __init__(self):
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
        logger.info(f"ChromaDB initialized at: {settings.CHROMA_PERSIST_DIR}")

    def get_or_create_collection(self, name: str):
        return self.client.get_or_create_collection(name=name)

# Singleton instance : creates a single instance of VectorDBClient to be used throughout the application
vector_db = VectorDBClient()