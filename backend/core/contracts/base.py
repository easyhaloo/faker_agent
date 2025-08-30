"""
Base contracts for the Faker Agent.

This module provides base contract classes used throughout the system
for standardized data representation and exchange.
"""
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

# Configure logger
logger = logging.getLogger(__name__)


class Message(BaseModel):
    """
    Standardized message format for LLM interactions.
    
    This class provides a common message format that can be used
    across different LLM providers and communication protocols.
    """
    
    role: str
    content: str
    name: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "role": self.role,
            "content": self.content
        }
        
        if self.name:
            result["name"] = self.name
            
        if self.metadata:
            result["metadata"] = self.metadata
            
        return result


class LLMPort(ABC):
    """
    Abstract interface for LLM providers.
    
    This class defines the contract that all LLM providers
    must implement to integrate with the system.
    """
    
    @abstractmethod
    async def generate(self, messages: List[Message], **kwargs) -> Any:
        """
        Generate a response from the LLM.
        
        Args:
            messages: List of messages representing the conversation
            **kwargs: Additional model parameters
            
        Returns:
            LLM response
        """
        pass
    
    @abstractmethod
    async def stream(self, messages: List[Message], **kwargs) -> Any:
        """
        Stream a response from the LLM.
        
        Args:
            messages: List of messages representing the conversation
            **kwargs: Additional model parameters
            
        Returns:
            Async iterator of response chunks
        """
        pass
