"""
Calculator tool for performing mathematical operations.
"""
from typing import Union

from backend.core.tools.base import BaseTool, ToolParameter


class CalculatorTool(BaseTool):
    """A calculator tool that performs basic mathematical operations."""
    
    name = "calculator"
    description = "Performs basic mathematical operations (+, -, *, /, ^, sqrt)"
    tags = ["math", "calculation"]
    priority = 5
    
    def get_parameters(self):
        return [
            {
                "name": "expression",
                "type": "string",
                "description": "Mathematical expression to evaluate (e.g., '2 + 3 * 4')",
                "required": True
            }
        ]
    
    async def run(self, expression: str) -> dict:
        """
        Evaluate a mathematical expression.
        
        Args:
            expression: Mathematical expression to evaluate
            
        Returns:
            Dictionary with result or error
        """
        try:
            # Safe evaluation of mathematical expression
            # Remove whitespace
            expr = expression.replace(" ", "")
            
            # Replace ^ with ** for exponentiation
            expr = expr.replace("^", "**")
            
            # Allowed characters (numbers, basic operators, parentheses, decimal point)
            allowed_chars = set("0123456789+-*/.()**sqrt")
            if not all(c in allowed_chars for c in expr):
                return {
                    "error": "Expression contains invalid characters",
                    "expression": expression
                }
            
            # Handle sqrt function
            if "sqrt" in expr:
                import re
                expr = re.sub(r"sqrt\(([^)]+)\)", r"(\1)**0.5", expr)
            
            # Evaluate expression
            result = eval(expr)
            
            return {
                "result": result,
                "expression": expression
            }
        except ZeroDivisionError:
            return {
                "error": "Division by zero",
                "expression": expression
            }
        except Exception as e:
            return {
                "error": f"Invalid expression: {str(e)}",
                "expression": expression
            }