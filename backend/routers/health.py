from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import os
from database.connection import get_db
from config.settings import settings

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def health_check(db: Session = Depends(get_db)):
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {e}"
        
    return {
        "status": "healthy",
        "database": db_status,
        "gemini_api": "configured" if settings.GEMINI_API_KEY else "missing",
        "storage_writable": os.access(settings.STORAGE_DIR, os.W_OK)
    }
