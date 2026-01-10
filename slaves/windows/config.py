from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "MCP Slave Windows"
    slave_id: str = "windows-slave-01"
    slave_type: str = "windows"
    
    host: str = "0.0.0.0"
    port: int = 8002
    
    brain_endpoint: str = "http://localhost:8000"
    auth_token: Optional[str] = None
    
    enable_audit: bool = True
    max_execution_time: int = 300
    
    allowed_commands: list[str] = [
        "dir", "type", "findstr", "Get-Process", "Get-Service",
        "Get-EventLog", "Test-Path", "Get-Content", "Select-String",
        "Get-ChildItem", "Get-Item", "Get-Location"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
