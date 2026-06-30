from google.adk import Agent
from agents.summarizer import summarizer_agent
from agents.decision import decision_agent
from agents.action_item import action_item_agent
from agents.timeline import timeline_agent
from agents.risk import risk_agent
from agents.validator import validator_agent
from agents.community_impact import community_impact_agent
from agents.accountability import accountability_agent
from agents.clarification import clarification_agent

def test_agents_registration_and_types():
    """Asserts that all nine ADK agents are instances of google.adk.Agent and have correct names."""
    agents_list = [
        (summarizer_agent, "summarizer_agent"),
        (decision_agent, "decision_agent"),
        (action_item_agent, "action_item_agent"),
        (timeline_agent, "timeline_agent"),
        (risk_agent, "risk_agent"),
        (validator_agent, "validator_agent"),
        (community_impact_agent, "community_impact_agent"),
        (accountability_agent, "accountability_agent"),
        (clarification_agent, "clarification_agent")
    ]
    
    for agent, expected_name in agents_list:
        assert isinstance(agent, Agent)
        assert agent.name == expected_name
        assert agent.instruction is not None
        assert agent.output_schema is not None
