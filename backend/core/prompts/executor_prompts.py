"""
Prompt templates for the executor module.
"""

# System message for the executor
EXECUTOR_SYSTEM_MESSAGE = "You are a helpful assistant."

# Response generation prompt template
RESPONSE_GENERATION_PROMPT_TEMPLATE = """
Original Query: {query}

Execution Steps:
{steps_summary}

Please provide a helpful response that addresses the original query based on the 
execution results above. Be concise and clear in your answer.
"""