import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Agent Office Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CHROMA_PERSIST_DIR: str = "./data/chroma"
    OPENAI_API_KEY: str
    
    # Twilio Settings (Using Optional so it doesn't crash if missing)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    USER_WHATSAPP_NUMBER: Optional[str] = None

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()