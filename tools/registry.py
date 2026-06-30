import logging
from typing import Dict, Any, Callable, Optional

logger = logging.getLogger("actionsync.tools")

class BaseActionSyncTool:
    """Base interface for all custom tools in the ActionSync AI platform.
    
    Exposes:
    - initialize(): Pre-execution setup (e.g. loading models, establishing connections).
    - execute(): Runs the primary tool logic.
    - validate(): Validates the generated output of the tool.
    - shutdown(): Cleans up resources.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.initialized = False

    def initialize(self) -> None:
        self.initialized = True
        logger.info(f"Initialized tool: {self.name}")

    def execute(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Subclasses must implement the execute method.")

    def validate(self, output: Any) -> bool:
        """Validates tool execution output. Subclasses can override this."""
        return True

    def shutdown(self) -> None:
        self.initialized = False
        logger.info(f"Shut down tool: {self.name}")


class ToolRegistry:
    """Centralized Tool Registry to manage the lifecycle of all tools."""
    def __init__(self):
        self._tools: Dict[str, BaseActionSyncTool] = {}

    def register(self, tool: BaseActionSyncTool) -> None:
        """Registers a tool with the registry."""
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def initialize_all(self) -> None:
        """Initializes all registered tools."""
        for tool in self._tools.values():
            if not tool.initialized:
                try:
                    tool.initialize()
                except Exception as e:
                    logger.error(f"Failed to initialize tool {tool.name}: {e}")

    def get_tool(self, name: str) -> BaseActionSyncTool:
        """Retrieves a registered tool by name."""
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' is not registered.")
        return self._tools[name]

    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Executes a tool by name with its validation check."""
        tool = self.get_tool(name)
        if not tool.initialized:
            tool.initialize()
        
        try:
            output = tool.execute(*args, **kwargs)
            if not tool.validate(output):
                raise ValueError(f"Tool '{name}' output failed validation checks.")
            return output
        except Exception as e:
            logger.error(f"Error executing tool '{name}': {e}")
            raise e

    def shutdown_all(self) -> None:
        """Shuts down and cleans up all registered tools."""
        for tool in self._tools.values():
            if tool.initialized:
                try:
                    tool.shutdown()
                except Exception as e:
                    logger.error(f"Error shutting down tool {tool.name}: {e}")

tool_registry = ToolRegistry()
