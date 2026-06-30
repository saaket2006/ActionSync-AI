from fastapi import APIRouter, Depends
from .auth import get_current_user
from config.settings import settings
from typing import Any

router = APIRouter(prefix="/settings", tags=["Settings"])

@router.get("")
def get_system_settings(current_user: Any = Depends(get_current_user)):
    """Retrieves current system settings (hiding sensitive credentials)."""
    return {
        "GEMINI_MODEL": settings.GEMINI_MODEL,
        "WHISPER_MODEL_NAME": settings.WHISPER_MODEL_NAME,
        "STORAGE_DIR": settings.STORAGE_DIR,
        "DATABASE_URL": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL
    }
