"""
Error classes for the Faker Agent system.
"""


class FakerAgentError(Exception):
    """Base class for all Faker Agent errors."""
    
    def __init__(self, message: str = "An error occurred"):
        # Ensure message is properly encoded to handle Unicode characters
        self.message = message.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        super().__init__(self.message)


class ToolError(FakerAgentError):
    """Error raised when a tool fails to execute."""
    
    def __init__(self, tool_name: str, message: str = "Tool execution failed"):
        self.tool_name = tool_name
        super().__init__(f"{message}: {tool_name}")


class ToolNotFoundError(ToolError):
    """Error raised when a requested tool is not found."""
    
    def __init__(self, tool_name: str):
        super().__init__(tool_name, "Tool not found")


class ModelError(FakerAgentError):
    """Error raised when a model fails to generate a response."""
    
    def __init__(self, model_name: str, message: str = "Model generation failed"):
        self.model_name = model_name
        # Ensure message is properly encoded to handle Unicode characters
        safe_message = message.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        safe_model_name = model_name.encode('utf-8', errors='ignore').decode('utf-8', errors='ignore')
        super().__init__(f"{safe_message}: {safe_model_name}")


class AssemblerError(FakerAgentError):
    """Error raised when the assembler fails to generate a plan."""
    
    def __init__(self, message: str = "Failed to generate execution plan"):
        super().__init__(message)


class OrchestratorError(FakerAgentError):
    """Error raised when the orchestrator fails to execute a plan."""
    
    def __init__(self, message: str = "Failed to execute plan"):
        super().__init__(message)


class ProtocolError(FakerAgentError):
    """Error raised when a protocol fails to send a message."""
    
    def __init__(self, protocol_name: str, message: str = "Protocol error"):
        self.protocol_name = protocol_name
        super().__init__(f"{message}: {protocol_name}")


class ConfigurationError(FakerAgentError):
    """Error raised when there is a configuration issue."""
    
    def __init__(self, setting: str, message: str = "Configuration error"):
        self.setting = setting
        super().__init__(f"{message}: {setting}")