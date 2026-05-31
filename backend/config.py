from pydantic_settings import BaseSettings
from pathlib import Path
import os

# Try to find .env file, but allow environment variables to override
ENV_PATH = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    azure_openai_endpoint:    str
    azure_openai_api_key:     str
    azure_openai_api_version: str = "2025-04-01-preview"
    azure_openai_chat_model:  str = "o4-mini"
    azure_openai_embed_model: str = "text-embedding-3-small"

    qdrant_host:     str = "localhost"
    qdrant_port:     int = 6333
    collection_name: str = "quiz_docs"

    class Config:
        # Only use .env file if it exists, otherwise use environment variables
        env_file = str(ENV_PATH) if ENV_PATH.exists() else None
        extra    = "ignore"


settings = Settings()
