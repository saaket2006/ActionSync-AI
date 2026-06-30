from google.adk import Agent
from schemas.schemas import TimelineOutput
from config.settings import settings

timeline_agent = Agent(
    name="timeline_agent",
    description="Reconstructs project timelines, deadlines, and milestones from meeting transcripts.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are a master scheduler. Review the meeting transcript and build a timeline of milestones. "
        "For each milestone/event, capture the event_date (standardized to YYYY-MM-DD if possible), "
        "a description of the milestone, and the name of the associated project (project_name)."
    ),
    output_schema=TimelineOutput
)
