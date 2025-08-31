"""
Chat model factory for LangChain integration.

This module provides factory functions for creating LangChain chat models
using the infrastructure LLM clients, maintaining compatibility with
code that expects LangChain interfaces.
"""
from typing import Dict, Optional, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_litellm import ChatLiteLLM

from backend.config.settings import settings
from backend.core.infrastructure.llm.factory import llm_factory
from backend.core.infrastructure.llm.llm_port_impl import LiteLLMAdapter


def get_chat_model(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    streaming: bool = False,
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    **kwargs
) -> BaseChatModel:
    """
    Get a configured LangChain chat model instance.
    
    Args:
        model_name: Name of the model to use (default: from settings)
        temperature: Temperature for generation (default: from settings)
        max_tokens: Maximum tokens to generate (default: from settings)
        streaming: Whether to enable streaming (default: False)
        api_key: API key to use (default: from settings)
        api_base: API base URL to use (default: from settings)
        **kwargs: Additional parameters to pass to the model
        
    Returns:
        A configured BaseChatModel instance
    """
    # Use settings as defaults if not specified
    model_name = model_name or settings.LITELLM_MODEL
    temperature = temperature if temperature is not None else settings.LITELLM_TEMPERATURE
    max_tokens = max_tokens if max_tokens is not None else settings.LITELLM_MAX_TOKENS
    api_key = api_key or settings.LITELLM_API_KEY
    api_base = api_base or settings.LITELLM_BASE_URL
    
    # Build the model kwargs
    model_kwargs = {
        "temperature": temperature,
    }
    
    if max_tokens:
        model_kwargs["max_tokens"] = max_tokens
        
    # Build kwargs for the client
    client_kwargs = {
        "model": model_name,
        "api_key": api_key,
        "model_kwargs": model_kwargs,
        "streaming": streaming,
    }
    
    # Add base_url to model_kwargs if provided
    if api_base:
        client_kwargs["api_base"] = api_base
    
    # Create client with proper configuration
    return ChatLiteLLM(**client_kwargs)


# Default model instance
default_chat_model = get_chat_model()