"""
Test for web search tool.
"""
import asyncio
import os
import sys

import pytest
from backend.core.tools.web_search import WebSearchTool


@pytest.mark.asyncio
async def test_web_search():
    """Test web search tool functionality."""
    # Initialize web search tool
    searcher = WebSearchTool()
    
    # Test basic search
    result = await searcher.run("Python programming", max_results=2)
    
    # Check that we got a result
    assert isinstance(result, dict)
    
    # If there's no error, check the structure
    if "error" not in result:
        assert "results" in result
        assert "total_results" in result
        assert len(result["results"]) <= 2
        for res in result["results"]:
            assert "title" in res
            assert "url" in res
            assert "snippet" in res
    
    # Test error handling with invalid input
    result = await searcher.run("")
    assert "error" in result