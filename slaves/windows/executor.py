import subprocess
import time
from typing import Optional
from shared.schemas.tool_schema import ToolExecutionResult
from shared.security.validator import CommandValidator
from slaves.windows.config import settings
import structlog

logger = structlog.get_logger()


class WindowsExecutor:
    def __init__(self):
        self.validator = CommandValidator(allowlist=settings.allowed_commands)
    
    async def execute_powershell(
        self,
        command: str,
        cwd: Optional[str] = None,
        timeout: int = 30,
        dry_run: bool = False
    ) -> ToolExecutionResult:
        start_time = time.time()
        
        is_valid, error_msg = self.validator.validate(command, platform="windows")
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
            logger.info("executing_powershell", command=command, cwd=cwd, timeout=timeout)
            
            ps_command = ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command]
            
            result = subprocess.run(
                ps_command,
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
        if tool_name == "powershell_exec":
            return await self.execute_powershell(
                command=parameters.get("command"),
                cwd=parameters.get("cwd"),
                timeout=parameters.get("timeout", 30),
                dry_run=dry_run
            )
        
        elif tool_name == "get_service":
            command = f"Get-Service -Name '{parameters.get('service_name')}' | Format-List"
            return await self.execute_powershell(command, dry_run=dry_run)
        
        elif tool_name == "get_process":
            process_name = parameters.get("process_name")
            if process_name:
                command = f"Get-Process -Name '{process_name}' | Format-Table"
            else:
                command = "Get-Process | Format-Table"
            return await self.execute_powershell(command, dry_run=dry_run)
        
        elif tool_name == "get_eventlog":
            log_name = parameters.get("log_name")
            newest = parameters.get("newest", 10)
            command = f"Get-EventLog -LogName '{log_name}' -Newest {newest} | Format-Table"
            return await self.execute_powershell(command, dry_run=dry_run)
        
        elif tool_name == "file_read":
            path = parameters.get("path")
            lines = parameters.get("lines")
            if lines:
                command = f"Get-Content -Path '{path}' -TotalCount {lines}"
            else:
                command = f"Get-Content -Path '{path}'"
            return await self.execute_powershell(command, dry_run=dry_run)
        
        elif tool_name == "test_path":
            command = f"Test-Path -Path '{parameters.get('path')}'"
            return await self.execute_powershell(command, dry_run=dry_run)
        
        else:
            return ToolExecutionResult(
                success=False,
                error=f"Unknown tool: {tool_name}",
                execution_time=0.0,
                dry_run=dry_run
            )
