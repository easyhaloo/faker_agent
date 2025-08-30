"""
LLM adapters for the Faker Agent.

This package provides adapters for various LLM providers,
with a focus on LiteLLM for compatibility with multiple APIs.
"""
from backend.core.infrastructure.llm.litellm_client import LiteLLMClient, litellm_client
from backend.core.infrastructure.llm.litellm_custom import CustomChatLiteLLM, custom_litellm_client
from backend.core.infrastructure.llm.factory import LLMFactory, llm_factory

__all__ = [
    "LiteLLMClient",
    "litellm_client",
    "CustomChatLiteLLM",
    "custom_litellm_client",
    "LLMFactory",
    "llm_factory",
]