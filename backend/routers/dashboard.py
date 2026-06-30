from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database.connection import get_db
from database.models import Meeting, Project, Task, Decision, Risk
from .auth import get_current_user
from typing import Dict, Any, List

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/metrics")
def get_dashboard_metrics(db: Session = Depends(get_db), current_user: Any = Depends(get_current_user)):
    """Computes aggregated organizational metrics for the dashboard analytics."""
    total_meetings = db.query(func.count(Meeting.id)).scalar() or 0
    active_projects = db.query(func.count(Project.id)).filter(Project.status == "Active").scalar() or 0
    
    total_tasks = db.query(func.count(Task.id)).scalar() or 0
    completed_tasks = db.query(func.count(Task.id)).filter(Task.status == "Completed").scalar() or 0
    pending_tasks = total_tasks - completed_tasks
    
    active_risks = db.query(func.count(Risk.id)).filter(Risk.status == "Active").scalar() or 0
    total_decisions = db.query(func.count(Decision.id)).scalar() or 0
    
    # Task completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    # Risk distribution
    high_risks = db.query(func.count(Risk.id)).filter(Risk.status == "Active", Risk.impact_level.in_(["High", "Critical"])).scalar() or 0
    med_risks = db.query(func.count(Risk.id)).filter(Risk.status == "Active", Risk.impact_level == "Medium").scalar() or 0
    low_risks = db.query(func.count(Risk.id)).filter(Risk.status == "Active", Risk.impact_level == "Low").scalar() or 0

    # Recent meetings
    recent_meetings = db.query(Meeting).order_by(Meeting.date.desc()).limit(5).all()
    recent_meetings_list = [
        {
            "id": m.id,
            "title": m.title,
            "date": m.date.isoformat(),
            "status": m.status
        } for m in recent_meetings
    ]

    return {
        "summary": {
            "total_meetings": total_meetings,
            "active_projects": active_projects,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "active_risks": active_risks,
            "total_decisions": total_decisions,
            "task_completion_rate": round(completion_rate, 1)
        },
        "risk_distribution": {
            "high": high_risks,
            "medium": med_risks,
            "low": low_risks
        },
        "recent_meetings": recent_meetings_list
    }
