"""
Execution contracts for the Faker Agent.

This module provides contract classes for execution plans and workflows,
enabling structured orchestration of tool chains and LLM interactions.
"""
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field

# Configure logger
logger = logging.getLogger(__name__)


class ToolInvocation(BaseModel):
    """
    Tool invocation specification.
    
    This class represents a planned invocation of a tool,
    including the tool name and parameters to be used.
    """
    
    tool_name: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters
        }


class ExecutionNode(BaseModel):
    """
    Node in an execution plan.
    
    This class represents a single step in an execution plan,
    consisting of a tool invocation and related metadata.
    """
    
    id: str
    tool_invocation: ToolInvocation
    next_nodes: List[str] = Field(default_factory=list)
    condition: Optional[str] = None
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        result = {
            "id": self.id,
            "tool_invocation": self.tool_invocation.dict(),
            "next_nodes": self.next_nodes
        }
        
        if self.condition:
            result["condition"] = self.condition
            
        return result


class ToolChain(BaseModel):
    """
    Tool chain for structured execution.
    
    This class represents a chain of tool invocations that can be
    executed in sequence or conditionally based on a graph structure.
    """
    
    nodes: List[ExecutionNode]
    entry_node: str
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "nodes": [node.dict() for node in self.nodes],
            "entry_node": self.entry_node
        }


class ExecutionPlan(BaseModel):
    """
    Execution plan for the agent.
    
    This class represents a complete plan for executing a task,
    including the tool chain to use and related metadata.
    """
    
    id: str
    tool_chain: ToolChain
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "id": self.id,
            "tool_chain": self.tool_chain.dict(),
            "metadata": self.metadata
        }
