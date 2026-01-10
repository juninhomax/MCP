from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
from pydantic import BaseModel
from brain.orchestrator.brain import MCPBrain
from brain.models.task import Task, SlaveInfo
from shared.security.auth import AuthManager, TokenInfo
import structlog

logger = structlog.get_logger()

router = APIRouter()
brain = MCPBrain()
auth_manager = AuthManager()


class TaskRequest(BaseModel):
    request: str
    dry_run: bool = False
    priority: str = "medium"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class SlaveRegistrationRequest(BaseModel):
    slave_id: str
    slave_type: str
    endpoint: str
    capabilities: list[str] = []


async def verify_token(authorization: Optional[str] = Header(None)) -> TokenInfo:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = authorization.replace("Bearer ", "")
    token_info = auth_manager.validate_token(token)
    
    if not token_info:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return token_info


@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_request: TaskRequest,
    token_info: TokenInfo = Depends(verify_token)
):
    logger.info(
        "task_request_received",
        request=task_request.request,
        dry_run=task_request.dry_run,
        requester=token_info.slave_id
    )
    
    task = await brain.process_request(
        user_request=task_request.request,
        dry_run=task_request.dry_run
    )
    
    return TaskResponse(
        task_id=task.task_id,
        status=task.status.value,
        message=f"Task created and {'planned' if task_request.dry_run else 'executed'}"
    )


@router.get("/tasks/{task_id}")
async def get_task(
    task_id: str,
    token_info: TokenInfo = Depends(verify_token)
):
    task = brain.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.post("/slaves/register")
async def register_slave(
    registration: SlaveRegistrationRequest,
    token_info: TokenInfo = Depends(verify_token)
):
    slave_info = SlaveInfo(
        slave_id=registration.slave_id,
        slave_type=registration.slave_type,
        endpoint=registration.endpoint,
        status="online",
        capabilities=registration.capabilities
    )
    
    brain.slave_manager.register_slave(slave_info)
    
    logger.info(
        "slave_registered",
        slave_id=registration.slave_id,
        slave_type=registration.slave_type
    )
    
    return {"status": "registered", "slave_id": registration.slave_id}


@router.get("/slaves/{slave_id}/health")
async def check_slave_health(
    slave_id: str,
    token_info: TokenInfo = Depends(verify_token)
):
    is_healthy = await brain.slave_manager.health_check(slave_id)
    return {"slave_id": slave_id, "healthy": is_healthy}


@router.post("/auth/token")
async def generate_token(slave_id: str, scopes: list[str] = None):
    token = auth_manager.generate_token(
        slave_id=slave_id,
        scopes=scopes or ["*"],
        expires_in_hours=24
    )
    return {"token": token, "expires_in_hours": 24}


@router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "mcp-brain"}
