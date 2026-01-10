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


def register_linux_tools():
    registry.register(
        ToolDefinition(
            name="linux_exec",
            description="Execute a safe bash command on Linux",
            tool_type=ToolType.LINUX,
            input_schema=ToolInputSchema(
                properties={
                    "command": {"type": "string", "description": "Command to execute"},
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
            name="git_status",
            description="Get git repository status",
            tool_type=ToolType.LINUX,
            input_schema=ToolInputSchema(
                properties={
                    "repo_path": {"type": "string", "description": "Path to git repository"}
                },
                required=["repo_path"]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
    
    registry.register(
        ToolDefinition(
            name="docker_ps",
            description="List running Docker containers",
            tool_type=ToolType.LINUX,
            input_schema=ToolInputSchema(
                properties={
                    "all": {"type": "boolean", "description": "Show all containers"}
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
            name="kubectl_get",
            description="Get Kubernetes resources",
            tool_type=ToolType.LINUX,
            input_schema=ToolInputSchema(
                properties={
                    "resource": {"type": "string", "description": "Resource type (pods, services, etc.)"},
                    "namespace": {"type": "string", "description": "Namespace"}
                },
                required=["resource"]
            ),
            dangerous=False,
            requires_approval=False
        ),
        None
    )
    
    registry.register(
        ToolDefinition(
            name="systemd_status",
            description="Get systemd service status",
            tool_type=ToolType.LINUX,
            input_schema=ToolInputSchema(
                properties={
                    "service": {"type": "string", "description": "Service name"}
                },
                required=["service"]
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
            tool_type=ToolType.LINUX,
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
