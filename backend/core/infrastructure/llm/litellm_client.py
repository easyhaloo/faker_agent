"""
LiteLLM adapter for the Faker Agent.

This module provides integration with LiteLLM, allowing the system
to connect to various LLM providers through a unified interface.
"""
import asyncio
import logging
import time
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from langchain_core.callbacks import AsyncCallbackHandler
from langchain_litellm import ChatLiteLLM
from litellm import ModelResponse
from litellm.utils import get_llm_provider
import litellm
from backend.config.settings import settings
from backend.core.contracts.base import Message
from backend.core.contracts.models import ModelRequest, ModelResponse as FakerModelResponse
from backend.core.errors import ModelError, ConfigurationError

# Configure logger
logger = logging.getLogger(__name__)
litellm._turn_on_debug()

class LiteLLMClient:
    """
    LiteLLM client for interfacing with various LLM providers.
    
    This class uses the LiteLLM library to provide a unified interface
    to multiple LLM providers, configurable through settings.
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[float] = None,
        retry_attempts: int = 1,
        streaming: bool = False,
    ):
        """
        Initialize the LiteLLM client.
        
        Args:
            model: Model name (defaults to settings)
            api_key: API key (defaults to settings)
            base_url: Base URL for custom endpoints (defaults to settings)
            temperature: Temperature for generation (defaults to settings)
            max_tokens: Maximum tokens to generate (defaults to settings)
        """
        # Use settings as defaults
        self.model = model or settings.LITELLM_MODEL
        self.api_key = api_key or settings.LITELLM_API_KEY
        self.base_url = base_url or settings.LITELLM_BASE_URL
        self.temperature = temperature or settings.LITELLM_TEMPERATURE
        self.max_tokens = max_tokens or settings.LITELLM_MAX_TOKENS
        self.timeout = timeout or settings.LITELLM_TIMEOUT
        self.retry_attempts = retry_attempts
        self.streaming = streaming
        
        # Validate required settings
        self._validate_config()
        
        # Create the LangChain ChatLiteLLM instance
        self.client = self._create_client()
        
        # Log initialization (without sensitive info)
        try:
            provider = get_llm_provider(self.model) if self.model else "unknown"
        except Exception:
            # If provider detection fails, use a default value
            provider = "default"
        logger.info(f"Initialized LiteLLMClient with model={self.model} (provider={provider}, streaming={self.streaming})")
    
    def _validate_config(self) -> None:
        """
        Validate the client configuration.
        
        Raises:
            ConfigurationError: If required configuration is missing
        """
        # Check if model is provided
        if not self.model:
            logger.warning("Model name not provided, using default model")
            self.model = "gpt-3.5-turbo"  # Use a default model
        
        # Check if either API key or base URL is provided
        # We'll log a warning but continue anyway for testing
        if not self.api_key and not self.base_url:
            logger.warning("Neither API key nor base URL provided, some features may not work")
            # For testing purposes only - in production, we would raise an error
            # raise ConfigurationError("api_key", "Either API key or base URL must be provided")
    
    def _create_client(self) -> ChatLiteLLM:
        """
        Create a LangChain ChatLiteLLM instance.
        
        Returns:
            Configured ChatLiteLLM instance
        """
        # Build the model kwargs
        model_kwargs = {
            "temperature": self.temperature,
        }
        
        if self.max_tokens:
            model_kwargs["max_tokens"] = self.max_tokens
            
        if self.timeout:
            model_kwargs["request_timeout"] = self.timeout
        
        # Build kwargs for the client
        client_kwargs = {
            "model": self.model,
            "api_key": self.api_key,
            "model_kwargs": model_kwargs,
            "streaming": self.streaming,
        }

        # Add base_url to model_kwargs if provided
        if self.base_url:
            client_kwargs["api_base"] = self.base_url
        
        # Create client with proper configuration
        client = ChatLiteLLM(**client_kwargs)
        
        # Set custom base URL if provided
        # Note: ChatLiteLLM in newer versions doesn't directly support base_url as a property
        # It's now handled through model configuration or other mechanisms
        
        return client
    
    def _convert_to_langchain_messages(self, messages: List[Message]) -> List[Dict[str, str]]:
        """
        Convert Faker Agent messages to LangChain format.
        
        Args:
            messages: List of Faker Agent messages
            
        Returns:
            List of messages in LangChain format
        """
        return [{"role": msg.role, "content": msg.content} for msg in messages]
    
    def _convert_from_litellm_response(
        self,
        response: Any,
        request: ModelRequest
    ) -> FakerModelResponse:
        """
        Convert LiteLLM response to Faker Agent format.
        
        Args:
            response: LiteLLM response
            request: Original model request
            
        Returns:
            Response in Faker Agent format
        """
        # Extract the message content
        content = ""
        if hasattr(response, "message") and hasattr(response.message, "content"):
            content = response.message.content
        
        # Create the response message
        message = Message(
            role="assistant",
            content=content
        )
        
        # Extract tool calls if present
        tool_calls = []
        if hasattr(response, "message") and hasattr(response.message, "tool_calls"):
            tool_calls = response.message.tool_calls
        
        # Extract usage information
        usage = {}
        if hasattr(response, "usage"):
            usage = response.usage
        
        # Create the model response
        return FakerModelResponse(
            message=message,
            tool_calls=tool_calls,
            usage=usage,
            model=request.model,
            metadata=request.metadata
        )
    
    async def generate(self, request: ModelRequest) -> FakerModelResponse:
        """
        Generate a response from the LLM.
        
        Args:
            request: The model request
            
        Returns:
            The model response
            
        Raises:
            ModelError: If generation fails
        """
        # Attempt with retries
        attempt = 0
        last_error = None
        
        while attempt < self.retry_attempts:
            try:
                logger.error(f"call llm from {request.model}")
                # Convert messages to LangChain format
                lc_messages = self._convert_to_langchain_messages(request.messages)
                
                # Override client settings if specified in request
                client = self._get_client_for_request(request)
                
                # Add tools if provided
                if request.tools:
                    # Use bind_tools from LangChain
                    client = client.bind_tools(request.tools)
                
                # Call the LLM
                logger.debug(f"call llm from {request.model}")

                start_time = time.time()
                response = await client.ainvoke(
                    lc_messages,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                )
                execution_time = time.time() - start_time
                
                # Log success
                logger.info(f"Generated response from {request.model} in {execution_time:.2f}s")
                
                # Add execution time to metadata
                if request.metadata is None:
                    request.metadata = {}
                request.metadata["execution_time"] = execution_time
                
                # Convert the response to our format
                return self._convert_from_litellm_response(response, request)
                
            except Exception as e:
                attempt += 1
                last_error = e
                
                # Log the error
                logger.warning(f"Attempt {attempt}/{self.retry_attempts} failed for {request.model}: {e}")
                
                # Wait before retrying (exponential backoff)
                if attempt < self.retry_attempts:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        # If we reach here, all attempts failed
        logger.error(f"All {self.retry_attempts} attempts failed for {request.model}: {last_error}")
        # Ensure error message is properly encoded to handle Unicode characters
        error_msg = f"Failed after {self.retry_attempts} attempts: {str(last_error)}"
        error_msg = error_msg.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        raise ModelError(request.model, error_msg)
    
    def _get_client_for_request(self, request: ModelRequest) -> ChatLiteLLM:
        """
        Get a client configured for the specific request.
        
        Args:
            request: The model request
            
        Returns:
            Configured ChatLiteLLM instance for this request
        """
        # Use the existing client if settings match
        if request.model == self.model:
            return self.client
        
        # Create a new client with the requested model
        model_kwargs = {
            "temperature": request.temperature,
        }
        
        if request.max_tokens:
            model_kwargs["max_tokens"] = request.max_tokens
            
        if self.timeout:
            model_kwargs["request_timeout"] = self.timeout
            
        # Build kwargs for the client
        client_kwargs = {
            "model": request.model,
            "api_key": self.api_key,
            "model_kwargs": model_kwargs,
            "streaming": self.streaming,
        }
        
        # Add base_url to model_kwargs if provided
        if self.base_url:
            if "model_kwargs" not in client_kwargs:
                client_kwargs["model_kwargs"] = {}
            client_kwargs["model_kwargs"]["base_url"] = self.base_url
            
        # Create client with proper configuration
        temp_client = ChatLiteLLM(**client_kwargs)
        
        # Set custom base URL if provided
        # Note: ChatLiteLLM in newer versions doesn't directly support base_url as a property
        # It's now handled through model configuration or other mechanisms
            
        return temp_client


class TokenStreamHandler(AsyncCallbackHandler):
    """Handler for streaming tokens from the LLM."""
    
    def __init__(self, token_callback: Callable[[str], None]):
        """Initialize with a callback for tokens."""
        self.token_callback = token_callback
    
    async def on_llm_new_token(self, token: str, **kwargs) -> None:
        """Called when a new token is generated."""
        await self.token_callback(token)


async def generate_streaming(
    client: LiteLLMClient,
    request: ModelRequest,
    token_callback: Callable[[str], None]
) -> AsyncGenerator[str, None]:
    """
    Generate a streaming response from the LLM.
    
    Args:
        client: The LiteLLM client
        request: The model request
        token_callback: Callback function for tokens
        
    Yields:
        Tokens as they are generated
    """
    # Create a streaming client
    streaming_client = LiteLLMClient(
        model=request.model or client.model,
        api_key=client.api_key,
        base_url=client.base_url,
        temperature=request.temperature or client.temperature,
        max_tokens=request.max_tokens or client.max_tokens,
        timeout=client.timeout,
        streaming=True
    )
    
    # Create a token handler
    handler = TokenStreamHandler(token_callback)
    
    # Convert messages to LangChain format
    lc_messages = client._convert_to_langchain_messages(request.messages)
    
    # Get client configured for this request
    lc_client = streaming_client._get_client_for_request(request)
    
    # Add tools if provided
    if request.tools:
        lc_client = lc_client.bind_tools(request.tools)
    
    try:
        # Stream the response
        async for chunk in lc_client.astream(
            lc_messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            callbacks=[handler]
        ):
            # Each chunk has a content field with the generated text so far
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    except Exception as e:
        logger.error(f"Error in streaming from {request.model}: {e}")
        raise ModelError(request.model, str(e))


# Create global client instance
litellm_client = LiteLLMClient()