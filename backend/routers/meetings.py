import os
import shutil
import uuid
import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from database.connection import get_db
from repositories.meeting_repository import MeetingRepository
from schemas.schemas import MeetingResponse, MeetingCreate, SegmentResponse
from .auth import get_current_user
from config.settings import settings
from typing import List, Any

router = APIRouter(prefix="/meetings", tags=["Meetings"])

@router.post("/upload", response_model=MeetingResponse, status_code=status.HTTP_201_CREATED)
def upload_meeting(
    title: str = Form(...),
    file: UploadFile = File(...),
    target_language: str = Form("en"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Uploads an audio file and initializes a new meeting record in the DB."""
    # Ensure directories exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in (".mp3", ".wav", ".m4a", ".mp4", ".ogg"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported audio format. Supported: mp3, wav, m4a, mp4, ogg."
        )

    # Save the file securely with a unique UUID filename
    safe_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save upload file: {e}"
        )

    meeting_in = MeetingCreate(
        title=title,
        date=datetime.datetime.utcnow(),
        duration=0.0,  # Computed later after transcription
        target_language=target_language
    )
    
    meeting = MeetingRepository.create_meeting(db, meeting_in, audio_path=file_path)
    return meeting

@router.get("", response_model=List[MeetingResponse])
def list_meetings(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Lists all meeting records in reverse chronological order."""
    return MeetingRepository.get_meetings(db, skip=skip, limit=limit)

@router.get("/{meeting_id}", response_model=MeetingResponse)
def get_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Retrieves a single meeting record by ID."""
    meeting = MeetingRepository.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.get("/{meeting_id}/segments", response_model=List[SegmentResponse])
def get_meeting_segments(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Retrieves all transcribed segments for a meeting."""
    meeting = MeetingRepository.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return MeetingRepository.get_segments_for_meeting(db, meeting_id)

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Deletes a meeting and its associated audio file and database entities."""
    meeting = MeetingRepository.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Delete file from disk
    if meeting.audio_path and os.path.exists(meeting.audio_path):
        try:
            os.remove(meeting.audio_path)
        except Exception as e:
            # Non-blocking log, continue deleting DB entry
            pass

    deleted = MeetingRepository.delete_meeting(db, meeting_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="Failed to delete meeting record.")

@router.get("/wait/{meeting_id}", response_model=MeetingResponse)
async def wait_for_meeting(
    meeting_id: str,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Long-polling endpoint that blocks and waits until a meeting status is no longer 'Pending' or 'Processing'."""
    import asyncio
    for _ in range(300):  # Timeout after 10 minutes (300 * 2s)
        meeting = MeetingRepository.get_meeting(db, meeting_id)
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        if meeting.status not in ("Pending", "Processing"):
            return meeting
            
        await asyncio.sleep(2)
        db.refresh(meeting)
        
    return meeting
