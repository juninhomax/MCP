from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "MCP Brain"
    debug: bool = False
    
    brain_host: str = "0.0.0.0"
    brain_port: int = 8000
    
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5-coder:14b"
    llm_api_base: str = "http://localhost:11434"
    llm_api_key: Optional[str] = None
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "mcp_brain"
    postgres_user: str = "mcp"
    postgres_password: str = "mcp_password"
    
    enable_audit: bool = True
    enable_dry_run: bool = True
    enable_kill_switch: bool = False
    
    max_reasoning_steps: int = 10
    request_timeout: int = 300
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
