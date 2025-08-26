"""
Base planner module that uses LiteLLM to generate task plans.
"""
import logging
from typing import Any, Dict, List, Optional

import litellm
from litellm import completion
from pydantic import BaseModel, Field

from backend.config.settings import settings

# Configure logger
logger = logging.getLogger(__name__)


class PlanStep(BaseModel):
    """A single step in a task plan."""
    
    step_id: int
    description: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)


class Plan(BaseModel):
    """A complete task plan with multiple steps."""
    
    plan_id: str
    task: str
    steps: List[PlanStep] = Field(default_factory=list)


class BasePlanner:
    """
    Base planner class that uses LLMs to generate task plans.
    """
    
    def __init__(self):
        self.model = settings.LITELLM_MODEL
        self.temperature = settings.LITELLM_TEMPERATURE
        self.max_tokens = settings.LITELLM_MAX_TOKENS
        
        # Set API key from settings
        if settings.LITELLM_API_KEY:
            litellm.api_key = settings.LITELLM_API_KEY
        
        logger.info(f"Initialized BasePlanner with model: {self.model}")
    
    async def create_plan(self, task: str, context: Optional[Dict[str, Any]] = None) -> Plan:
        """
        Create a plan for the given task.
        
        Args:
            task: The natural language task to plan for
            context: Optional context information
            
        Returns:
            A Plan object with steps
        """
        context = context or {}
        
        # Create prompt for the LLM
        prompt = self._build_planning_prompt(task, context)
        
        try:
            # Call LiteLLM
            response = await completion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful planning assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract and parse the plan
            plan_text = response.choices[0].message.content
            plan = self._parse_plan(task, plan_text)
            
            return plan
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            # Return a simple error plan
            return Plan(
                plan_id="error",
                task=task,
                steps=[PlanStep(step_id=1, description=f"Error creating plan: {str(e)}")]
            )
    
    def _build_planning_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build the planning prompt for the LLM."""
        prompt = f"""
        Task: {task}
        
        Please create a step-by-step plan to complete this task.
        Break it down into logical steps that can be executed sequentially.
        
        For each step, consider:
        1. What needs to be done
        2. What tools or APIs might be needed
        3. What information is required
        
        Format the response as a numbered list of steps.
        """
        
        # Add context if available
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            prompt += f"\n\nAdditional context:\n{context_str}"
            
        return prompt
    
    def _parse_plan(self, task: str, plan_text: str) -> Plan:
        """Parse the LLM output into a structured Plan object."""
        import re
        import uuid
        
        # Generate a unique plan ID
        plan_id = str(uuid.uuid4())
        
        # Create plan object
        plan = Plan(plan_id=plan_id, task=task)
        
        # Simple parsing: look for numbered steps
        steps = re.findall(r"(\d+)[\.:\)]\s*(.*?)(?=\n\d+[\.:\)]|\Z)", plan_text, re.DOTALL)
        
        if not steps:
            # Fallback: split by newlines and try to create steps
            lines = [line.strip() for line in plan_text.split("\n") if line.strip()]
            for i, line in enumerate(lines):
                plan.steps.append(PlanStep(step_id=i+1, description=line))
        else:
            for step_num, step_desc in steps:
                plan.steps.append(
                    PlanStep(
                        step_id=int(step_num),
                        description=step_desc.strip()
                    )
                )
        
        return plan