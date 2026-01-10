# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-01-10

### Added - Phase 1: Foundations

#### MCP Brain
- LLM integration (Ollama, GLM-4)
- Multi-step reasoning engine
- Task orchestration and planning
- Slave manager for distributed execution
- REST API with FastAPI
- Token-based authentication
- Structured JSON logging
- Dry-run mode support

#### MCP Slave Linux
- Bash command execution
- Git operations (status)
- Docker management (ps)
- Kubernetes operations (kubectl get)
- Systemd service status
- File read operations
- Command validation and allowlist
- JSON-RPC 2.0 protocol

#### MCP Slave Windows
- PowerShell command execution
- Windows service management
- Process information
- Event log access
- File operations
- Path testing
- Command validation for Windows

#### Shared Libraries
- JSON-RPC 2.0 implementation
- Tool schema definitions
- Authentication manager
- Command validator with dangerous pattern detection
- Security utilities

#### Documentation
- Architecture documentation
- Deployment guide
- API documentation
- Usage guide with examples
- Contributing guidelines

#### Testing
- Unit tests for validator
- Unit tests for authentication
- Unit tests for JSON-RPC
- Test scripts for platform validation

#### DevOps
- Docker support (Dockerfile for each component)
- Docker Compose configuration
- Startup/shutdown scripts (Linux & Windows)
- Health check endpoints

### Security
- Token-based authentication with expiration
- Command allowlist enforcement
- Dangerous pattern detection
- Dry-run mode for safe testing
- Audit logging for all operations
- No direct command execution from Brain

### Philosophy
- LLM never trusts itself
- Every action is justified, validated, traceable, and reversible
- Strict separation between decision (Brain) and execution (Slaves)
- Security-first approach

## [Unreleased]

### Planned - Phase 2: Tools & Security
- Enhanced tool registry
- JSON Schema validation
- Token rotation
- Enhanced structured logging
- PostgreSQL audit storage
- Redis state management

### Planned - Phase 3: Multi-slaves
- Intelligent routing
- Retry & fallback mechanisms
- Load balancing
- Multiple slaves per type

### Planned - Phase 4: Advanced AI
- Improved multi-step reasoning
- Planning/execution separation
- Long context support
- RAG for infrastructure documentation

### Planned - Phase 5: Production
- Prometheus metrics
- Grafana dashboards
- mTLS support
- VPN integration (WireGuard)
- Backup & rollback capabilities
- Enhanced observability

## Version History

- **0.1.0** - Initial release (Phase 1 complete)
  - Core Brain functionality
  - Linux Slave
  - Windows Slave
  - Basic security
  - Documentation
