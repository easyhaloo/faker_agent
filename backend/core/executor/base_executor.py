"""
Base executor module for running tasks and calling tools.
"""
import asyncio
import logging
import traceback
from typing import Any, Dict, List, Optional, Union

import litellm
from litellm import completion
from pydantic import BaseModel

from backend.config.settings import settings
from backend.core.planner.base_planner import Plan, PlanStep
from backend.core.prompts.executor_prompts import (
    EXECUTOR_SYSTEM_MESSAGE,
    RESPONSE_GENERATION_PROMPT_TEMPLATE
)

# Configure logger
logger = logging.getLogger(__name__)


class ExecutionResult(BaseModel):
    """Result of executing a single step or tool call."""
    
    success: bool
    output: Any
    error: Optional[str] = None


class StepExecution(BaseModel):
    """Result of executing a plan step."""
    
    step_id: int
    step_description: str
    result: ExecutionResult
    tool_results: Dict[str, ExecutionResult] = {}


class TaskExecution(BaseModel):
    """Complete execution result for a task."""
    
    task_id: str
    original_query: str
    plan: Optional[Plan] = None
    steps: List[StepExecution] = []
    final_response: Optional[str] = None
    status: str = "pending"  # pending, running, completed, failed
    error: Optional[str] = None


class BaseExecutor:
    """
    Base executor class that runs tasks according to a plan.
    """
    
    def __init__(self, registry=None):
        self.model = settings.LITELLM_MODEL
        self.temperature = settings.LITELLM_TEMPERATURE
        self.max_tokens = settings.LITELLM_MAX_TOKENS
        self.registry = registry  # Tool registry (will be passed in)
        
        # Set API key and base URL from settings
        if settings.LITELLM_API_KEY:
            litellm.api_key = settings.LITELLM_API_KEY
            
        # Set custom base URL if provided
        if settings.LITELLM_BASE_URL:
            litellm.api_base = settings.LITELLM_BASE_URL
            
        logger.info(f"Initialized BaseExecutor with model: {self.model}")
    
    async def execute_task(self, task_id: str, query: str, plan: Plan) -> TaskExecution:
        """
        Execute a task based on the provided plan.
        
        Args:
            task_id: Unique identifier for the task
            query: The original query/task
            plan: The plan to execute
            
        Returns:
            TaskExecution object with execution results
        """
        task_execution = TaskExecution(
            task_id=task_id,
            original_query=query,
            plan=plan,
            status="running"
        )
        
        try:
            # Execute each step in the plan sequentially
            for step in plan.steps:
                step_result = await self._execute_step(step)
                task_execution.steps.append(step_result)
                
                # If a step failed, we might want to stop or adjust
                if not step_result.result.success:
                    logger.warning(f"Step {step.step_id} failed: {step_result.result.error}")
            
            # Generate final response
            final_response = await self._generate_response(query, task_execution)
            task_execution.final_response = final_response
            task_execution.status = "completed"
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            logger.error(traceback.format_exc())
            task_execution.status = "failed"
            task_execution.error = str(e)
            
        return task_execution
    
    async def _execute_step(self, step: PlanStep) -> StepExecution:
        """Execute a single step in the plan."""
        logger.info(f"Executing step {step.step_id}: {step.description}")
        
        step_execution = StepExecution(
            step_id=step.step_id,
            step_description=step.description,
            result=ExecutionResult(success=True, output=f"Executed: {step.description}")
        )
        
        try:
            # Execute any tool calls in this step
            for tool_call in step.tool_calls:
                tool_result = await self._execute_tool(tool_call)
                step_execution.tool_results[tool_call.get("tool_name", "unknown")] = tool_result
                
        except Exception as e:
            logger.error(f"Error in step {step.step_id}: {e}")
            step_execution.result = ExecutionResult(
                success=False,
                output=None,
                error=str(e)
            )
            
        return step_execution
    
    async def _execute_tool(self, tool_call: Dict[str, Any]) -> ExecutionResult:
        """Execute a single tool call."""
        tool_name = tool_call.get("tool_name")
        parameters = tool_call.get("parameters", {})
        
        try:
            if self.registry and tool_name in self.registry.tools:
                tool = self.registry.tools[tool_name]
                result = await tool.run(**parameters)
                return ExecutionResult(success=True, output=result)
            else:
                return ExecutionResult(
                    success=False,
                    output=None,
                    error=f"Tool '{tool_name}' not found in registry"
                )
        except Exception as e:
            logger.error(f"Error executing tool '{tool_name}': {e}")
            return ExecutionResult(
                success=False,
                output=None,
                error=str(e)
            )
    
    async def _generate_response(self, query: str, execution: TaskExecution) -> str:
        """Generate a final response based on the execution results."""
        # Build prompt with execution results
        steps_summary = []
        for step in execution.steps:
            result = "✓ Success" if step.result.success else f"✗ Failed: {step.result.error}"
            steps_summary.append(f"Step {step.step_id}: {step.step_description} - {result}")
        
        steps_text = "\n".join(steps_summary)
        
        prompt = RESPONSE_GENERATION_PROMPT_TEMPLATE.format(
            query=query,
            steps_summary=steps_text
        )
        
        try:
            # Call LiteLLM
            response = await completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": EXECUTOR_SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error while processing your request: {str(e)}"