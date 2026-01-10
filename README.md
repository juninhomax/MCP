# MCP Brain / Slaves - Distributed AI Infrastructure Platform

## 🎯 Overview

A distributed MCP platform enabling a local LLM to reason, decide, orchestrate, and execute technical actions on heterogeneous infrastructure (Linux/Windows) via secure MCP Slaves.

## 🏗️ Architecture

### MCP Brain (Master)
- Decision-making engine
- LLM inference (local or API)
- Multi-step reasoning
- Tool routing and orchestration
- No direct system command execution

### MCP Slaves (Execution Agents)
- **Linux Slave**: bash, git, docker, kubectl, systemd
- **Windows Slave**: PowerShell, Services, Registry, IIS
- Sandboxed execution only
- No business logic or decision-making

## 🔐 Security

- HTTPS mandatory
- Token-based authentication per slave
- JSON-RPC 2.0 protocol
- Command allowlist
- Full audit trail

## 📦 Project Structure

```
mcp-brain-slaves/
├── brain/              # MCP Brain (Master)
│   ├── api/           # FastAPI endpoints
│   ├── llm/           # LLM integration
│   ├── orchestrator/  # Task orchestration
│   └── models/        # Data models
├── slaves/            # MCP Slaves
│   ├── linux/         # Linux agent
│   └── windows/       # Windows agent
├── shared/            # Shared libraries
│   ├── security/      # Auth & validation
│   ├── protocol/      # JSON-RPC
│   └── schemas/       # Tool schemas
├── tests/             # Test suite
└── docs/              # Documentation
```

## 🚀 Quick Start

### MCP Brain

```bash
cd brain
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### MCP Slave Linux

```bash
cd slaves/linux
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### MCP Slave Windows

```powershell
cd slaves\windows
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8002
```

## 🧪 Testing

```bash
pytest tests/ -v
```

## 📊 Observability

- Structured JSON logs
- MCP call traces
- AI decision history
- Command execution journal

## 🛠️ Current Phase: Phase 1 - Foundations

- [x] MCP Brain minimal
- [x] 1 LLM local integration
- [x] 1 Slave Linux
- [x] JSON-RPC basic protocol

## 🧠 Philosophy

**The LLM never trusts itself**

Every action is:
- Justified
- Validated
- Traceable
- Reversible

## 📝 License

MIT
