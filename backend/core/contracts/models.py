"""
Model-related contracts for the Faker Agent system.
"""
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from backend.core.contracts.base import Message


class ModelRequest(BaseModel):
    """Request to an LLM."""
    
    messages: List[Message] = Field(..., description="Messages to send to the model")
    model: str = Field(..., description="Name of the model to use")
    temperature: float = Field(0.7, description="Temperature for generation")
    max_tokens: Optional[int] = Field(None, description="Maximum number of tokens to generate")
    tools: List[Dict[str, Any]] = Field(default_factory=list, description="Tools available to the model")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class ModelResponse(BaseModel):
    """Response from an LLM."""
    
    message: Message = Field(..., description="Response message from the model")
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list, description="Tool calls made by the model")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token usage information")
    model: str = Field(..., description="Name of the model that generated the response")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")