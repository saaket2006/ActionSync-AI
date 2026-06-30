from sqlalchemy.orm import Session
from sqlalchemy import or_
from database.models import Meeting, Segment, MemoryItem
from schemas.schemas import MeetingCreate, MeetingUpdate, SegmentCreate
from typing import List, Optional, Dict, Any
import datetime

class MeetingRepository:
    @staticmethod
    def create_meeting(db: Session, meeting_in: MeetingCreate, audio_path: Optional[str] = None) -> Meeting:
        db_meeting = Meeting(
            title=meeting_in.title,
            date=meeting_in.date,
            duration=meeting_in.duration,
            audio_path=audio_path,
            status="Pending"
        )
        db.add(db_meeting)
        db.commit()
        db.refresh(db_meeting)
        return db_meeting

    @staticmethod
    def get_meeting(db: Session, meeting_id: str) -> Optional[Meeting]:
        return db.query(Meeting).filter(Meeting.id == meeting_id).first()

    @staticmethod
    def get_meetings(db: Session, skip: int = 0, limit: int = 100) -> List[Meeting]:
        return db.query(Meeting).order_by(Meeting.date.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def update_meeting(db: Session, meeting_id: str, update_in: MeetingUpdate) -> Optional[Meeting]:
        db_meeting = MeetingRepository.get_meeting(db, meeting_id)
        if not db_meeting:
            return None
        
        update_data = update_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_meeting, key, value)
            
        db_meeting.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(db_meeting)
        return db_meeting

    @staticmethod
    def delete_meeting(db: Session, meeting_id: str) -> bool:
        db_meeting = MeetingRepository.get_meeting(db, meeting_id)
        if not db_meeting:
            return False
        db.delete(db_meeting)
        db.commit()
        return True

    @staticmethod
    def create_segment(db: Session, meeting_id: str, segment_in: SegmentCreate) -> Segment:
        db_segment = Segment(
            meeting_id=meeting_id,
            speaker=segment_in.speaker,
            text=segment_in.text,
            start_time=segment_in.start_time,
            end_time=segment_in.end_time
        )
        db.add(db_segment)
        db.commit()
        db.refresh(db_segment)
        return db_segment

    @staticmethod
    def get_segments_for_meeting(db: Session, meeting_id: str) -> List[Segment]:
        return db.query(Segment).filter(Segment.meeting_id == meeting_id).order_by(Segment.start_time.asc()).all()

    @staticmethod
    def save_memory_item(db: Session, scope: str, key: str, value: str) -> MemoryItem:
        db_item = db.query(MemoryItem).filter(MemoryItem.scope == scope, MemoryItem.key == key).first()
        if db_item:
            db_item.value = value
            db_item.updated_at = datetime.datetime.utcnow()
        else:
            db_item = MemoryItem(scope=scope, key=key, value=value)
            db.add(db_item)
        db.commit()
        db.refresh(db_item)
        return db_item

    @staticmethod
    def get_memory_item(db: Session, scope: str, key: str) -> Optional[MemoryItem]:
        return db.query(MemoryItem).filter(MemoryItem.scope == scope, MemoryItem.key == key).first()

    @staticmethod
    def delete_memory_item(db: Session, scope: str, key: str) -> bool:
        db_item = db.query(MemoryItem).filter(MemoryItem.scope == scope, MemoryItem.key == key).first()
        if not db_item:
            return False
        db.delete(db_item)
        db.commit()
        return True

    @staticmethod
    def search_memory_items(db: Session, query: str, scope: Optional[str] = None) -> List[MemoryItem]:
        q = db.query(MemoryItem)
        if scope:
            q = q.filter(MemoryItem.scope == scope)
        return q.filter(
            or_(
                MemoryItem.key.ilike(f"%{query}%"),
                MemoryItem.value.ilike(f"%{query}%")
            )
        ).all()
