"""
Test for calculator tool.
"""
import asyncio
import os
import sys

import pytest
from backend.core.tools.calculator import CalculatorTool


@pytest.mark.asyncio
async def test_calculator():
    """Test calculator tool functionality."""
    # Initialize calculator tool
    calculator = CalculatorTool()
    
    # Test basic arithmetic
    result = await calculator.run("2 + 3")
    assert "result" in result
    assert result["result"] == 5
    
    # Test subtraction
    result = await calculator.run("10 - 4")
    assert "result" in result
    assert result["result"] == 6
    
    # Test multiplication
    result = await calculator.run("6 * 7")
    assert "result" in result
    assert result["result"] == 42
    
    # Test division
    result = await calculator.run("15 / 3")
    assert "result" in result
    assert result["result"] == 5
    
    # Test error cases
    result = await calculator.run("10 / 0")
    assert "error" in result
    
    result = await calculator.run("invalid expression")
    assert "error" in result