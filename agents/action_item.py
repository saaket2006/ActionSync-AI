from google.adk import Agent
from schemas.schemas import ActionItemOutput
from config.settings import settings

action_item_agent = Agent(
    name="action_item_agent",
    description="Identifies and extracts action items, deliverables, and assignments from meeting transcripts.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are an agile project manager. Analyze the transcript to extract all action items. "
        "For each item, identify a concise title, detailed description, the name of the owner (assignee_name), "
        "the status (Pending or In Progress), and the deadline (format as YYYY-MM-DD if a specific date or weekday "
        "was mentioned relative to the meeting, otherwise omit)."
    ),
    output_schema=ActionItemOutput
)
