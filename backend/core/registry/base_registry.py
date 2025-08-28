"""
Registry for managing tools and plugins.
"""
import logging
from typing import Any, Callable, Dict, List, Optional, Type

from pydantic import BaseModel, create_model

# Configure logger
logger = logging.getLogger(__name__)


class ToolParameter(BaseModel):
    """Parameter definition for a tool."""
    
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None


class ToolDefinition(BaseModel):
    """Definition of a tool that can be called by the agent."""
    
    tool_name: str
    description: str
    parameters: List[ToolParameter] = []
    return_schema: Dict[str, Any] = {}
    tags: List[str] = []
    priority: int = 0
    
    # These fields are not serialized
    function: Optional[Callable] = None
    tool_class: Optional[Type] = None


class BaseTool:
    """Base class for all tools."""
    
    name = "base_tool"
    description = "Base tool class"
    parameters = []
    tags = []
    priority = 0
    
    async def run(self, **kwargs) -> Any:
        """Run the tool with the provided parameters."""
        raise NotImplementedError("Subclasses must implement this method")
    
    @classmethod
    def get_definition(cls) -> ToolDefinition:
        """Get the tool definition."""
        params = []
        for param in cls.parameters:
            params.append(ToolParameter(
                name=param["name"],
                type=param["type"],
                description=param["description"],
                required=param.get("required", True),
                default=param.get("default")
            ))
        
        return ToolDefinition(
            tool_name=cls.name,
            description=cls.description,
            parameters=params,
            tags=cls.tags,
            priority=cls.priority,
            tool_class=cls
        )


class ToolRegistry:
    """Registry for managing tools and plugins."""
    
    def __init__(self):
        self.tools: Dict[str, ToolDefinition] = {}
        logger.info("Initialized ToolRegistry")
    
    def register_tool(self, tool_class: Type[BaseTool]) -> None:
        """Register a tool class."""
        tool_def = tool_class.get_definition()
        self.tools[tool_def.tool_name] = tool_def
        logger.info(f"Registered tool: {tool_def.tool_name}")
    
    def register_function(
        self, 
        name: str, 
        func: Callable, 
        description: str, 
        parameters: List[Dict[str, Any]]
    ) -> None:
        """Register a function as a tool."""
        params = []
        for param in parameters:
            params.append(ToolParameter(
                name=param["name"],
                type=param["type"],
                description=param["description"],
                required=param.get("required", True),
                default=param.get("default")
            ))
        
        tool_def = ToolDefinition(
            tool_name=name,
            description=description,
            parameters=params,
            function=func
        )
        
        self.tools[name] = tool_def
        logger.info(f"Registered function as tool: {name}")
    
    def get_tool(self, tool_name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self.tools.get(tool_name)
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List all registered tools."""
        result = []
        for name, tool in self.tools.items():
            result.append({
                "name": name,
                "description": tool.description,
                "parameters": [p.dict() for p in tool.parameters],
                "tags": tool.tags,
                "priority": tool.priority
            })
        return result
    
    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute a tool by name."""
        tool_def = self.get_tool(tool_name)
        if not tool_def:
            raise ValueError(f"Tool not found: {tool_name}")
        
        if tool_def.function:
            # Call function directly
            return await tool_def.function(**kwargs)
        elif tool_def.tool_class:
            # Create instance and call run
            tool = tool_def.tool_class()
            return await tool.run(**kwargs)
        else:
            raise ValueError(f"Tool '{tool_name}' has no executable implementation")


# Create global registry instance
registry = ToolRegistry()