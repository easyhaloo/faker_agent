"""
Prompt templates for the planner module.
"""

# System message for the planner
PLANNER_SYSTEM_MESSAGE = "You are a helpful planning assistant."

# Planning prompt template
PLANNING_PROMPT_TEMPLATE = """
Task: {task}

Please create a step-by-step plan to complete this task.
Break it down into logical steps that can be executed sequentially.

For each step, consider:
1. What needs to be done
2. What tools or APIs might be needed
3. What information is required

Format the response as a numbered list of steps.
"""

# Context addition template
CONTEXT_ADDITION_TEMPLATE = """
Additional context:
{context}
"""