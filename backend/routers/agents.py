import asyncio
import logging
import uuid
import datetime
import time
from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from database.connection import get_db
from .auth import get_current_user
from repositories.meeting_repository import MeetingRepository
from repositories.entity_repository import EntityRepository
from config.settings import settings

# Import ADK components
from google.adk import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from orchestrator.workflow import actionsync_orchestrator
from tools.registry import tool_registry

logger = logging.getLogger("actionsync.routers.agents")

router = APIRouter(prefix="/agents", tags=["Agent Execution"])

# Initialize a global session service for ADK runner
session_service = InMemorySessionService()

def make_content(text: str) -> types.Content:
    """Helper to wrap string text into Google GenAI Content structure."""
    return types.Content(
        role="user",
        parts=[types.Part.from_text(text=text)]
    )

async def run_pipeline_task(db_session_factory, meeting_id: str):
    """Background task to run the ADK pipeline on a meeting transcript."""
    start_time = time.time()
    db = db_session_factory()
    try:
        meeting = MeetingRepository.get_meeting(db, meeting_id)
        if not meeting:
            logger.error(f"Meeting {meeting_id} not found in background task.")
            return

        logger.info(f"⏳ [BACKGROUND PROCESS] Started ActionSync AI pipeline for meeting '{meeting.title}' (ID: {meeting_id}) at {datetime.datetime.utcnow().isoformat()}")

        # 1. Check if raw transcription exists; if not, transcribe first
        if not meeting.transcript_raw:
            if not meeting.audio_path or not os.path.exists(meeting.audio_path):
                logger.error(f"No audio file or transcript for meeting {meeting_id}")
                MeetingRepository.update_meeting(db, meeting_id, MeetingUpdate(status="Failed"))
                return
            
            # Execute WhisperTool inside FastAPI threadpool to prevent blocking the event loop
            logger.info("🎙️ [BACKGROUND PROCESS] Starting Whisper speech transcription. Event loop continues to handle requests...")
            w_start = time.time()
            transcription_result = await run_in_threadpool(
                tool_registry.execute_tool, "WhisperTool", meeting.audio_path
            )
            w_elapsed = time.time() - w_start
            logger.info(f"🎙️ [BACKGROUND PROCESS] Speech transcription finished in {w_elapsed:.2f} seconds.")
            
            meeting.transcript_raw = transcription_result["text"]
            meeting.transcript_clean = transcription_result["text"]
            
            # Save segments to database
            for seg in transcription_result["segments"]:
                MeetingRepository.create_segment(
                    db,
                    meeting_id=meeting.id,
                    segment_in=SegmentCreate(
                        speaker=seg["speaker"],
                        text=seg["text"],
                        start_time=seg["start_time"],
                        end_time=seg["end_time"]
                    )
                )
            
            # Compute total duration from segments
            if transcription_result["segments"]:
                meeting.duration = transcription_result["segments"][-1]["end_time"]
            db.commit()

        # 2. Check for Gemini Key. If not set, run in mock mode
        if not settings.GEMINI_API_KEY:
            logger.warning("GEMINI_API_KEY not configured. Running pipeline in mock fallback mode.")
            await asyncio.sleep(3.0)  # Simulate processing latency
            pipeline_result = get_mock_pipeline_output()
        else:
            # Run using Google ADK Orchestrator
            logger.info("Instantiating ADK runner for orchestrator workflow...")
            runner = Runner(
                agent=actionsync_orchestrator,
                app_name="ActionSyncAI",
                session_service=session_service
            )
            
            session_id = f"session_{meeting_id}"
            user_id = "actionsync_operator"
            new_message = make_content(meeting.transcript_raw)
            
            # Create session in InMemorySessionService before running runner
            try:
                await session_service.create_session(
                    app_name="ActionSyncAI",
                    user_id=user_id,
                    session_id=session_id
                )
                logger.info(f"Successfully created ADK session: {session_id}")
            except Exception as e:
                logger.warning(f"Session already exists or could not be created: {e}")
            
            events = []
            logger.info(f"Running ADK workflow for session: {session_id}")
            
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=new_message
            ):
                events.append(event)
                
            # Extract final pipeline output from event stream
            pipeline_result = None
            for event in events:
                if event.output is not None:
                    pipeline_result = event.output
                    
            if not pipeline_result:
                raise RuntimeError("Orchestrator did not yield a valid output event.")

        # 3. Save outcomes using KnowledgeGraphBuilder tool
        logger.info("🧱 [BACKGROUND PROCESS] Executing KnowledgeGraphBuilder to save entities and relations...")
        kg_start = time.time()
        builder_tool = tool_registry.get_tool("KnowledgeGraphBuilder")
        await run_in_threadpool(builder_tool.execute, db, meeting_id, pipeline_result)
        logger.info(f"🧱 [BACKGROUND PROCESS] Knowledge graph built in {time.time() - kg_start:.2f} seconds.")

        # 4. Update Meeting metadata and status
        from schemas.schemas import MeetingUpdate
        MeetingRepository.update_meeting(
            db, 
            meeting_id, 
            MeetingUpdate(
                status="Completed",
                executive_summary=pipeline_result["summarizer"]["executive_summary"],
                community_impact=pipeline_result["community_impact"]["impact_summary"],
                clarification_notes="\n".join(pipeline_result["clarification"]["questions"]) if pipeline_result["clarification"]["is_clarification_needed"] else None
            )
        )
        
        total_elapsed = time.time() - start_time
        logger.info(f"✨ [BACKGROUND PROCESS] Pipeline for meeting '{meeting.title}' (ID: {meeting_id}) COMPLETED successfully! Total duration: {total_elapsed:.2f} seconds.")
        
    except Exception as e:
        logger.error(f"Failed background pipeline execution for meeting {meeting_id}: {e}")
        from schemas.schemas import MeetingUpdate
        MeetingRepository.update_meeting(db, meeting_id, MeetingUpdate(status="Failed"))
    finally:
        db.close()


@router.post("/process/{meeting_id}", status_code=status.HTTP_202_ACCEPTED)
def trigger_pipeline(
    meeting_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Any = Depends(get_current_user)
):
    """Triggers the agent pipeline to process transcript and build knowledge graph in the background."""
    meeting = MeetingRepository.get_meeting(db, meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    if meeting.status in ("Processing", "Completed") and meeting.executive_summary:
         return {"status": "skipped", "message": "Meeting is already processed or processing."}

    # Set status to Processing
    from schemas.schemas import MeetingUpdate
    MeetingRepository.update_meeting(db, meeting_id, MeetingUpdate(status="Processing"))
    
    # Run pipeline in background task
    from database.connection import db_session
    background_tasks.add_task(run_pipeline_task, db_session, meeting_id)
    
    return {"status": "processing", "message": "Multi-agent coordination pipeline triggered in background."}


def get_mock_pipeline_output() -> Dict[str, Any]:
    """Generates standard mock pipeline output when Gemini Key is not set."""
    return {
        "summarizer": {
            "executive_summary": (
                "The meeting covered planning for the upcoming quarter. Key deliverables included "
                "database schema design and frontend layout alignment. John was tasked with completing the API schema "
                "by next Tuesday, and Sarah will coordinate with him to sync the frontend pages. "
                "A hosting risk was noted regarding database credentials. A follow-up sync is scheduled for next Thursday."
            ),
            "key_topics": ["Roadmap planning", "Database design", "Frontend alignment", "Hosting risk"],
            "meeting_context": "Kickoff meeting for Q3 ActionSync AI development. Attendees: John, Sarah. Tone: collaborative."
        },
        "decision": {
            "decisions": [
                {
                    "title": "Adopt SQLite for Dev and PostgreSQL for Prod",
                    "description": "The team decided to use SQLite for speed of local development, and PostgreSQL in Docker for production deployments.",
                    "decider_name": "John",
                    "status": "Approved"
                }
            ]
        },
        "action_item": {
            "tasks": [
                {
                    "title": "Complete Database Schema",
                    "description": "Design and implement the SQLAlchemy models and repository layers for ActionSync AI.",
                    "assignee_name": "John",
                    "status": "Pending",
                    "deadline": "2026-07-06"
                },
                {
                    "title": "Align Streamlit Interface",
                    "description": "Create the pages for meeting history, uploads, dashboard, and knowledge graph visualization.",
                    "assignee_name": "Sarah",
                    "status": "Pending",
                    "deadline": "2026-07-09"
                }
            ]
        },
        "risk": {
            "risks": [
                {
                    "description": "Hosting credentials dependency",
                    "impact_level": "High",
                    "mitigation_strategy": "Request credentials from the operations team by Friday morning."
                }
            ]
        },
        "timeline": {
            "events": [
                {
                    "event_date": "2026-07-06",
                    "description": "Complete Database Schema",
                    "project_name": "Database Layer"
                },
                {
                    "event_date": "2026-07-09",
                    "description": "Align Streamlit Interface",
                    "project_name": "Frontend Pages"
                }
            ]
        },
        "validator": {
            "is_valid": True,
            "errors": [],
            "reasons": "All extracted entities have consistent assignees, projects, and deadlines."
        },
        "community_impact": {
            "impact_summary": "Workload is balanced. The task division matches the technical roles of John and Sarah.",
            "team_dynamics": "Collaborative alignment. Clarifying dependencies early avoids friction during integration.",
            "cultural_alignment": "Aligns with transparency and proactive planning values."
        },
        "accountability": {
            "accountability_summary": "Clear ownership established for all major deliverables.",
            "assignments_confirmed": ["John -> Complete Database Schema", "Sarah -> Align Streamlit Interface"],
            "follow_up_schedule": "Next sync on Thursday, July 9, 2026."
        },
        "clarification": {
            "is_clarification_needed": False,
            "questions": []
        }
    }

# Additional imports needed for background task
import os
from schemas.schemas import SegmentCreate
