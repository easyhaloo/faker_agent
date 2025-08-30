"""
LLM-based Assembler for generating tool chains from user queries.

This module provides an LLM-based Assembler that analyzes user queries and
generates a plan for executing the appropriate tools to fulfill the request.
It uses the LLM to determine which tools to use and in what order, validating
the generated plan against the available tools.
"""
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple, Union

from backend.config.settings import settings
from backend.core.assembler.tool_spec import (
    AssemblerOutput,
    ExecutionPlan,
    ToolCall,
    ToolChain,
    ToolNode,
    ToolSpec
)
from backend.core.contracts.base import Message
from backend.core.contracts.execution import ExecutionPlan as ContractExecutionPlan
from backend.core.contracts.models import ModelRequest
from backend.core.filters.filter_manager import filter_manager
from backend.core.infrastructure.llm.factory import llm_factory
from backend.core.prompts.assembler_prompts import (
    ASSEMBLER_SYSTEM_MESSAGE,
    TOOL_CHAIN_PROMPT_TEMPLATE,
    TOOL_SPEC_FORMAT_TEMPLATE,
    PARAMETER_FORMAT_TEMPLATE,
    FALLBACK_PROMPT_TEMPLATE
)
from backend.core.tools.base import BaseTool
from backend.core.tools.registry import tool_registry

# Configure logger
logger = logging.getLogger(__name__)


class LLMAssembler:
    """
    LLM-based Assembler for generating tool chains from user queries.
    
    This class uses an LLM to analyze user queries and generate a plan
    for executing the appropriate tools to fulfill the request. It integrates
    with the LLM infrastructure and tool registry to provide a flexible
    and extensible planning system.
    """
    
    def __init__(
        self,
        filter_strategy: Optional[str] = None,
        tool_tags: Optional[List[str]] = None,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ):
        """
        Initialize the LLM Assembler.
        
        Args:
            filter_strategy: Optional filter strategy name
            tool_tags: Optional tool tags to pre-filter by
            model: Optional model name to use
            temperature: Optional temperature for generation
            max_tokens: Optional maximum tokens to generate
        """
        # Get filtered tools
        self.tools = filter_manager.filter_tools(
            strategy_name=filter_strategy,
            tags=tool_tags
        )
        
        # LLM settings
        self.model = model or settings.LITELLM_MODEL
        self.temperature = temperature if temperature is not None else 0.0  # Use low temperature for deterministic planning
        self.max_tokens = max_tokens or settings.LITELLM_MAX_TOKENS
        
        # Get LLM client from factory
        self.llm_client = llm_factory.get_default_client()
            
        logger.info(f"Initialized LLMAssembler with {len(self.tools)} tools and model {self.model}")
    
    async def get_response(self, query: str, messages: List[Any] = None) -> Any:
        """
        Get a response from the LLM for a user query.
        
        Args:
            query: The user's query
            messages: Optional list of previous messages for context
            
        Returns:
            LLM response object
        """
        try:
            # Prepare messages for the LLM
            llm_messages = []
            
            # Add system message
            llm_messages.append(Message(
                role="system", 
                content=ASSEMBLER_SYSTEM_MESSAGE
            ))
            
            # Add previous messages if provided
            if messages:
                for msg in messages:
                    if hasattr(msg, 'role') and hasattr(msg, 'content'):
                        llm_messages.append(Message(
                            role=msg.role, 
                            content=msg.content
                        ))
                    elif isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                        llm_messages.append(Message(
                            role=msg['role'], 
                            content=msg['content']
                        ))
            
            # Add current query
            llm_messages.append(Message(
                role="user", 
                content=query
            ))
            
            # Create model request
            request = ModelRequest(
                messages=llm_messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Start time for performance monitoring
            start_time = time.time()
            
            # Call the LLM
            response = await self.llm_client.generate(request)
            
            # Log execution time
            execution_time = time.time() - start_time
            logger.info(f"LLM response generated in {execution_time:.2f}s")
            
            # Return the response message
            return response.message
            
        except Exception as e:
            logger.error(f"Error getting LLM response: {e}")
            # Return a simple fallback response as a dictionary to ensure compatibility
            # Ensure the error message is properly encoded to handle Unicode characters
            error_msg = str(e)
            error_msg = error_msg.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
            return {
                "role": "assistant",
                "content": f"抱歉，我在处理您的请求时遇到了问题: {error_msg}"
            }
    
    def _get_tool_specs(self) -> List[ToolSpec]:
        """
        Get tool specifications for the available tools.
        
        Returns:
            List of tool specifications
        """
        specs = []
        
        for tool in self.tools:
            # Use tool's spec if available
            if hasattr(tool, 'spec'):
                # Convert from contract to assembler spec
                spec = ToolSpec.from_contract(tool.spec)
                specs.append(spec)
            else:
                # Fallback to creating spec from tool attributes
                params = {}
                for param in getattr(tool, 'get_parameters', lambda: [])():
                    param_name = getattr(param, 'name', '')
                    if param_name:
                        params[param_name] = {
                            'type': getattr(param, 'type', 'string'),
                            'description': getattr(param, 'description', ''),
                            'required': getattr(param, 'required', True)
                        }
                
                # Create tool spec
                spec = ToolSpec(
                    name=tool.name,
                    description=tool.description,
                    parameters=params,
                    tags=getattr(tool, 'tags', []),
                    priority=getattr(tool, 'priority', 0)
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
            
            # Prepare messages
            messages = [
                Message(role="system", content=ASSEMBLER_SYSTEM_MESSAGE),
                Message(role="user", content=prompt)
            ]
            
            # Create model request
            request = ModelRequest(
                messages=messages,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Start time for performance monitoring
            start_time = time.time()
            
            # Call the LLM
            response = await self.llm_client.generate(request)
            
            # Log execution time
            execution_time = time.time() - start_time
            logger.info(f"Assembler plan generated in {execution_time:.2f}s")
            
            # Extract the output text
            output_text = response.message.content.strip()
            
            # Extract JSON from the output
            json_data = await self._extract_json(output_text)
            if not json_data:
                logger.warning(f"Could not extract JSON from LLM output: {output_text}")
                # Fallback to a simple execution plan
                return self._create_fallback_plan(query)
            
            # Validate the JSON schema
            try:
                output = AssemblerOutput(**json_data)
                
                # Validate that all tools exist
                self._validate_tools_exist(output.tool_chain)
                
                return output
            except Exception as e:
                logger.error(f"Error validating JSON schema: {e}")
                return self._create_fallback_plan(query)
                
        except Exception as e:
            logger.error(f"Error in LLM Assembler: {e}")
            return self._create_fallback_plan(query)
            
    def _validate_tools_exist(self, tool_chain: ToolChain) -> None:
        """
        Validate that all tools in the chain exist in the registry.
        
        Args:
            tool_chain: The tool chain to validate
        
        Raises:
            ValueError: If a tool doesn't exist
        """
        for node in tool_chain.nodes:
            tool_name = node.tool_call.tool_name
            if not tool_registry.get_tool(tool_name):
                logger.warning(f"Tool not found in registry: {tool_name}")
                raise ValueError(f"Tool not found: {tool_name}")
    
    async def create_execution_plan(self, query: str) -> ExecutionPlan:
        """
        Create an execution plan from a user query.
        
        This method uses the assemble() method to generate a tool chain
        and converts it to an execution plan that can be used by the
        flow orchestrator.
        
        Args:
            query: The user's query
            
        Returns:
            An ExecutionPlan with the tool chain
        """
        try:
            # Generate the full tool chain
            assembler_output = await self.assemble(query)
            
            # Convert to execution plan
            execution_plan = ExecutionPlan.from_assembler_output(assembler_output)
            
            # Add metadata
            execution_plan.metadata["generation_time"] = time.time()
            execution_plan.metadata["tool_count"] = len(assembler_output.tool_chain.nodes)
            execution_plan.metadata["model"] = self.model
            
            return execution_plan
            
        except Exception as e:
            logger.error(f"Error creating execution plan: {e}")
            # Create a simple fallback plan
            empty_chain = ToolChain(
                nodes=[],
                execution_order="sequential"
            )
            
            return ExecutionPlan(
                query=query,
                plan=f"Error creating plan: {str(e)}",
                tool_chain=empty_chain,
                context={},
                metadata={"error": str(e)}
            )
            
    async def create_contract_execution_plan(self, query: str) -> ContractExecutionPlan:
        """
        Create a contract-compatible execution plan from a user query.
        
        This is a convenience method that generates an execution plan
        and converts it to the contract format used by other components.
        
        Args:
            query: The user's query
            
        Returns:
            A contract-compatible execution plan
        """
        execution_plan = await self.create_execution_plan(query)
        return execution_plan.to_contract()
    
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