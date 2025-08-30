"""
LLMPort implementation for the Faker Agent.

This module provides an implementation of the LLMPort interface
using LiteLLM as the underlying provider.
"""
import asyncio
import logging
from typing import Any, AsyncGenerator, Callable, List, Optional

from backend.core.contracts.base import LLMPort, Message
from backend.core.contracts.models import ModelRequest, ModelResponse
from backend.core.infrastructure.llm.litellm_client import litellm_client, generate_streaming

# Configure logger
logger = logging.getLogger(__name__)


class LiteLLMAdapter(LLMPort):
    """
    LiteLLM adapter implementing the LLMPort interface.
    
    This class provides an implementation of the LLMPort interface
    using LiteLLM as the underlying provider. It supports both
    synchronous and streaming modes of operation.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        streaming: bool = False,
    ):
        """
        Initialize the LiteLLM adapter.
        
        Args:
            model: Model name (defaults to client default)
            temperature: Temperature for generation (defaults to client default)
            max_tokens: Maximum tokens to generate (defaults to client default)
        """
        self.model = model or litellm_client.model
        self.temperature = temperature or litellm_client.temperature
        self.max_tokens = max_tokens or litellm_client.max_tokens
        self.timeout = timeout
        self.streaming = streaming
        
        logger.info(f"Initialized LiteLLMAdapter with model={self.model}, streaming={self.streaming}")
    
    async def chat(self, messages: List[Message]) -> Message:
        """
        Send messages to the LLM and get a response.
        
        Args:
            messages: List of messages in the conversation
            
        Returns:
            Response message from the LLM
        """
        # Create the model request
        request = ModelRequest(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Generate the response
        response = await litellm_client.generate(request)
        
        # Return just the message
        return response.message
    
    async def generate(self, messages: List[Message], **kwargs) -> Any:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of messages representing the conversation
            **kwargs: Additional model parameters
            
        Returns:
            LLM response
        """
        # Override defaults with kwargs if provided
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        # Create the model request
        request = ModelRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=kwargs.get("tools")
        )
        
        # Generate the response
        return await litellm_client.generate(request)
    
    async def stream(self, messages: List[Message], **kwargs) -> AsyncGenerator[str, None]:
        """
        Stream a response from the LLM.
        
        Args:
            messages: List of messages representing the conversation
            **kwargs: Additional model parameters
            
        Returns:
            Async iterator of response chunks
        """
        # Override defaults with kwargs if provided
        model = kwargs.get("model", self.model)
        temperature = kwargs.get("temperature", self.temperature)
        max_tokens = kwargs.get("max_tokens", self.max_tokens)
        
        # Create the model request
        request = ModelRequest(
            messages=messages,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=kwargs.get("tools")
        )
        
        # Stream the response
        async def token_callback(token: str) -> None:
            # This is just a placeholder function if no callback is provided
            pass
        
        callback = kwargs.get("token_callback", token_callback)
        
        # Return the async generator directly
        return generate_streaming(litellm_client, request, callback)
    
    async def stream_chat(
        self, 
        messages: List[Message],
        token_callback: Callable[[str], None]
    ) -> Message:
        """
        Stream messages to the LLM and get tokens as they're generated.
        
        Args:
            messages: List of messages in the conversation
            token_callback: Callback function for each token
            
        Returns:
            Final response message from the LLM
        """
        # Create the model request
        request = ModelRequest(
            messages=messages,
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        # Full response content
        full_content = ""
        
        # Stream the response
        async for token in generate_streaming(litellm_client, request, token_callback):
            # Update the full content
            full_content = token
        
        # Create a message from the full content
        return Message(
            role="assistant",
            content=full_content
        )


# Create global adapter instances
default_llm_adapter = LiteLLMAdapter()
streaming_llm_adapter = LiteLLMAdapter(streaming=True)