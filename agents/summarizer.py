from google.adk import Agent
from schemas.schemas import SummarizerOutput
from config.settings import settings

summarizer_agent = Agent(
    name="summarizer_agent",
    description="Analyzes meeting transcripts and extracts executive summaries, key topics, and background context.",
    model=settings.GEMINI_MODEL,
    instruction=(
        "You are an expert executive assistant. Analyze the provided meeting transcript segments. "
        "Synthesize the discussions and produce a clear, high-level executive summary, "
        "a list of key topics, and any meeting context (e.g. purpose of meeting, attendees, tone)."
    ),
    output_schema=SummarizerOutput
)
