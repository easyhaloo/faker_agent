"""
LiteLLM chat model for LangChain integration.

This module provides a custom LangChain chat model implementation
that uses LiteLLM as the backend. This allows for direct integration
with LangChain's agent framework and other components.
"""
import asyncio
import logging
from typing import Any, Dict, List, Mapping, Optional, Union

import litellm
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    ChatMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage
)
from langchain_core.outputs import ChatGeneration, ChatResult

from backend.config.settings import settings
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)


class LiteLLMChatModel(BaseChatModel):
    """
    Custom LangChain chat model implementation using LiteLLM.
    
    This class implements the LangChain BaseChatModel interface, allowing it
    to be used with LangChain's agents, chains, and other components.
    """
    
    model_name: str = settings.LITELLM_MODEL
    temperature: float = settings.LITELLM_TEMPERATURE
    max_tokens: int = settings.LITELLM_MAX_TOKENS
    api_key: Optional[str] = settings.LITELLM_API_KEY
    api_base: Optional[str] = settings.LITELLM_BASE_URL
    streaming: bool = False
    
    class Config:
        """Configuration for this pydantic object."""
        arbitrary_types_allowed = True
    
    @property
    def _llm_type(self) -> str:
        """Return type of LLM."""
        return "litellm-chat"
    
    def _convert_message_to_litellm_format(self, message: BaseMessage) -> Dict[str, Any]:
        """Convert LangChain message to LiteLLM format."""
        if isinstance(message, SystemMessage):
            return {"role": "system", "content": message.content}
        elif isinstance(message, HumanMessage):
            return {"role": "user", "content": message.content}
        elif isinstance(message, AIMessage):
            msg = {"role": "assistant", "content": message.content}
            # Add tool calls if present
            if hasattr(message, "tool_calls") and message.tool_calls:
                msg["tool_calls"] = message.tool_calls
            return msg
        elif isinstance(message, ToolMessage):
            return {
                "role": "tool",
                "content": message.content,
                "name": message.name,
                "tool_call_id": message.tool_call_id
            }
        elif isinstance(message, ChatMessage):
            return {"role": message.role, "content": message.content}
        else:
            # Default for unknown message types
            return {"role": "user", "content": str(message.content)}

    def _convert_messages_to_litellm_format(self, messages: List[BaseMessage]) -> List[Dict[str, Any]]:
        """Convert a list of LangChain messages to LiteLLM format."""
        return [self._convert_message_to_litellm_format(message) for message in messages]
    
    def _create_generation_from_response(
        self, response: Dict[str, Any]
    ) -> ChatGeneration:
        """Create a LangChain ChatGeneration from a LiteLLM response."""
        message_content = response.get("content", "")
        
        # Check for tool calls in the response
        tool_calls = None
        if "tool_calls" in response:
            tool_calls = response["tool_calls"]
        
        # Create an AIMessage with the response content and any tool calls
        message = AIMessage(content=message_content, tool_calls=tool_calls)
        
        return ChatGeneration(message=message)
    
    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a chat response using LiteLLM."""
        # Convert messages to LiteLLM format
        litellm_messages = self._convert_messages_to_litellm_format(messages)
        
        # Set up parameters for the API call
        params = {
            "model": self.model_name,
            "messages": litellm_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        # Add stop sequences if provided
        if stop:
            params["stop"] = stop
        
        # Add any additional parameters
        params.update(kwargs)
        
        try:
            # Call LiteLLM
            response = litellm.completion(**params)
            
            # Extract the assistant's message from the response
            assistant_message = response.choices[0].message
            
            # Create a ChatGeneration object from the response
            generation = self._create_generation_from_response(assistant_message)
            
            # Return the ChatResult with the generation
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Error in LiteLLMChatModel._generate: {e}")
            # Create a minimal error response
            error_message = AIMessage(content=f"Error generating response: {str(e)}")
            return ChatResult(generations=[ChatGeneration(message=error_message)])
    
    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a chat response asynchronously using LiteLLM."""
        # Convert messages to LiteLLM format
        litellm_messages = self._convert_messages_to_litellm_format(messages)
        
        # Set up parameters for the API call
        params = {
            "model": self.model_name,
            "messages": litellm_messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        
        # Add stop sequences if provided
        if stop:
            params["stop"] = stop
        
        # Add any additional parameters
        params.update(kwargs)
        
        try:
            # Call LiteLLM asynchronously
            response = await litellm.acompletion(**params)
            
            # Extract the assistant's message from the response
            assistant_message = response.choices[0].message
            
            # Create a ChatGeneration object from the response
            generation = self._create_generation_from_response(assistant_message)
            
            # Return the ChatResult with the generation
            return ChatResult(generations=[generation])
            
        except Exception as e:
            logger.error(f"Error in LiteLLMChatModel._agenerate: {e}")
            # Create a minimal error response
            error_message = AIMessage(content=f"Error generating response: {str(e)}")
            return ChatResult(generations=[ChatGeneration(message=error_message)])


# Create a global instance with default settings
default_chat_model = LiteLLMChatModel()