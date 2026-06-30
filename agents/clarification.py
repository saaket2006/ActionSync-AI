from google.adk import Agent
from schemas.schemas import ClarificationOutput
from config.settings import settings

clarification_agent = Agent(
    name="clarification_agent",
    description="Identifies gaps, logical ambiguities, or missing ownership/deadlines, and compiles follow-up questions.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are a critical inquiry specialist. Review the transcript alongside all extracted summaries, "
        "decisions, and tasks. Find any missing details, conflicting statements, or vague assignments. "
        "Provide: is_clarification_needed (True if there are critical missing elements, False otherwise), "
        "and a list of clarifying questions to resolve those gaps."
    ),
    output_schema=ClarificationOutput
)
