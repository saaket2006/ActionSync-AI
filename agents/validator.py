from google.adk import Agent
from schemas.schemas import ValidatorOutput
from config.settings import settings

validator_agent = Agent(
    name="validator_agent",
    description="Cross-checks and validates the combined outputs of the parallel extraction agents for consistency.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are a quality assurance auditor. You will receive the combined outputs of the parallel agents "
        "(Summarizer, Decision, Action Item, Timeline, Risk). "
        "Your task is to analyze these outputs and identify any inconsistencies, logical conflicts, or missing "
        "details (e.g. if a decision says 'John will take over project X', there should be a task assigned to John "
        "for project X, or a corresponding timeline milestone). "
        "Provide: is_valid (True if high-quality and consistent, False if major errors are found), "
        "a list of errors, and the reasons for your assessment."
    ),
    output_schema=ValidatorOutput
)
