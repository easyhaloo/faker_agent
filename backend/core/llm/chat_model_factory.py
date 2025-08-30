"""
Chat model factory for creating different configurations of LLM chat models.

This module provides factory functions for creating chat models with different
configurations, making it easy to use the same model type with different settings.
"""
from typing import Dict, Optional, Union

from langchain_core.language_models.chat_models import BaseChatModel

from backend.config.settings import settings
from backend.core.llm.litellm_chat_model import LiteLLMChatModel


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
    Get a configured chat model instance.
    
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
    
    # Create and return the chat model
    return LiteLLMChatModel(
        model_name=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        streaming=streaming,
        api_key=api_key,
        api_base=api_base,
        **kwargs
    )


def get_planner_model() -> BaseChatModel:
    """
    Get a chat model configured for planning tasks.
    
    Planning tasks typically need lower temperature for more deterministic results.
    
    Returns:
        A BaseChatModel configured for planning
    """
    return get_chat_model(temperature=0.0)


def get_executor_model() -> BaseChatModel:
    """
    Get a chat model configured for executor tasks.
    
    Executor tasks need to follow instructions precisely.
    
    Returns:
        A BaseChatModel configured for executor tasks
    """
    return get_chat_model(temperature=0.2)


def get_assembler_model() -> BaseChatModel:
    """
    Get a chat model configured for assembler tasks.
    
    Assembler tasks need to reason about tool usage.
    
    Returns:
        A BaseChatModel configured for assembler tasks
    """
    return get_chat_model(temperature=0.0, max_tokens=1500)


# Default model instance
default_chat_model = get_chat_model()