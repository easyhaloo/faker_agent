"""
LLM infrastructure module for the Faker Agent backend.

This package provides LLM integration components including:
- LiteLLM client factory
- LLM adapters
- Chat model utilities
"""
from backend.core.infrastructure.llm.litellm_client import LiteLLMClient, litellm_client
from backend.core.infrastructure.llm.litellm_custom import CustomChatLiteLLM, custom_litellm_client
from backend.core.infrastructure.llm.factory import LLMFactory, llm_factory
from backend.core.infrastructure.llm.llm_port_impl import LiteLLMAdapter, default_llm_adapter, streaming_llm_adapter
from backend.core.infrastructure.llm.chat_model import get_chat_model, default_chat_model

__all__ = [
    "LiteLLMClient",
    "litellm_client",
    "CustomChatLiteLLM",
    "custom_litellm_client",
    "LLMFactory",
    "llm_factory",
    "LiteLLMAdapter",
    "default_llm_adapter",
    "streaming_llm_adapter",
    "get_chat_model",
    "default_chat_model",
]