from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "MCP Slave Linux"
    slave_id: str = "linux-slave-01"
    slave_type: str = "linux"
    
    host: str = "0.0.0.0"
    port: int = 8001
    
    brain_endpoint: str = "http://localhost:8000"
    auth_token: Optional[str] = None
    
    enable_audit: bool = True
    max_execution_time: int = 300
    
    allowed_commands: list[str] = [
        "ls", "cat", "grep", "find", "ps", "top", "df", "du",
        "git", "docker", "kubectl", "systemctl status",
        "journalctl", "tail", "head", "wc", "awk", "sed"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
