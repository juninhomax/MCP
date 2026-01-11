from abc import ABC, abstractmethod
from typing import Optional, Any, Dict
import json
import httpx
from brain.config import settings


class LLMResponse:
    def __init__(self, content: str, metrics: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metrics = metrics or {}
    
    def __str__(self):
        return self.content


class LLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> LLMResponse:
        pass


class OllamaProvider(LLMProvider):
    def __init__(self, base_url: str, model: str):
        self.base_url = base_url.rstrip('/')
        self.model = model
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        if json_mode:
            payload["format"] = "json"
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            # Extraire les metriques de performance d'Ollama
            metrics = {}
            if "eval_count" in result:
                metrics["tokens_generated"] = result.get("eval_count", 0)
            if "eval_duration" in result:
                # Convertir nanosecondes en secondes
                duration_sec = result.get("eval_duration", 0) / 1_000_000_000
                metrics["generation_time"] = duration_sec
                if metrics.get("tokens_generated", 0) > 0 and duration_sec > 0:
                    metrics["tokens_per_second"] = metrics["tokens_generated"] / duration_sec
            if "prompt_eval_count" in result:
                metrics["tokens_prompt"] = result.get("prompt_eval_count", 0)
            if "prompt_eval_duration" in result:
                metrics["prompt_time"] = result.get("prompt_eval_duration", 0) / 1_000_000_000
            
            # Temps total
            if "total_duration" in result:
                metrics["total_time"] = result.get("total_duration", 0) / 1_000_000_000
            
            return LLMResponse(
                content=result["message"]["content"],
                metrics=metrics
            )


class GLM4Provider(LLMProvider):
    def __init__(self, api_key: str, model: str = "glm-4"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://open.bigmodel.cn/api/paas/v4"
    
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        json_mode: bool = False
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            # GLM4 peut aussi retourner des metriques usage
            metrics = {}
            if "usage" in result:
                usage = result["usage"]
                metrics["tokens_prompt"] = usage.get("prompt_tokens", 0)
                metrics["tokens_generated"] = usage.get("completion_tokens", 0)
                metrics["tokens_total"] = usage.get("total_tokens", 0)
            
            return LLMResponse(
                content=result["choices"][0]["message"]["content"],
                metrics=metrics
            )


def get_llm_provider() -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaProvider(settings.llm_api_base, settings.llm_model)
    elif settings.llm_provider == "glm4":
        if not settings.llm_api_key:
            raise ValueError("GLM-4 requires API key")
        return GLM4Provider(settings.llm_api_key, settings.llm_model)
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
