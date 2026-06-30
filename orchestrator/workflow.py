import asyncio
import logging
from typing import AsyncGenerator, Any, Dict
from google.adk.workflow._base_node import BaseNode
from google.adk.agents.context import Context
from schemas.schemas import PipelineOutput

# Import agents
from agents.summarizer import summarizer_agent
from agents.decision import decision_agent
from agents.action_item import action_item_agent
from agents.timeline import timeline_agent
from agents.risk import risk_agent
from agents.validator import validator_agent
from agents.community_impact import community_impact_agent
from agents.accountability import accountability_agent
from agents.clarification import clarification_agent

logger = logging.getLogger("actionsync.orchestrator")

class ActionSyncOrchestrator(BaseNode):
    """Google ADK Orchestrator Node.
    
    Coordinates the ActionSync AI Meeting Intelligence pipeline:
    - Runs Summarizer, Decision, Action Item, Timeline, and Risk agents concurrently.
    - Synchronizes their outputs and passes them to Validator.
    - Sequentially executes Community Impact, Accountability, and Clarification agents.
    - Combines all outputs into a validated PipelineOutput structure.
    """
    name: str = "ActionSyncOrchestrator"
    description: str = "ActionSync AI Multi-Agent Coordinator Node"
    output_schema: Any = PipelineOutput

    async def _run_impl(self, *, ctx: Context, node_input: Any) -> AsyncGenerator[Any, None]:
        """Orchestrates the multi-agent coordination pipeline.
        
        Args:
            ctx: Execution context provided by ADK.
            node_input: The input transcript (raw or clean string).
        """
        logger.info("ActionSyncOrchestrator pipeline started.")
        
        if not isinstance(node_input, str):
            # Extract text if passed as a complex object/Content
            from google.adk.utils.context_utils import extract_text_from_content
            node_input = extract_text_from_content(node_input)

        # 1. Parallel Execution Phase (Summarizer, Decision, Action Item, Timeline, Risk)
        logger.info("Dispatching parallel extraction agents: Summarizer, Decision, Action Item, Timeline, Risk.")
        
        tasks = [
            ctx.run_node(summarizer_agent, node_input),
            ctx.run_node(decision_agent, node_input),
            ctx.run_node(action_item_agent, node_input),
            ctx.run_node(timeline_agent, node_input),
            ctx.run_node(risk_agent, node_input)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for task exceptions
        for idx, res in enumerate(results):
            if isinstance(res, Exception):
                logger.error(f"Agent task {idx} failed with error: {res}")
                raise res

        parallel_outputs = {
            "summarizer": results[0],
            "decision": results[1],
            "action_item": results[2],
            "timeline": results[3],
            "risk": results[4]
        }
        
        logger.info("Parallel extraction complete. Proceeding to validation.")

        # 2. Sequential Execution Phase (Validator, Community Impact, Accountability, Clarification)
        # We pass the consolidated dictionary of parallel results to downstream agents
        # Since ADK run_node expects input matching the agent's schema, we format it as string/dict
        
        # Validator
        logger.info("Running Validator Agent...")
        validator_res = await ctx.run_node(validator_agent, str(parallel_outputs))
        
        # Community Impact
        logger.info("Running Community Impact Agent...")
        community_res = await ctx.run_node(community_impact_agent, str(parallel_outputs))
        
        # Accountability
        logger.info("Running Accountability Agent...")
        accountability_res = await ctx.run_node(accountability_agent, str(parallel_outputs))
        
        # Clarification
        logger.info("Running Clarification Agent...")
        clarification_res = await ctx.run_node(clarification_agent, str(parallel_outputs))

        # 3. Aggregate Outputs
        logger.info("Aggregating multi-agent results.")
        pipeline_output = {
            "summarizer": parallel_outputs["summarizer"],
            "decision": parallel_outputs["decision"],
            "action_item": parallel_outputs["action_item"],
            "timeline": parallel_outputs["timeline"],
            "risk": parallel_outputs["risk"],
            "validator": validator_res,
            "community_impact": community_res,
            "accountability": accountability_res,
            "clarification": clarification_res
        }
        
        # Yield the final validated pipeline output
        yield pipeline_output
        logger.info("ActionSyncOrchestrator pipeline successfully completed.")

# Single instance of orchestrator to be used in runners
actionsync_orchestrator = ActionSyncOrchestrator(name="actionsync_orchestrator")
