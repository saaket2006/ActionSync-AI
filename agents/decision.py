from google.adk import Agent
from schemas.schemas import DecisionOutput
from config.settings import settings

decision_agent = Agent(
    name="decision_agent",
    description="Identifies and extracts formal decisions, agreements, and consensus from meeting transcripts.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are an organizational archivist. Review the meeting transcript and extract all decisions "
        "made. For each decision, capture the title, a detailed description, the name of the main decision maker "
        "(the decider_name), and the status of the decision (Approved or Proposed)."
    ),
    output_schema=DecisionOutput
)
