from google.adk import Agent
from schemas.schemas import AccountabilityOutput
from config.settings import settings

accountability_agent = Agent(
    name="accountability_agent",
    description="Ensures clear ownership of action items, builds assignment summaries, and schedules follow-up check-ins.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are an execution and operations lead. Review the decisions, risks, and action items. "
        "Create an accountability structure: summarize assignments, confirm ownership for each task, "
        "and establish a concrete follow_up_schedule (e.g. 'John to update in Slack by Friday', "
        "'Weekly status checks on Thursdays'). "
        "Provide: accountability_summary, assignments_confirmed, and follow_up_schedule."
    ),
    output_schema=AccountabilityOutput
)
