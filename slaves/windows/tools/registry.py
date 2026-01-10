from typing import Callable, Any
from shared.schemas.tool_schema import ToolDefinition, ToolType, ToolInputSchema
import structlog

logger = structlog.get_logger()


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, tuple[ToolDefinition, Callable]] = {}
    
    def register(self, definition: ToolDefinition, handler: Callable):
        self._tools[definition.name] = (definition, handler)
        logger.info("tool_registered", tool_name=definition.name)
    
    def get_tool(self, name: str) -> tuple[ToolDefinition, Callable] | None:
        return self._tools.get(name)
    
    def list_tools(self) -> list[ToolDefinition]:
        return [definition for definition, _ in self._tools.values()]
    
    def has_tool(self, name: str) -> bool:
        return name in self._tools


registry = ToolRegistry()


def register_windows_tools():
    registry.register(
        ToolDefinition(
            name="powershell_exec",
            description="Execute a safe PowerShell command on Windows",
            tool_type=ToolType.WINDOWS,
            input_schema=ToolInputSchema(
                properties={
                    "command": {"type": "string", "description": "PowerShell command to execute"},
                    "cwd": {"type": "string", "description": "Working directory"}
                },
                required=["command"]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
    
    registry.register(
        ToolDefinition(
            name="get_service",
            description="Get Windows service status",
            tool_type=ToolType.WINDOWS,
            input_schema=ToolInputSchema(
                properties={
                    "service_name": {"type": "string", "description": "Service name"}
                },
                required=["service_name"]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
    
    registry.register(
        ToolDefinition(
            name="get_process",
            description="Get Windows process information",
            tool_type=ToolType.WINDOWS,
            input_schema=ToolInputSchema(
                properties={
                    "process_name": {"type": "string", "description": "Process name (optional)"}
                },
                required=[]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
    
    registry.register(
        ToolDefinition(
            name="get_eventlog",
            description="Get Windows Event Log entries",
            tool_type=ToolType.WINDOWS,
            input_schema=ToolInputSchema(
                properties={
                    "log_name": {"type": "string", "description": "Log name (Application, System, Security)"},
                    "newest": {"type": "integer", "description": "Number of newest entries"}
                },
                required=["log_name"]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
    
    registry.register(
        ToolDefinition(
            name="file_read",
            description="Read file contents",
            tool_type=ToolType.WINDOWS,
            input_schema=ToolInputSchema(
                properties={
                    "path": {"type": "string", "description": "File path"},
                    "lines": {"type": "integer", "description": "Number of lines to read"}
                },
                required=["path"]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
    
    registry.register(
        ToolDefinition(
            name="test_path",
            description="Test if a path exists",
            tool_type=ToolType.WINDOWS,
            input_schema=ToolInputSchema(
                properties={
                    "path": {"type": "string", "description": "Path to test"}
                },
                required=["path"]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
