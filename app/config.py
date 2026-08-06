import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Multi-Agent Office Platform"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()