import os
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from tools.doc_generator import DocumentGenerator
from .auth import get_current_user
from repositories.meeting_repository import MeetingRepository
from repositories.entity_repository import EntityRepository
from typing import Optional, Any

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/download")
def download_report(
    meeting_id: str,
    format: str = Query("pdf", description="Format: pdf or markdown"),
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Generates and downloads meeting intelligence reports on demand."""
    meeting = MeetingRepository.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    # Reconstruct the pipeline data structure from DB entities to generate the report
    decisions = EntityRepository.get_decisions_for_meeting(db, meeting_id)
    tasks = EntityRepository.get_tasks_for_meeting(db, meeting_id)
    risks = EntityRepository.get_risks_for_meeting(db, meeting_id)
    timeline = EntityRepository.get_timeline_for_meeting(db, meeting_id)

    pipeline_output = {
        "summarizer": {
            "executive_summary": meeting.executive_summary or "",
            "key_topics": [],
            "meeting_context": ""
        },
        "decision": {
            "decisions": [
                {
                    "title": d.title,
                    "description": d.description or "",
                    "decider_name": d.decider.name if d.decider else "Unknown",
                    "status": d.status
                } for d in decisions
            ]
        },
        "action_item": {
            "tasks": [
                {
                    "title": t.title,
                    "description": t.description or "",
                    "assignee_name": t.assignee.name if t.assignee else "Unknown",
                    "status": t.status,
                    "deadline": t.deadline.strftime("%Y-%m-%d") if t.deadline else None
                } for t in tasks
            ]
        },
        "risk": {
            "risks": [
                {
                    "description": r.description,
                    "impact_level": r.impact_level,
                    "mitigation_strategy": r.mitigation_strategy or ""
                } for r in risks
            ]
        },
        "timeline": {
            "events": [
                {
                    "event_date": e.event_date.strftime("%Y-%m-%d"),
                    "description": e.description,
                    "project_name": e.project.name if e.project else "General"
                } for e in timeline
            ]
        },
        "community_impact": {
            "impact_summary": meeting.community_impact or "",
            "team_dynamics": "",
            "cultural_alignment": ""
        },
        "accountability": {
            "accountability_summary": "",
            "assignments_confirmed": [],
            "follow_up_schedule": ""
        },
        "clarification": {
            "is_clarification_needed": meeting.clarification_notes is not None,
            "questions": [meeting.clarification_notes] if meeting.clarification_notes else []
        }
    }

    # Generate documents
    doc_gen = DocumentGenerator()
    doc_gen.initialize()
    files = doc_gen.execute(meeting.title, pipeline_output)

    if format.lower() == "pdf":
        file_path = files["pdf_path"]
        media_type = "application/pdf"
    elif format.lower() == "markdown":
        file_path = files["markdown_path"]
        media_type = "text/markdown"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported formats: pdf, markdown.")

    if not os.path.exists(file_path):
        raise HTTPException(status_code=500, detail="Failed to locate generated file on disk.")

    return FileResponse(
        file_path,
        media_type=media_type,
        filename=os.path.basename(file_path)
    )
