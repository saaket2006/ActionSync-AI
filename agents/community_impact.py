from google.adk import Agent
from schemas.schemas import CommunityImpactOutput
from config.settings import settings

community_impact_agent = Agent(
    name="community_impact_agent",
    description="Assesses team dynamics, workload implications, and cultural alignment of meeting outcomes.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are an organizational psychologist. Examine the decisions, action items, and summary of the meeting. "
        "Evaluate the team/community impact: analyze if the deliverables impose excessive workload, "
        "how team collaboration and friction might change (team_dynamics), and whether the decisions "
        "align with general positive workplace culture and corporate values (cultural_alignment). "
        "Provide: impact_summary, team_dynamics detail, and cultural_alignment description."
    ),
    output_schema=CommunityImpactOutput
)
