import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(default="", env="GEMINI_API_KEY")
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    SECRET_KEY: str = Field(default="actionsync_secret_key_default_1234567890", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    DATABASE_URL: str = Field(default="sqlite:///./storage/actionsync.db", env="DATABASE_URL")
    
    GEMINI_MODEL: str = Field(default="gemini-2.5-flash", env="GEMINI_MODEL")
    WHISPER_MODEL_NAME: str = Field(default="base", env="WHISPER_MODEL_NAME")
    
    STORAGE_DIR: str = Field(default="./storage", env="STORAGE_DIR")
    UPLOAD_DIR: str = Field(default="./storage/uploads", env="UPLOAD_DIR")
    GENERATED_DOCS_DIR: str = Field(default="./storage/docs", env="GENERATED_DOCS_DIR")
    KNOWLEDGE_GRAPH_PATH: str = Field(default="./storage/knowledge_graph.json", env="KNOWLEDGE_GRAPH_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()

# Export loaded settings to environment variables for external libraries (like Google GenAI/ADK SDKs)
if settings.GEMINI_API_KEY:
    os.environ["GEMINI_API_KEY"] = settings.GEMINI_API_KEY
if settings.GEMINI_MODEL:
    os.environ["GEMINI_MODEL"] = settings.GEMINI_MODEL

# Ensure directories exist on import
for path in [settings.STORAGE_DIR, settings.UPLOAD_DIR, settings.GENERATED_DOCS_DIR]:
    os.makedirs(path, exist_ok=True)
