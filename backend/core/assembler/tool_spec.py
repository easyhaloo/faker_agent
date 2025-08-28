"""
Tool specifications for the LLM-based Assembler.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolSpec(BaseModel):
    """Tool specification for the LLM-based Assembler."""
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Parameters required by the tool"
    )


class ToolCall(BaseModel):
    """Tool call specification for the LLM-based Assembler."""
    
    tool_name: str = Field(..., description="Name of the tool to call")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the tool"
    )


class ToolNode(BaseModel):
    """Node in a tool chain graph."""
    
    id: str = Field(..., description="Unique identifier for this node")
    tool_call: ToolCall = Field(..., description="Tool to call at this node")
    dependencies: List[str] = Field(
        default_factory=list,
        description="IDs of nodes that must complete before this one"
    )
    condition: Optional[str] = Field(
        None,
        description="Optional condition for when to execute this node"
    )


class ToolChain(BaseModel):
    """Tool chain specification for the LLM-based Assembler."""
    
    nodes: List[ToolNode] = Field(
        default_factory=list,
        description="Nodes in the tool chain"
    )
    execution_order: str = Field(
        "sequential",
        description="How to execute the chain: 'sequential' or 'graph'"
    )


class AssemblerOutput(BaseModel):
    """Output from the LLM-based Assembler."""
    
    query: str = Field(..., description="Original user query")
    plan: str = Field(..., description="Plan for answering the query")
    tool_chain: ToolChain = Field(..., description="Tool chain to execute")


class ExecutionPlan(BaseModel):
    """Execution plan for a user query."""
    
    query: str = Field(..., description="Original user query")
    tools: List[ToolCall] = Field(
        default_factory=list,
        description="Sequential list of tool calls"
    )