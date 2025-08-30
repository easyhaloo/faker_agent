"""
Factory for creating LLM clients.

This module provides a factory for creating LLM clients
based on configuration, abstracting away the implementation details.
"""
import logging
from typing import Any, Dict, Optional, Type, Union

from langchain_core.language_models import BaseChatModel

from backend.core.contracts.base import LLMPort
from backend.core.infrastructure.llm.litellm_client import LiteLLMClient, litellm_client
from backend.core.infrastructure.llm.litellm_custom import CustomChatLiteLLM, custom_litellm_client
from backend.core.infrastructure.llm.llm_port_impl import LiteLLMAdapter, default_llm_adapter, streaming_llm_adapter

# Configure logger
logger = logging.getLogger(__name__)


class LLMFactory:
    """
    Factory for creating LLM clients.
    
    This class provides methods for creating and configuring
    LLM clients based on the provided settings.
    """
    
    @staticmethod
    def create_litellm_client(
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        streaming: bool = False,
    ) -> LiteLLMClient:
        """
        Create a LiteLLM client.
        
        Args:
            model: Model name
            api_key: API key
            base_url: Base URL for custom endpoints
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Configured LiteLLM client
        """
        return LiteLLMClient(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            streaming=streaming
        )
    
    @staticmethod
    def create_custom_litellm(
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> CustomChatLiteLLM:
        """
        Create a custom LiteLLM client.
        
        Args:
            model: Model name
            api_key: API key
            base_url: Base URL for custom endpoints
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            
        Returns:
            Configured custom LiteLLM client
        """
        return CustomChatLiteLLM(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    @staticmethod
    def get_default_client() -> LiteLLMClient:
        """
        Get the default LiteLLM client.
        
        Returns:
            Default LiteLLM client
        """
        return litellm_client
        
    @staticmethod
    def create_streaming_client(
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
    ) -> LiteLLMClient:
        """
        Create a streaming LiteLLM client.
        
        Args:
            model: Model name
            api_key: API key
            base_url: Base URL for custom endpoints
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            
        Returns:
            Configured streaming LiteLLM client
        """
        return LiteLLMClient(
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            streaming=True
        )
    
    @staticmethod
    def get_default_custom_client() -> CustomChatLiteLLM:
        """
        Get the default custom LiteLLM client.
        
        Returns:
            Default custom LiteLLM client
        """
        return custom_litellm_client


    @staticmethod
    def create_llm_adapter(
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        streaming: bool = False,
    ) -> LiteLLMAdapter:
        """
        Create a LiteLLM adapter implementing the LLMPort interface.
        
        Args:
            model: Model name
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            streaming: Whether to enable streaming
            
        Returns:
            Configured LiteLLM adapter
        """
        return LiteLLMAdapter(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout,
            streaming=streaming
        )
        
    @staticmethod
    def get_default_adapter() -> LiteLLMAdapter:
        """
        Get the default LiteLLM adapter.
        
        Returns:
            Default LiteLLM adapter
        """
        return default_llm_adapter
        
    @staticmethod
    def get_streaming_adapter() -> LiteLLMAdapter:
        """
        Get the streaming LiteLLM adapter.
        
        Returns:
            Streaming LiteLLM adapter
        """
        return streaming_llm_adapter


# Singleton factory instance
llm_factory = LLMFactory()