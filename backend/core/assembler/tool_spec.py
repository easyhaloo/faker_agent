"""
Tool specifications for the LLM-based Assembler.

This module defines the data models used by the LLM Assembler to create
and validate execution plans. These models are used to represent tool
specifications, tool calls, and the structure of the execution plan.
"""
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.core.contracts.tools import ToolSpec as ContractToolSpec
from backend.core.contracts.execution import ExecutionPlan as ContractExecutionPlan


class ToolSpec(BaseModel):
    """Tool specification for the LLM-based Assembler."""
    
    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Description of what the tool does")
    parameters: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Parameters required by the tool"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for tool categorization")
    priority: int = Field(0, description="Tool priority for ranking")
    
    def to_contract(self) -> ContractToolSpec:
        """Convert to contract ToolSpec."""
        return ContractToolSpec(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            tags=self.tags,
            priority=self.priority
        )
    
    @classmethod
    def from_contract(cls, spec: ContractToolSpec) -> "ToolSpec":
        """Create ToolSpec from contract ToolSpec."""
        return cls(
            name=spec.name,
            description=spec.description,
            parameters=spec.parameters,
            tags=spec.tags,
            priority=spec.priority
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
    plan: str = Field("", description="Natural language description of the plan")
    tool_chain: ToolChain = Field(..., description="Tool chain to execute")
    context: Dict[str, Any] = Field(default_factory=dict, description="Execution context")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def to_contract(self) -> ContractExecutionPlan:
        """Convert to contract ExecutionPlan."""
        return ContractExecutionPlan(
            query=self.query,
            plan=self.plan,
            tool_chain=self.tool_chain,
            context=self.context,
            metadata=self.metadata
        )
    
    @classmethod
    def from_assembler_output(cls, output: "AssemblerOutput") -> "ExecutionPlan":
        """Create ExecutionPlan from AssemblerOutput."""
        return cls(
            query=output.query,
            plan=output.plan,
            tool_chain=output.tool_chain,
            context={},
            metadata={}
        )