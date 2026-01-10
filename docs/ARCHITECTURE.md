# Architecture Documentation

## System Overview

The MCP Brain/Slaves platform is a distributed AI infrastructure orchestration system that separates decision-making (Brain) from execution (Slaves).

## Components

### 1. MCP Brain (Master)

**Location**: `brain/`

**Responsibilities**:
- LLM-based reasoning and decision making
- Task decomposition and planning
- Slave orchestration
- Result aggregation
- Security validation

**Key Modules**:
- `llm/provider.py`: LLM integration (Ollama, GLM-4)
- `orchestrator/brain.py`: Main orchestration logic
- `orchestrator/slave_manager.py`: Slave communication
- `api/routes.py`: REST API endpoints
- `models/task.py`: Task and execution models

**API Endpoints**:
- `POST /api/v1/tasks`: Create and execute tasks
- `GET /api/v1/tasks/{task_id}`: Get task status
- `POST /api/v1/slaves/register`: Register a slave
- `GET /api/v1/slaves/{slave_id}/health`: Check slave health
- `POST /api/v1/auth/token`: Generate auth token

### 2. MCP Slave Linux

**Location**: `slaves/linux/`

**Responsibilities**:
- Execute bash commands
- Git operations
- Docker management
- Kubernetes operations
- Systemd service management
- File operations

**Tools**:
- `linux_exec`: Execute bash commands
- `git_status`: Git repository status
- `docker_ps`: List Docker containers
- `kubectl_get`: Get Kubernetes resources
- `systemd_status`: Service status
- `file_read`: Read file contents

### 3. MCP Slave Windows

**Location**: `slaves/windows/`

**Responsibilities**:
- Execute PowerShell commands
- Windows service management
- Process management
- Event log access
- File operations

**Tools**:
- `powershell_exec`: Execute PowerShell commands
- `get_service`: Get service status
- `get_process`: Get process information
- `get_eventlog`: Read event logs
- `file_read`: Read file contents
- `test_path`: Test path existence

### 4. Shared Libraries

**Location**: `shared/`

**Components**:
- `protocol/jsonrpc.py`: JSON-RPC 2.0 implementation
- `schemas/tool_schema.py`: Tool definition schemas
- `security/auth.py`: Token-based authentication
- `security/validator.py`: Command validation

## Communication Flow

```
User Request
    ↓
MCP Brain (LLM Analysis)
    ↓
Task Decomposition
    ↓
Execution Plan
    ↓
JSON-RPC Calls → MCP Slaves
    ↓
Command Execution
    ↓
Results Aggregation
    ↓
Response to User
```

## Security Architecture

### Authentication
- Token-based authentication per slave
- Bearer token in HTTP headers
- Token expiration support
- Scope-based access control

### Command Validation
- Allowlist of safe commands
- Dangerous pattern detection
- Platform-specific validation
- Dry-run mode support

### Audit Trail
- Structured JSON logging
- Request/response tracking
- Command execution history
- Decision reasoning logs

## Data Models

### Task
```python
{
    "task_id": "uuid",
    "user_request": "string",
    "status": "pending|analyzing|planning|executing|completed|failed",
    "reasoning_steps": [...],
    "execution_plan": {...},
    "result": {...}
}
```

### Tool Execution
```python
{
    "tool_name": "string",
    "parameters": {...},
    "dry_run": bool,
    "timeout": int
}
```

### Tool Result
```python
{
    "success": bool,
    "output": "string",
    "error": "string",
    "exit_code": int,
    "execution_time": float
}
```

## Deployment Architecture

### Development
```
localhost:8000 - MCP Brain
localhost:8001 - Linux Slave
localhost:8002 - Windows Slave
```

### Production
```
brain.internal:8000 - MCP Brain (behind VPN)
linux-slave-01.internal:8001 - Linux Slave
linux-slave-02.internal:8001 - Linux Slave
windows-slave-01.internal:8002 - Windows Slave
```

## Scalability

- Horizontal scaling of slaves
- Load balancing via slave manager
- Stateless execution agents
- Redis for state management (future)
- PostgreSQL for audit logs (future)

## Observability

### Logging
- Structured JSON logs
- Log levels: INFO, WARNING, ERROR
- Contextual information (task_id, slave_id, etc.)

### Metrics (Future)
- Task execution time
- Success/failure rates
- Slave health status
- LLM inference time

### Tracing (Future)
- End-to-end request tracing
- Distributed tracing support
- Performance profiling
