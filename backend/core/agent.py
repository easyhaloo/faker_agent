"""
Main agent class that orchestrates planning and execution.
"""
import asyncio
import logging
import uuid
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from backend.core.executor.base_executor import BaseExecutor, TaskExecution
from backend.core.memory.simple_memory import memory
from backend.core.planner.base_planner import BasePlanner, Plan
from backend.core.registry.base_registry import registry

# Configure logger
logger = logging.getLogger(__name__)


class AgentResponse(BaseModel):
    """Response from the agent to a user query."""
    
    task_id: str
    response: str
    actions: List[Dict[str, Any]] = []


class Agent:
    """
    Main agent class that orchestrates planning and execution.
    """
    
    def __init__(self):
        self.planner = BasePlanner()
        self.executor = BaseExecutor(registry=registry)
        logger.info("Initialized Agent")
    
    async def process_query(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """
        Process a user query and return a response.
        
        Args:
            query: The user's query
            conversation_id: Optional conversation ID for context
            context: Optional additional context
            
        Returns:
            AgentResponse with the agent's response
        """
        # Generate IDs if not provided
        conversation_id = conversation_id or str(uuid.uuid4())
        task_id = str(uuid.uuid4())
        context = context or {}
        
        try:
            # Store the user query in memory
            await memory.add_message(conversation_id, "user", query)
            
            # 1. Planning: Break down the task
            logger.info(f"Planning for query: {query}")
            plan = await self.planner.create_plan(query, context)
            
            # 2. Execution: Execute the plan
            logger.info(f"Executing plan for task {task_id}")
            execution = await self.executor.execute_task(task_id, query, plan)
            
            # 3. Response: Get the final response
            response = execution.final_response or "I wasn't able to complete the task."
            
            # Store the agent's response in memory
            await memory.add_message(conversation_id, "assistant", response)
            
            # Extract actions for the response
            actions = self._extract_actions(execution)
            
            return AgentResponse(
                task_id=task_id,
                response=response,
                actions=actions
            )
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            error_response = f"I encountered an error: {str(e)}"
            
            # Store the error response
            await memory.add_message(conversation_id, "assistant", error_response)
            
            return AgentResponse(
                task_id=task_id,
                response=error_response,
                actions=[]
            )
    
    def _extract_actions(self, execution: TaskExecution) -> List[Dict[str, Any]]:
        """Extract actions from the execution result for the response."""
        actions = []
        
        for step in execution.steps:
            for tool_name, result in step.tool_results.items():
                if result.success:
                    actions.append({
                        "tool": tool_name,
                        "result": result.output
                    })
        
        return actions


# Create global agent instance
agent = Agent()