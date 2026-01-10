from typing import Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ReasoningStep(BaseModel):
    step_id: str = Field(default_factory=lambda: str(uuid4()))
    thought: str
    action: Optional[str] = None
    observation: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ExecutionPlan(BaseModel):
    plan_id: str = Field(default_factory=lambda: str(uuid4()))
    steps: list[dict[str, Any]]
    estimated_duration: Optional[int] = None
    requires_approval: bool = False
    dry_run: bool = False


class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    user_request: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    
    reasoning_steps: list[ReasoningStep] = Field(default_factory=list)
    execution_plan: Optional[ExecutionPlan] = None
    
    result: Optional[Any] = None
    error: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    
    metadata: dict[str, Any] = Field(default_factory=dict)


class SlaveInfo(BaseModel):
    slave_id: str
    slave_type: str
    endpoint: str
    status: str = "unknown"
    last_seen: Optional[datetime] = None
    capabilities: list[str] = Field(default_factory=list)
