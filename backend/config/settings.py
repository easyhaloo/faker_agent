"""
Application settings module.
"""
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Logs directory
LOGS_DIR = BASE_DIR.parent / "logs"


class Settings(BaseSettings):
    """Application settings."""
    
    # Application settings
    APP_NAME: str = "Faker Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = str(LOGS_DIR / "application.log")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # API settings
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://0.0.0.0:5173",
        "http://0.0.0.0:5174"
    ]
    
    # LiteLLM settings
    LITELLM_API_KEY: str = Field("", env="LITELLM_API_KEY")
    GEMINI_API_KEY: str = Field("", env="GEMINI_API_KEY")
    GITHUB_API_BASE: str = Field("", env="GITHUB_API_BASE")
    GITHUB_API_KEY: str = Field("", env="GITHUB_API_KEY")
    # Default to GitHub Models provider to avoid OpenAI Assistants v2 paths
    LITELLM_MODEL: str = "github/gpt-4o-mini"  # Default model with provider prefix
    LITELLM_BASE_URL: str = Field("", env="LITELLM_BASE_URL")  # Custom endpoint URL

    LITELLM_TEMPERATURE: float = 0.7
    LITELLM_MAX_TOKENS: int = 800
    LITELLM_TIMEOUT: float = 60.0  # Request timeout in seconds
    
    # Weather API (placeholder for demo)
    WEATHER_API_KEY: str = Field("", env="WEATHER_API_KEY")
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"), 
        env_file_encoding="utf-8", 
        case_sensitive=True
    )


# Create settings instance
settings = Settings()