from google.adk import Agent
from schemas.schemas import RiskOutput
from config.settings import settings

risk_agent = Agent(
    name="risk_agent",
    description="Identifies risks, bottlenecks, dependencies, and mitigation plans from meeting transcripts.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are a risk officer. Review the meeting transcript and identify potential risks, issues, blockers, "
        "or bottlenecks. For each risk, extract the description, impact_level (Low, Medium, High, Critical), "
        "and a proposed mitigation_strategy discussed or recommended."
    ),
    output_schema=RiskOutput
)
