"""
Core tools module for the Faker Agent.

This package provides a framework for creating and managing tools that can
be used by the LangGraph orchestrator. Tools are operations that the agent
can perform to interact with external systems or compute results.
"""
from .base import BaseTool, ToolParameter, LangChainToolAdapter
from .registry import ToolRegistry, tool_registry
from .filtered_registry import FilteredToolRegistry, filtered_registry
from .calculator import CalculatorTool
from .web_search import WebSearchTool
from .weather import WeatherTool

__all__ = [
    "BaseTool",
    "ToolParameter",
    "LangChainToolAdapter",
    "ToolRegistry",
    "tool_registry",
    "FilteredToolRegistry",
    "filtered_registry",
    "CalculatorTool",
    "WebSearchTool",
    "WeatherTool"
]