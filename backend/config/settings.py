"""
Settings module for the Faker Agent backend.

This module defines configuration settings using Pydantic Settings,
allowing configuration through environment variables with defaults.
"""
import os
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings."""
    
    # Server settings
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = Field(default="%(asctime)s - %(name)s - %(levelname)s - %(message)s", env="LOG_FORMAT")
    
    # LiteLLM settings
    LITELLM_MODEL: str = Field(default="gpt-3.5-turbo", env="LITELLM_MODEL")
    LITELLM_API_KEY: Optional[str] = Field(default=None, env="LITELLM_API_KEY")
    LITELLM_BASE_URL: Optional[str] = Field(default=None, env="LITELLM_BASE_URL")
    LITELLM_TEMPERATURE: float = Field(default=0.7, env="LITELLM_TEMPERATURE")
    LITELLM_MAX_TOKENS: Optional[int] = Field(default=None, env="LITELLM_MAX_TOKENS")
    LITELLM_TIMEOUT: float = Field(default=30.0, env="LITELLM_TIMEOUT")
    
    # Additional API keys
    GITHUB_API_KEY: Optional[str] = Field(default=None, env="GITHUB_API_KEY")
    GITHUB_API_BASE: Optional[str] = Field(default=None, env="GITHUB_API_BASE")
    GEMINI_API_KEY: Optional[str] = Field(default=None, env="GEMINI_API_KEY")
    WEATHER_API_KEY: Optional[str] = Field(default=None, env="WEATHER_API_KEY")
    
    # LiteLLM fallback configuration - use GitHub settings if LiteLLM settings are not provided
    @property
    def effective_litellm_api_key(self) -> Optional[str]:
        """Get effective API key for LiteLLM (fallback to GITHUB_API_KEY if LITELLM_API_KEY not set)"""
        return self.LITELLM_API_KEY or self.GITHUB_API_KEY
    
    @property
    def effective_litellm_base_url(self) -> Optional[str]:
        """Get effective base URL for LiteLLM (fallback to GITHUB_API_BASE if LITELLM_BASE_URL not set)"""
        return self.LITELLM_BASE_URL or self.GITHUB_API_BASE
    
    # Memory settings
    MEMORY_CLEANUP_INTERVAL: int = Field(default=3600, env="MEMORY_CLEANUP_INTERVAL")  # 1 hour
    
    class Config:
        """Pydantic config."""
        # Use path relative to this settings file
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        env_file_encoding = "utf-8"


# Create settings instance
settings = Settings()