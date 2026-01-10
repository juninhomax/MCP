# Usage Guide

## Quick Start

### 1. Start Ollama (for local LLM)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model
ollama pull qwen2.5-coder:14b

# Verify it's running
curl http://localhost:11434/api/tags
```

### 2. Start MCP Brain

```bash
cd brain
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python main.py
```

### 3. Generate Tokens

```bash
# Generate token for Linux slave
curl -X POST "http://localhost:8000/api/v1/auth/token?slave_id=linux-slave-01&scopes=*"

# Save the token
export LINUX_TOKEN="<token-from-response>"
```

### 4. Start Linux Slave

```bash
cd slaves/linux
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env

# Edit .env and add the token
echo "AUTH_TOKEN=$LINUX_TOKEN" >> .env

python main.py
```

### 5. Start Windows Slave (on Windows)

```powershell
cd slaves\windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env

# Edit .env and add the token
# Then start
python main.py
```

## Common Use Cases

### Infrastructure Monitoring

**Check service status**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Check if nginx service is running on Linux server"
  }'
```

**Monitor Docker containers**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "List all Docker containers and their status"
  }'
```

**Check disk space**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show disk usage on all mounted filesystems"
  }'
```

### Git Operations

**Repository status**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Get git status of repository at /home/user/project"
  }'
```

### Kubernetes Operations

**List pods**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "List all pods in the default namespace"
  }'
```

**Get service information**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show all services in production namespace"
  }'
```

### Windows Administration

**Check Windows service**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Get status of Windows Update service"
  }'
```

**View event logs**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Show last 10 Application event log entries"
  }'
```

**Process information**:
```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "List all running processes"
  }'
```

## Dry Run Mode

Test commands without executing them:

```bash
curl -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Restart all Docker containers",
    "dry_run": true
  }'
```

The response will show what would be executed without actually running it.

## Task Tracking

**Create a task**:
```bash
RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "request": "Check system load"
  }')

TASK_ID=$(echo $RESPONSE | jq -r '.task_id')
```

**Check task status**:
```bash
curl -X GET "http://localhost:8000/api/v1/tasks/$TASK_ID" \
  -H "Authorization: Bearer $TOKEN"
```

## Python Client Example

```python
import httpx
import json

class MCPClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": f"Bearer {token}"}
    
    async def create_task(self, request: str, dry_run: bool = False):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/v1/tasks",
                headers=self.headers,
                json={
                    "request": request,
                    "dry_run": dry_run
                }
            )
            return response.json()
    
    async def get_task(self, task_id: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/api/v1/tasks/{task_id}",
                headers=self.headers
            )
            return response.json()

# Usage
import asyncio

async def main():
    client = MCPClient("http://localhost:8000", "your-token")
    
    # Create task
    result = await client.create_task("List Docker containers")
    print(f"Task created: {result['task_id']}")
    
    # Get task details
    task = await client.get_task(result['task_id'])
    print(json.dumps(task, indent=2))

asyncio.run(main())
```

## Best Practices

### 1. Use Dry Run First
Always test with `dry_run: true` before executing potentially dangerous operations.

### 2. Specific Requests
Be specific in your requests:
- ❌ "Check the server"
- ✅ "Check nginx service status on Linux server"

### 3. Monitor Task Status
For long-running tasks, poll the task status endpoint.

### 4. Token Management
- Rotate tokens regularly
- Use different tokens for different slaves
- Revoke unused tokens

### 5. Error Handling
Always check the `success` field in responses:

```python
result = await client.create_task("...")
if result.get('status') == 'failed':
    print(f"Error: {result.get('error')}")
```

### 6. Logging
Enable audit logging in production:

```env
ENABLE_AUDIT=true
```

## Troubleshooting

### "Command validation failed"
The command is not in the allowlist. Check `allowed_commands` in config.

### "No slave available"
Ensure the slave is:
1. Running
2. Registered with the brain
3. Healthy (check `/health` endpoint)

### "LLM timeout"
Increase `REQUEST_TIMEOUT` in brain config or use a faster model.

### "Invalid or expired token"
Generate a new token using `/auth/token` endpoint.

## Advanced Usage

### Custom Allowlist

Edit slave config to add custom commands:

```python
# slaves/linux/config.py
allowed_commands: list[str] = [
    "ls", "cat", "grep",
    "my-custom-script",  # Add your command
]
```

### Multiple Slaves

Register multiple slaves of the same type for load balancing:

```bash
# Start slave 1
SLAVE_ID=linux-slave-01 PORT=8001 python main.py

# Start slave 2
SLAVE_ID=linux-slave-02 PORT=8011 python main.py
```

### Custom Tools

Add custom tools to slaves:

```python
# In slaves/linux/tools/registry.py
registry.register(
    ToolDefinition(
        name="my_custom_tool",
        description="My custom operation",
        tool_type=ToolType.LINUX,
        input_schema=ToolInputSchema(
            properties={
                "param1": {"type": "string"}
            },
            required=["param1"]
        )
    ),
    my_custom_handler
)
```
