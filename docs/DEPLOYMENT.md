# Deployment Guide

## Prerequisites

### All Components
- Python 3.11+
- pip

### MCP Brain
- Ollama (for local LLM) OR GLM-4 API key
- Redis (optional, for state)
- PostgreSQL (optional, for audit)

### Linux Slave
- Linux OS (Ubuntu 20.04+, Debian 11+, etc.)
- bash, git, docker, kubectl (optional)

### Windows Slave
- Windows 10/11 or Windows Server 2019+
- PowerShell 5.1+

## Installation

### 1. MCP Brain

```bash
cd brain

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start the brain
python main.py
```

**Configuration** (`.env`):
```env
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5-coder:14b
LLM_API_BASE=http://localhost:11434
```

### 2. MCP Slave Linux

```bash
cd slaves/linux

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Start the slave
python main.py
```

**Configuration** (`.env`):
```env
SLAVE_ID=linux-slave-01
BRAIN_ENDPOINT=http://localhost:8000
AUTH_TOKEN=<generated-token>
```

### 3. MCP Slave Windows

```powershell
cd slaves\windows

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env with your settings

# Start the slave
python main.py
```

## Token Generation

Generate authentication tokens for slaves:

```bash
# Using curl
curl -X POST "http://localhost:8000/api/v1/auth/token?slave_id=linux-slave-01&scopes=*"

# Response:
# {"token": "your-token-here", "expires_in_hours": 24}
```

Copy the token to the slave's `.env` file:
```env
AUTH_TOKEN=your-token-here
```

## Docker Deployment

### MCP Brain

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY brain/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY brain/ .
COPY shared/ /app/shared/

EXPOSE 8000

CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t mcp-brain -f Dockerfile.brain .
docker run -d -p 8000:8000 --env-file brain/.env mcp-brain
```

### MCP Slave Linux

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY slaves/linux/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY slaves/linux/ .
COPY shared/ /app/shared/

EXPOSE 8001

CMD ["python", "main.py"]
```

## Docker Compose

```yaml
version: '3.8'

services:
  brain:
    build:
      context: .
      dockerfile: Dockerfile.brain
    ports:
      - "8000:8000"
    environment:
      - LLM_PROVIDER=ollama
      - LLM_API_BASE=http://ollama:11434
    depends_on:
      - ollama
    networks:
      - mcp-network

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - mcp-network

  linux-slave:
    build:
      context: .
      dockerfile: Dockerfile.linux
    ports:
      - "8001:8001"
    environment:
      - BRAIN_ENDPOINT=http://brain:8000
      - AUTH_TOKEN=${LINUX_SLAVE_TOKEN}
    networks:
      - mcp-network

  windows-slave:
    build:
      context: .
      dockerfile: Dockerfile.windows
    ports:
      - "8002:8002"
    environment:
      - BRAIN_ENDPOINT=http://brain:8000
      - AUTH_TOKEN=${WINDOWS_SLAVE_TOKEN}
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge

volumes:
  ollama-data:
```

## Production Considerations

### Security

1. **Use HTTPS**: Deploy behind reverse proxy (nginx, Traefik)
2. **VPN**: Use WireGuard or similar for slave communication
3. **mTLS**: Implement mutual TLS authentication
4. **Firewall**: Restrict access to internal network only
5. **Secrets**: Use environment variables or secret managers

### High Availability

1. **Multiple Slaves**: Deploy multiple slaves per type
2. **Load Balancing**: Use slave manager's routing
3. **Health Checks**: Monitor slave availability
4. **Failover**: Automatic retry on slave failure

### Monitoring

1. **Logs**: Centralize logs (ELK, Loki)
2. **Metrics**: Prometheus + Grafana
3. **Alerts**: Set up alerts for failures
4. **Tracing**: Implement distributed tracing

### Backup

1. **Database**: Regular PostgreSQL backups
2. **Configuration**: Version control all configs
3. **State**: Redis persistence or snapshots

## Troubleshooting

### Brain won't start
- Check LLM provider is accessible
- Verify Python version (3.11+)
- Check port 8000 is available

### Slave can't register
- Verify AUTH_TOKEN is correct
- Check BRAIN_ENDPOINT is reachable
- Ensure network connectivity

### Commands fail validation
- Check allowed_commands in config
- Review command validator rules
- Enable dry_run mode for testing

### LLM errors
- Verify Ollama is running
- Check model is downloaded: `ollama pull qwen2.5-coder:14b`
- Verify API key for GLM-4

## Health Checks

```bash
# Brain health
curl http://localhost:8000/health

# Linux slave health
curl http://localhost:8001/health

# Windows slave health
curl http://localhost:8002/health

# List available tools
curl http://localhost:8001/tools
```
