"""
Custom LiteLLM implementation for the Faker Agent.

This module provides a custom implementation of the LiteLLM client,
with additional features like event callbacks and streaming support.
"""
import logging
import asyncio
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Union

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from litellm import ModelResponse, acompletion

from backend.config.settings import settings
from backend.core.contracts.base import Message
from backend.core.contracts.models import ModelRequest, ModelResponse as FakerModelResponse
from backend.core.errors import ModelError

# Configure logger
logger = logging.getLogger(__name__)


class CustomChatLiteLLM(BaseChatModel):
    """
    Custom LiteLLM chat model implementation.
    
    This class extends BaseChatModel to provide a custom implementation
    with additional features like event callbacks and token streaming.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Initialize the custom LiteLLM model.
        
        Args:
            model: Model name (defaults to settings)
            api_key: API key (defaults to settings)
            base_url: Base URL for custom endpoints (defaults to settings)
            temperature: Temperature for generation (defaults to settings)
            max_tokens: Maximum tokens to generate (defaults to settings)
        """
        super().__init__()
        
        # Use settings as defaults
        self._model_name = model or settings.LITELLM_MODEL
        self._api_key = api_key or settings.LITELLM_API_KEY
        self._base_url = base_url or settings.LITELLM_BASE_URL
        self._temperature = temperature or settings.LITELLM_TEMPERATURE
        self._max_tokens = max_tokens or settings.LITELLM_MAX_TOKENS
        
        # Default to not streaming
        self._streaming = False
        
        # Build the model kwargs
        self._model_kwargs = {
            "temperature": self._temperature,
        }
        
        if self._max_tokens:
            self._model_kwargs["max_tokens"] = self._max_tokens
        
        # Log initialization (without sensitive info)
        logger.info(f"Initialized CustomChatLiteLLM with model={self._model_name}")
    
    def _convert_message_to_litellm(self, message: BaseMessage) -> Dict[str, str]:
        """
        Convert LangChain message to LiteLLM format.
        
        Args:
            message: LangChain message
            
        Returns:
            Message in LiteLLM format
        """
        role = "user"
        if isinstance(message, SystemMessage):
            role = "system"
        elif isinstance(message, AIMessage):
            role = "assistant"
        
        return {
            "role": role,
            "content": message.content
        }
    
    def _convert_messages_to_litellm(self, messages: List[BaseMessage]) -> List[Dict[str, str]]:
        """
        Convert LangChain messages to LiteLLM format.
        
        Args:
            messages: List of LangChain messages
            
        Returns:
            List of messages in LiteLLM format
        """
        return [self._convert_message_to_litellm(msg) for msg in messages]
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackHandler] = None,
        **kwargs
    ) -> ChatResult:
        """
        Generate a response from the LLM (async).
        
        Args:
            messages: List of messages
            stop: Optional stop sequences
            run_manager: Optional callback handler
            **kwargs: Additional arguments
            
        Returns:
            LangChain ChatResult
            
        Raises:
            ModelError: If generation fails
        """
        try:
            # Convert messages to LiteLLM format
            litellm_messages = self._convert_messages_to_litellm(messages)
            
            # Merge additional kwargs with model_kwargs
            model_kwargs = {**self._model_kwargs, **kwargs}
            
            # Add stop sequences if provided
            if stop:
                model_kwargs["stop"] = stop
            
            # Set up streaming callbacks if needed
            stream_options = {}
            if self._streaming and run_manager:
                stream_options["stream"] = True
            
            # Build completion parameters
            completion_kwargs = {
                "model": self._model_name,
                "messages": litellm_messages,
                **model_kwargs,
                **stream_options
            }
            
            # Add API key if available
            if self._api_key:
                completion_kwargs["api_key"] = self._api_key
            
            # Add custom base URL if available
            if self._base_url:
                completion_kwargs["api_base"] = self._base_url
            
            # Generate the response
            if self._streaming and run_manager:
                # Handle streaming
                content = ""
                async for chunk in self._astream_with_litellm(**completion_kwargs):
                    # Ensure the chunk has delta content
                    if (
                        hasattr(chunk, "choices") and
                        len(chunk.choices) > 0 and
                        hasattr(chunk.choices[0], "delta") and
                        hasattr(chunk.choices[0].delta, "content") and
                        chunk.choices[0].delta.content
                    ):
                        content_chunk = chunk.choices[0].delta.content
                        content += content_chunk
                        # Send to callback
                        await run_manager.on_llm_new_token(content_chunk)
                
                # Create a chat generation from the accumulated content
                generation = ChatGeneration(
                    message=AIMessage(content=content),
                    generation_info={"finish_reason": "stop"}
                )
                
                # Create and return the chat result
                return ChatResult(generations=[generation])
            else:
                # Non-streaming mode
                response = await acompletion(**completion_kwargs)
                
                # Extract the content
                content = ""
                if (
                    hasattr(response, "choices") and
                    len(response.choices) > 0 and
                    hasattr(response.choices[0], "message") and
                    hasattr(response.choices[0].message, "content")
                ):
                    content = response.choices[0].message.content
                
                # Create a chat generation
                generation = ChatGeneration(
                    message=AIMessage(content=content),
                    generation_info={"finish_reason": "stop"}
                )
                
                # Create and return the chat result
                return ChatResult(generations=[generation])
                
        except Exception as e:
            logger.error(f"Error generating response from {self._model_name}: {e}")
            raise ModelError(self._model_name, str(e))
    
    async def _astream_with_litellm(self, **kwargs) -> AsyncIterator[ModelResponse]:
        """
        Stream response chunks from LiteLLM.
        
        Args:
            **kwargs: LiteLLM completion parameters
            
        Yields:
            Response chunks
        """
        # Enable streaming
        kwargs["stream"] = True
        
        # Call LiteLLM completion with streaming
        async for chunk in acompletion(**kwargs):
            yield chunk
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager = None,
        **kwargs
    ) -> ChatResult:
        """
        Generate a response from the LLM (sync).
        This is required by BaseChatModel but we only support async usage.
        
        Args:
            messages: List of messages
            stop: Optional stop sequences
            run_manager: Optional callback handler
            **kwargs: Additional arguments
            
        Returns:
            LangChain ChatResult
            
        Raises:
            NotImplementedError: This method is not implemented
        """
        raise NotImplementedError("This class only supports async usage. Use _agenerate instead.")
    
    @property
    def _llm_type(self) -> str:
        """
        Get the LLM type.
        
        Returns:
            LLM type string
        """
        return "custom_litellm"


# Create global client instance
custom_litellm_client = CustomChatLiteLLM()