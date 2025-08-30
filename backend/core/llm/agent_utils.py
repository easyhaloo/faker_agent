"""
Utility functions for working with LangChain agents.

This module provides helper functions for creating and working with
LangChain agents using our custom LiteLLM chat model.
"""
from typing import Dict, List, Optional, Union

from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import BaseTool

from backend.core.llm.chat_model_factory import get_chat_model


def create_agent_executor(
    tools: List[BaseTool],
    llm: Optional[BaseLanguageModel] = None,
    system_message: Optional[str] = None,
    verbose: bool = False
) -> AgentExecutor:
    """
    Create a LangChain agent executor with the specified tools and LLM.
    
    Args:
        tools: List of LangChain tools to make available to the agent
        llm: Language model to use (default: our default chat model)
        system_message: Optional system message to customize agent behavior
        verbose: Whether to enable verbose output
        
    Returns:
        A configured AgentExecutor instance
    """
    # Use default chat model if none provided
    llm = llm or get_chat_model()
    
    # Default system message if none provided
    if system_message is None:
        system_message = (
            "You are a helpful AI assistant. "
            "You have access to the following tools: {tool_names}\n\n"
            "{tools}\n\n"
            "To use a tool, please use the following format:\n"
            "```\n"
            "Thought: I need to use a tool\n"
            "Action: tool_name\n"
            "Action Input: the input to the tool\n"
            "```\n\n"
            "The observation will be the result of the tool.\n"
            "When you have a final answer, respond with:\n"
            "```\n"
            "Thought: I know the final answer\n"
            "Final Answer: the final answer to the original input question\n"
            "```\n\n"
            "Begin!\n"
        )
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create the agent
    agent = create_react_agent(llm, tools, prompt)
    
    # Create and return the executor
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=verbose,
        handle_parsing_errors=True
    )


def convert_to_langchain_tools(tools: List[Dict]) -> List[BaseTool]:
    """
    Convert our internal tool format to LangChain BaseTool instances.
    
    Args:
        tools: List of tool dictionaries in our internal format
        
    Returns:
        List of LangChain BaseTool instances
    """
    from langchain.tools import Tool
    
    langchain_tools = []
    
    for tool in tools:
        # Get required attributes
        name = tool.get("name")
        description = tool.get("description", "")
        func = tool.get("run")
        coroutine = tool.get("arun")
        
        if name and (func or coroutine):
            # Create a LangChain Tool
            langchain_tool = Tool(
                name=name,
                description=description,
                func=func if func else lambda *args, **kwargs: None,
                coroutine=coroutine
            )
            langchain_tools.append(langchain_tool)
    
    return langchain_tools