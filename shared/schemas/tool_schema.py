from typing import Any, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ToolType(str, Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    GENERIC = "generic"


class ToolInputSchema(BaseModel):
    type: str = "object"
    properties: dict[str, Any]
    required: list[str] = Field(default_factory=list)


class ToolDefinition(BaseModel):
    name: str
    description: str
    tool_type: ToolType
    input_schema: ToolInputSchema
    dangerous: bool = False
    requires_approval: bool = False


class ToolExecutionRequest(BaseModel):
    tool_name: str
    parameters: dict[str, Any]
    dry_run: bool = False
    timeout: int = 30


class ToolExecutionResult(BaseModel):
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    execution_time: float
    dry_run: bool = False
