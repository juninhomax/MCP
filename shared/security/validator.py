import re
from typing import Optional


class CommandValidator:
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"mkfs\.",
        r"dd\s+if=.*of=/dev/",
        r":\(\)\{\s*:\|:&\s*\};:",
        r"curl.*\|\s*bash",
        r"wget.*\|\s*sh",
        r"eval\s*\(",
        r"exec\s*\(",
        r"shutdown",
        r"reboot",
        r"init\s+[06]",
        r"systemctl\s+(halt|poweroff|reboot)",
        r"format\s+[a-z]:",
        r"del\s+/[fqs]\s+[a-z]:\\",
    ]
    
    ALLOWED_COMMANDS_LINUX = [
        "ls", "cat", "grep", "find", "ps", "top", "df", "du",
        "git", "docker", "kubectl", "systemctl status",
        "journalctl", "tail", "head", "wc", "awk", "sed"
    ]
    
    ALLOWED_COMMANDS_WINDOWS = [
        "dir", "type", "findstr", "Get-Process", "Get-Service",
        "Get-EventLog", "Test-Path", "Get-Content", "Select-String"
    ]
    
    def __init__(self, allowlist: Optional[list[str]] = None):
        self.allowlist = allowlist or []
    
    def is_dangerous(self, command: str) -> tuple[bool, Optional[str]]:
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                return True, f"Dangerous pattern detected: {pattern}"
        return False, None
    
    def is_allowed(self, command: str, platform: str = "linux") -> tuple[bool, Optional[str]]:
        if self.allowlist:
            # Pour PowerShell, verifier si au moins une cmdlet autorisee est presente
            if platform == "windows":
                for allowed in self.allowlist:
                    if allowed in command:
                        return True, None
                return False, "Command not in allowlist"
            else:
                # Pour Linux, verification stricte du debut
                for allowed in self.allowlist:
                    if command.startswith(allowed):
                        return True, None
                return False, "Command not in allowlist"
        
        base_commands = (
            self.ALLOWED_COMMANDS_LINUX if platform == "linux" 
            else self.ALLOWED_COMMANDS_WINDOWS
        )
        
        cmd_start = command.split()[0] if command.split() else ""
        for allowed in base_commands:
            if cmd_start == allowed or command.startswith(allowed):
                return True, None
        
        return False, f"Command '{cmd_start}' not in default allowed commands"
    
    def validate(self, command: str, platform: str = "linux") -> tuple[bool, Optional[str]]:
        is_dangerous, danger_msg = self.is_dangerous(command)
        if is_dangerous:
            return False, danger_msg
        
        is_allowed, allow_msg = self.is_allowed(command, platform)
        if not is_allowed:
            return False, allow_msg
        
        return True, None
