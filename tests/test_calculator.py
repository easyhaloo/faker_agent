"""
Test for calculator tool.
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.core.tools.calculator import CalculatorTool


async def test_calculator():
    """Test calculator tool functionality."""
    # Initialize calculator tool
    calculator = CalculatorTool()
    
    # Test expressions
    expressions = [
        "2 + 3",
        "10 - 4",
        "6 * 7",
        "15 / 3",
        "2 ^ 3",
        "sqrt(16)",
        "2 * (3 + 4)",
        "10 / 0",  # Division by zero
        "invalid expression"  # Invalid expression
    ]
    
    print("Testing calculator tool...")
    for expr in expressions:
        print(f"\nEvaluating: {expr}")
        result = await calculator.run(expr)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Result: {result['result']}")
    
    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(test_calculator())