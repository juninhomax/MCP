# API Documentation

## MCP Brain API

Base URL: `http://localhost:8000/api/v1`

### Authentication

All endpoints (except `/auth/token`) require Bearer token authentication:

```
Authorization: Bearer <token>
```

### Endpoints

#### Generate Token

```http
POST /auth/token?slave_id=<id>&scopes=<scope1,scope2>
```

**Response**:
```json
{
  "token": "generated-token-string",
  "expires_in_hours": 24
}
```

#### Create Task

```http
POST /tasks
Authorization: Bearer <token>
Content-Type: application/json

{
  "request": "Check status of nginx service on Linux server",
  "dry_run": false,
  "priority": "medium"
}
```

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "message": "Task created and executed"
}
```

#### Get Task Status

```http
GET /tasks/{task_id}
Authorization: Bearer <token>
```

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "user_request": "Check status of nginx service",
  "status": "completed",
  "reasoning_steps": [
    {
      "step_id": "...",
      "thought": "Need to check systemd service status",
      "action": "linux.systemd_status",
      "observation": "{...}"
    }
  ],
  "execution_plan": {
    "plan_id": "...",
    "steps": [
      {
        "slave_type": "linux",
        "tool": "systemd_status",
        "parameters": {"service": "nginx"},
        "justification": "Check nginx service status"
      }
    ]
  },
  "result": {
    "steps": [
      {
        "step": 0,
        "success": true,
        "output": "● nginx.service - A high performance web server..."
      }
    ]
  },
  "created_at": "2026-01-10T15:39:00Z",
  "completed_at": "2026-01-10T15:39:05Z"
}
```

#### Register Slave

```http
POST /slaves/register
Authorization: Bearer <token>
Content-Type: application/json

{
  "slave_id": "linux-slave-01",
  "slave_type": "linux",
  "endpoint": "http://192.168.1.100:8001",
  "capabilities": ["linux_exec", "git_status", "docker_ps"]
}
```

**Response**:
```json
{
  "status": "registered",
  "slave_id": "linux-slave-01"
}
```

#### Check Slave Health

```http
GET /slaves/{slave_id}/health
Authorization: Bearer <token>
```

**Response**:
```json
{
  "slave_id": "linux-slave-01",
  "healthy": true
}
```

## MCP Slave JSON-RPC API

Base URL: `http://localhost:8001/jsonrpc` (Linux) or `http://localhost:8002/jsonrpc` (Windows)

### Execute Tool

```http
POST /jsonrpc
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "execute_tool",
  "params": {
    "tool_name": "linux_exec",
    "parameters": {
      "command": "ls -la /tmp"
    },
    "dry_run": false,
    "timeout": 30
  },
  "id": "1"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "success": true,
    "output": "total 24\ndrwxrwxrwt  8 root root 4096 Jan 10 15:39 .\n...",
    "error": null,
    "exit_code": 0,
    "execution_time": 0.123,
    "dry_run": false
  },
  "id": "1"
}
```

### List Tools

```http
POST /jsonrpc
Content-Type: application/json

{
  "jsonrpc": "2.0",
  "method": "list_tools",
  "params": {},
  "id": "2"
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "result": {
    "tools": [
      {
        "name": "linux_exec",
        "description": "Execute a safe bash command on Linux",
        "tool_type": "linux",
        "input_schema": {
          "type": "object",
          "properties": {
            "command": {"type": "string"},
            "cwd": {"type": "string"}
          },
          "required": ["command"]
        }
      }
    ]
  },
  "id": "2"
}
```

## Error Responses

### JSON-RPC Errors

```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32601,
    "message": "Method not found",
    "data": null
  },
  "id": "1"
}
```

**Error Codes**:
- `-32700`: Parse error
- `-32600`: Invalid request
- `-32601`: Method not found
- `-32602`: Invalid params
- `-32603`: Internal error
- `-32000`: Server error
- `-32001`: Unauthorized
- `-32002`: Forbidden
- `-32003`: Execution failed

### HTTP Errors

```json
{
  "detail": "Invalid or expired token"
}
```

**Status Codes**:
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not found
- `500`: Internal server error

## Examples

### Example 1: Check Docker Containers

```bash
# Get token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/token?slave_id=admin&scopes=*" | jq -r '.token')

# Create task
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "List all running Docker containers",
    "dry_run": false
  }'
```

### Example 2: Read Windows Event Log

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show last 5 Application event log entries",
    "dry_run": false
  }'
```

### Example 3: Dry Run Mode

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Restart nginx service",
    "dry_run": true
  }'
```

## Rate Limiting

Currently not implemented. Future versions will include:
- Per-token rate limits
- Per-slave rate limits
- Configurable limits

## Webhooks

Future feature for async task notifications.
