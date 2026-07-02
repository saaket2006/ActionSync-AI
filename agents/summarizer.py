from google.adk import Agent
from schemas.schemas import SummarizerOutput
from config.settings import settings

summarizer_agent = Agent(
    name="summarizer_agent",
    description="Analyzes meeting transcripts and extracts executive summaries, key topics, and background context.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are an expert executive assistant. Analyze the provided meeting transcript segments. "
        "Synthesize the discussions and produce a highly detailed, comprehensive, and elaborated executive summary. "
        "Avoid making it brief or overly concise. Elaborate on the primary themes, contextual background, "
        "key arguments, concerns raised by participants, and the general trajectory of the discussion. "
        "Ensure the summary captures the depth of the meeting. Provide a thorough breakdown of the meeting "
        "context (purpose, participants, tone) and detailed, descriptive key topics discussed."
    ),
    output_schema=SummarizerOutput
)
