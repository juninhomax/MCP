from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "MCP Slave Windows"
    slave_id: str = "windows-slave-01"
    slave_type: str = "windows"
    slave_port: int = 8002
    brain_url: str = "http://localhost:8000"
    
    host: str = "0.0.0.0"
    port: int = 8002
    
    brain_endpoint: str = "http://localhost:8000"
    auth_token: Optional[str] = None
    
    enable_audit: bool = True
    max_execution_time: int = 300
    
    # Liste elargie des commandes autorisees (prefixes)
    allowed_commands: list[str] = [
        "dir", "type", "findstr", "Get-Process", "Get-Service",
        "Get-EventLog", "Test-Path", "Get-Content", "Select-String",
        "Get-ChildItem", "Get-Item", "Get-Location", "Format-Table",
        "Format-List", "Select-Object", "Sort-Object", "Where-Object",
        "Measure-Object", "Group-Object"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
