"""
LangChain integration module for the Faker Agent backend.

This package provides custom LangChain integrations, including:
- Custom LiteLLM chat model implementation
- Chat model factory for creating different configurations
- Agent utilities for working with LangChain agents
"""
from backend.core.llm.agent_utils import convert_to_langchain_tools, create_agent_executor
from backend.core.llm.chat_model_factory import (
    default_chat_model,
    get_assembler_model,
    get_chat_model,
    get_executor_model,
    get_planner_model,
)
from backend.core.llm.litellm_chat_model import LiteLLMChatModel

__all__ = [
    "LiteLLMChatModel",
    "default_chat_model",
    "get_chat_model",
    "get_planner_model",
    "get_executor_model",
    "get_assembler_model",
    "create_agent_executor",
    "convert_to_langchain_tools",
]