"""
Prompt templates for the assembler module.
"""

# System message for the assembler
ASSEMBLER_SYSTEM_MESSAGE = "You are a tool chain planning assistant."

# Tool chain generation prompt template
TOOL_CHAIN_PROMPT_TEMPLATE = """
You are an AI assistant tasked with creating a tool execution plan to answer user queries.

USER QUERY: "{query}"

AVAILABLE TOOLS:
{tools_list}

Based on the user query, create a step-by-step execution plan using the available tools.
Your output must follow these steps:

1. ANALYSIS: Briefly analyze what the user is asking for (1-2 sentences)
2. PLAN: Create a step-by-step plan for answering the query (numbered list)
3. TOOL_CHAIN: Provide a JSON structure defining the tool chain to execute, following this schema:

```json
{{
    "query": "original user query",
    "plan": "brief description of the approach",
    "tool_chain": {{
        "nodes": [
            {{
                "id": "unique_node_id",
                "tool_call": {{
                    "tool_name": "name_of_tool",
                    "parameters": {{
                        "param1": "value1",
                        "param2": "value2"
                    }}
                }},
                "dependencies": ["id_of_dependent_node"],
                "condition": "optional condition expression"
            }}
        ],
        "execution_order": "sequential"
    }}
}}
```

IMPORTANT GUIDELINES:
- Only use tools from the provided list
- Ensure all required parameters are provided for each tool
- For simple queries, a single tool may be sufficient
- For complex queries, chain multiple tools together
- Use clear, unique IDs for each node (e.g., "node1", "node2")
- The "dependencies" field should list node IDs that must complete before this node executes
- Use "sequential" for the execution_order unless explicit dependencies are defined
- Do not add any explanations or text outside the JSON structure

YOUR RESPONSE:
"""

# Tool specification format template
TOOL_SPEC_FORMAT_TEMPLATE = """{index}. {name}: {description}
{parameters}
"""

# Parameter format template
PARAMETER_FORMAT_TEMPLATE = """    - {name} ({type}): {description} [{required}]"""

# Fallback prompt template
FALLBACK_PROMPT_TEMPLATE = """I'm sorry, but I couldn't generate a proper tool chain for your request. 
Please try rephrasing your query or ask something else."""