"""
LLM-based Assembler for generating tool chains from user queries.
"""
import json
import logging
import re
from typing import Any, Dict, List, Optional

import litellm
from litellm import completion

from backend.config.settings import settings
from backend.core.assembler.tool_spec import (
    AssemblerOutput,
    ExecutionPlan,
    ToolCall,
    ToolChain,
    ToolNode,
    ToolSpec
)
from backend.core.filters.filter_manager import filter_manager
from backend.core.prompts.assembler_prompts import (
    ASSEMBLER_SYSTEM_MESSAGE,
    TOOL_CHAIN_PROMPT_TEMPLATE,
    TOOL_SPEC_FORMAT_TEMPLATE,
    PARAMETER_FORMAT_TEMPLATE,
    FALLBACK_PROMPT_TEMPLATE
)
from backend.core.tools.base import BaseTool

# Configure logger
logger = logging.getLogger(__name__)


class LLMAssembler:
    """
    LLM-based Assembler for generating tool chains from user queries.
    
    This class uses an LLM to analyze user queries and generate a plan
    for executing the appropriate tools to fulfill the request.
    """
    
    def __init__(
        self,
        filter_strategy: Optional[str] = None,
        tool_tags: Optional[List[str]] = None
    ):
        """
        Initialize the LLM Assembler.
        
        Args:
            filter_strategy: Optional filter strategy name
            tool_tags: Optional tool tags to pre-filter by
        """
        # Get filtered tools
        self.tools = filter_manager.filter_tools(
            strategy_name=filter_strategy,
            tags=tool_tags
        )
        
        # LLM settings
        self.model = settings.LITELLM_MODEL
        self.temperature = 0.0  # Use low temperature for deterministic planning
        self.max_tokens = settings.LITELLM_MAX_TOKENS
        
        # Set API key from settings
        if settings.LITELLM_API_KEY:
            litellm.api_key = settings.LITELLM_API_KEY
            
        # Set custom base URL if provided
        if settings.LITELLM_BASE_URL:
            litellm.api_base = settings.LITELLM_BASE_URL
            
        logger.info(f"Initialized LLMAssembler with {len(self.tools)} tools")
    
    def _get_tool_specs(self) -> List[ToolSpec]:
        """
        Get tool specifications for the available tools.
        
        Returns:
            List of tool specifications
        """
        specs = []
        
        for tool in self.tools:
            # Get parameters schema
            params = {}
            for param in getattr(tool, 'parameters', []):
                param_name = param.get('name', '')
                if param_name:
                    params[param_name] = {
                        'type': param.get('type', 'string'),
                        'description': param.get('description', ''),
                        'required': param.get('required', True)
                    }
            
            # Create tool spec
            spec = ToolSpec(
                name=tool.name,
                description=tool.description,
                parameters=params
            )
            specs.append(spec)
            
        return specs
    
    async def _create_chain_prompt(self, query: str) -> str:
        """
        Create a prompt for generating a tool chain.
        
        Args:
            query: The user's query
            
        Returns:
            Prompt for the LLM
        """
        # Get tool specs
        tool_specs = self._get_tool_specs()
        
        # Format tool specifications for the prompt
        tools_text = ""
        for i, spec in enumerate(tool_specs, 1):
            params_text = ""
            for param_name, param_info in spec.parameters.items():
                required = "REQUIRED" if param_info.get('required', True) else "OPTIONAL"
                params_text += PARAMETER_FORMAT_TEMPLATE.format(
                    name=param_name,
                    type=param_info.get('type', 'string'),
                    description=param_info.get('description', ''),
                    required=required
                ) + "\n"
            
            # Format parameters section
            formatted_params = ""
            if params_text:
                formatted_params = "   Parameters:\n" + params_text
            
            tools_text += TOOL_SPEC_FORMAT_TEMPLATE.format(
                index=i,
                name=spec.name,
                description=spec.description,
                parameters=formatted_params
            ) + "\n"
            
        # Create the prompt
        prompt = TOOL_CHAIN_PROMPT_TEMPLATE.format(
            query=query,
            tools_list=tools_text
        )
        
        return prompt
    
    async def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from LLM output text.
        
        Args:
            text: The text to extract JSON from
            
        Returns:
            Extracted JSON as a dictionary, or None if not found
        """
        # Try to find JSON within markdown code blocks first
        matches = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON surrounded by brackets
        matches = re.findall(r'({[\s\S]*})', text)
        if matches:
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # No valid JSON found
        return None
    
    async def assemble(self, query: str) -> AssemblerOutput:
        """
        Generate a tool chain for answering a user query.
        
        Args:
            query: The user's query
            
        Returns:
            An AssemblerOutput with the generated tool chain
        """
        try:
            # Create the prompt
            prompt = await self._create_chain_prompt(query)
            
            # Call the LLM
            response = await completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": ASSEMBLER_SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract the output text
            output_text = response.choices[0].message.content.strip()
            
            # Extract JSON from the output
            json_data = await self._extract_json(output_text)
            if not json_data:
                logger.warning(f"Could not extract JSON from LLM output: {output_text}")
                # Fallback to a simple execution plan
                return self._create_fallback_plan(query)
            
            # Validate the JSON schema
            try:
                return AssemblerOutput(**json_data)
            except Exception as e:
                logger.error(f"Error validating JSON schema: {e}")
                return self._create_fallback_plan(query)
                
        except Exception as e:
            logger.error(f"Error in LLM Assembler: {e}")
            return self._create_fallback_plan(query)
    
    async def create_execution_plan(self, query: str) -> ExecutionPlan:
        """
        Create a simplified execution plan from a user query.
        
        This method is a simplified version of assemble() that returns
        a linear list of tool calls rather than a full graph.
        
        Args:
            query: The user's query
            
        Returns:
            An execution plan with a list of tool calls
        """
        try:
            # Generate the full tool chain
            assembler_output = await self.assemble(query)
            
            # Extract tool calls in the correct order
            tool_calls = []
            
            if assembler_output.tool_chain.execution_order == "sequential":
                # For sequential execution, just take nodes in order
                for node in assembler_output.tool_chain.nodes:
                    tool_calls.append(node.tool_call)
                    
            else:
                # For graph execution, we need to sort by dependencies
                # This is a simplified topological sort
                remaining_nodes = list(assembler_output.tool_chain.nodes)
                while remaining_nodes:
                    # Find nodes with no remaining dependencies
                    ready_nodes = []
                    for node in remaining_nodes:
                        if not node.dependencies:
                            ready_nodes.append(node)
                    
                    if not ready_nodes:
                        # If no nodes are ready, there might be a cycle
                        # Just add the remaining nodes in order
                        for node in remaining_nodes:
                            tool_calls.append(node.tool_call)
                        break
                    
                    # Add ready nodes to the execution plan
                    for node in ready_nodes:
                        tool_calls.append(node.tool_call)
                        remaining_nodes.remove(node)
                        
                        # Remove this node from dependencies
                        for other_node in remaining_nodes:
                            if node.id in other_node.dependencies:
                                other_node.dependencies.remove(node.id)
            
            return ExecutionPlan(
                query=query,
                tools=tool_calls
            )
            
        except Exception as e:
            logger.error(f"Error creating execution plan: {e}")
            # Create a simple fallback plan
            return ExecutionPlan(
                query=query,
                tools=[]
            )
    
    def _create_fallback_plan(self, query: str) -> AssemblerOutput:
        """
        Create a fallback plan when LLM assembly fails.
        
        Args:
            query: The user's query
            
        Returns:
            A simple AssemblerOutput
        """
        # Try to find a weather-related tool as fallback
        weather_tool = None
        for tool in self.tools:
            if "weather" in tool.name.lower():
                weather_tool = tool
                break
        
        # If no weather tool, use the first available tool
        if not weather_tool and self.tools:
            weather_tool = self.tools[0]
        
        # Create a fallback tool chain
        if weather_tool:
            tool_call = ToolCall(
                tool_name=weather_tool.name,
                parameters={"query": query}
            )
            
            node = ToolNode(
                id="fallback_node",
                tool_call=tool_call,
                dependencies=[]
            )
            
            tool_chain = ToolChain(
                nodes=[node],
                execution_order="sequential"
            )
            
            return AssemblerOutput(
                query=query,
                plan="Fallback plan using available tool",
                tool_chain=tool_chain
            )
        else:
            # No tools available
            empty_chain = ToolChain(
                nodes=[],
                execution_order="sequential"
            )
            
            return AssemblerOutput(
                query=query,
                plan="No tools available to answer query",
                tool_chain=empty_chain
            )


# Create global assembler instance
assembler = LLMAssembler()