import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class AISettings(BaseSettings):
    
    groq_api_key: str = ""
    ai_model: str = "qwen/qwen3-32b" 
    
    temperature: float = 0.3 
    max_tokens: int = 2048
    
    max_session_messages: int = 20 
    session_timeout_minutes: int = 30
    
    class Config:
        env_prefix = ""
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_ai_settings() -> AISettings:
    """Get cached AI settings"""
    return AISettings()
