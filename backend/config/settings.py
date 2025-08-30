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
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]
    
    # LiteLLM settings
    LITELLM_API_KEY: str = Field("", env="LITELLM_API_KEY")
    LITELLM_MODEL: str = "gpt-3.5-turbo"  # Default model
    LITELLM_BASE_URL: str = Field("", env="LITELLM_BASE_URL")  # Custom endpoint URL
    LITELLM_TEMPERATURE: float = 0.7
    LITELLM_MAX_TOKENS: int = 800
    
    # Weather API (placeholder for demo)
    WEATHER_API_KEY: str = Field("", env="WEATHER_API_KEY")
    WEATHER_API_URL: str = "https://api.openweathermap.org/data/2.5"
    
    # Model configuration
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True
    )


# Create settings instance
settings = Settings()