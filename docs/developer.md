# Developer Guide: ActionSync AI

This document provides instructions for developers looking to extend, customize, and test ActionSync AI.

---

## 1. Running Automated Tests

ActionSync AI utilizes `pytest` for automated test verification.

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Modules
```bash
pytest tests/test_tools.py -v
pytest tests/test_agents.py -v
pytest tests/test_api.py -v
```

---

## 2. Adding a New Tool

All platform tools must register with the centralized tool registry to participate in agent lifecycles.

1. **Create the Tool File**: Add a new python file in `tools/` (e.g. `tools/my_tool.py`).
2. **Inherit from `BaseActionSyncTool`**:
   ```python
   from tools.registry import BaseActionSyncTool, tool_registry

   class MyTool(BaseActionSyncTool):
       def __init__(self):
           super().__init__(name="MyTool", description="Short description of tool execution.")

       def initialize(self) -> None:
           # Set up connections, models, etc.
           self.initialized = True

       def execute(self, arg1: str) -> str:
           # Tool processing logic
           return f"Processed: {arg1}"

       def validate(self, output: Any) -> bool:
           # Validate format
           return isinstance(output, str)

       def shutdown(self) -> None:
           # Resource cleanup
           self.initialized = False

   # Register with the global registry
   tool_registry.register(MyTool())
   ```
3. **Import inside `backend/routers/agents.py`** or main bootstrap file to ensure registration runs during system initialization.

---

## 3. Registering a New Agent

To add an agent to the pipeline:

1. **Define the Agent Profile**: Create a new file in `agents/` (e.g. `agents/my_agent.py`):
   ```python
   from google.adk import Agent
   from config.settings import settings
   from schemas.schemas import MyOutputSchema  # Define in schemas/schemas.py

   my_agent = Agent(
       name="my_agent",
       description="Brief agent description.",
       model=settings.GEMINI_MODEL,
       instruction="Prompt instructions for the LLM behavior.",
       output_schema=MyOutputSchema
   )
   ```
2. **Integrate with the Orchestrator**: Update `orchestrator/workflow.py` to import `my_agent`, insert it into the execution pipeline, and append its output to the consolidated `PipelineOutput` schema.
