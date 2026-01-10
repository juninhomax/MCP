import subprocess
import time
from typing import Optional
from shared.schemas.tool_schema import ToolExecutionResult
from shared.security.validator import CommandValidator
from slaves.linux.config import settings
import structlog

logger = structlog.get_logger()


class LinuxExecutor:
    def __init__(self):
        self.validator = CommandValidator(allowlist=settings.allowed_commands)
    
    async def execute_command(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 30,
        dry_run: bool = False
    ) -> ToolExecutionResult:
        start_time = time.time()
        
        is_valid, error_msg = self.validator.validate(command, platform="linux")
        if not is_valid:
            logger.warning("command_rejected", command=command, reason=error_msg)
            return ToolExecutionResult(
                success=False,
                error=f"Command validation failed: {error_msg}",
                execution_time=time.time() - start_time,
                dry_run=dry_run
            )
        
        if dry_run:
            logger.info("dry_run_command", command=command, cwd=cwd)
            return ToolExecutionResult(
                success=True,
                output=f"[DRY RUN] Would execute: {command}",
                execution_time=time.time() - start_time,
                dry_run=True
            )
        
        try:
            logger.info("executing_command", command=command, cwd=cwd, timeout=timeout)
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            execution_time = time.time() - start_time
            
            logger.info(
                "command_completed",
                command=command,
                exit_code=result.returncode,
                execution_time=execution_time
            )
            
            return ToolExecutionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                exit_code=result.returncode,
                execution_time=execution_time,
                dry_run=False
            )
            
        except subprocess.TimeoutExpired:
            logger.error("command_timeout", command=command, timeout=timeout)
            return ToolExecutionResult(
                success=False,
                error=f"Command timed out after {timeout} seconds",
                execution_time=time.time() - start_time,
                dry_run=False
            )
        
        except Exception as e:
            logger.error("command_execution_error", command=command, error=str(e))
            return ToolExecutionResult(
                success=False,
                error=str(e),
                execution_time=time.time() - start_time,
                dry_run=False
            )
    
    async def execute_tool(
        self,
        tool_name: str,
        parameters: dict,
        dry_run: bool = False
    ) -> ToolExecutionResult:
        if tool_name == "linux_exec":
            return await self.execute_command(
                command=parameters.get("command"),
                cwd=parameters.get("cwd"),
                timeout=parameters.get("timeout", 30),
                dry_run=dry_run
            )
        
        elif tool_name == "git_status":
            command = f"git -C {parameters.get('repo_path')} status"
            return await self.execute_command(command, dry_run=dry_run)
        
        elif tool_name == "docker_ps":
            command = "docker ps" + (" -a" if parameters.get("all") else "")
            return await self.execute_command(command, dry_run=dry_run)
        
        elif tool_name == "kubectl_get":
            namespace = parameters.get("namespace", "default")
            command = f"kubectl get {parameters.get('resource')} -n {namespace}"
            return await self.execute_command(command, dry_run=dry_run)
        
        elif tool_name == "systemd_status":
            command = f"systemctl status {parameters.get('service')}"
            return await self.execute_command(command, dry_run=dry_run)
        
        elif tool_name == "file_read":
            lines = parameters.get("lines")
            command = f"cat {parameters.get('path')}"
            if lines:
                command = f"head -n {lines} {parameters.get('path')}"
            return await self.execute_command(command, dry_run=dry_run)
        
        else:
            return ToolExecutionResult(
                success=False,
                error=f"Unknown tool: {tool_name}",
                execution_time=0.0,
                dry_run=dry_run
            )
