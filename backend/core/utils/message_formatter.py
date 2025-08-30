"""
消息格式化工具，用于处理LangChain消息格式转换。

提供标准化的消息格式转换功能，确保消息在不同组件之间传递时保持一致格式。
"""
from typing import Any, Dict, List, Optional, Union

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend.core.utils.logging import get_logger

# 配置日志
logger = get_logger()

class MessageFormatter:
    """
    消息格式化工具类，提供各种消息格式之间的转换功能。
    
    统一消息格式，确保在调用链的各个环节中消息格式保持一致。
    """
    
    @staticmethod
    def to_dict_format(message: Union[HumanMessage, AIMessage, ToolMessage, Dict[str, Any]]) -> Dict[str, Any]:
        """
        将LangChain消息对象转换为标准字典格式。
        
        Args:
            message: LangChain消息对象或已经是字典格式的消息
            
        Returns:
            包含role和content键的标准字典格式
        """
        # 如果已经是字典且包含必要的字段，直接返回
        if isinstance(message, dict) and "role" in message and "content" in message:
            return message
            
        # 根据消息类型转换
        if isinstance(message, HumanMessage):
            return {
                "role": "user",
                "content": message.content
            }
        elif isinstance(message, AIMessage):
            result = {
                "role": "assistant",
                "content": message.content
            }
            # 如果有tool_calls，添加到结果中
            if hasattr(message, 'tool_calls') and message.tool_calls:
                result["tool_calls"] = message.tool_calls
            return result
        elif isinstance(message, ToolMessage):
            return {
                "role": "tool",
                "content": message.content,
                "tool_call_id": message.tool_call_id,
                "name": message.name
            }
        else:
            # 无法识别的类型，尝试提取内容
            content = getattr(message, 'content', str(message))
            return {
                "role": "user",  # 默认为用户消息
                "content": content
            }
    
    @staticmethod
    def to_langchain_format(message: Dict[str, Any]) -> Union[HumanMessage, AIMessage, ToolMessage]:
        """
        将字典格式的消息转换为LangChain消息对象。
        
        Args:
            message: 包含role和content键的字典
            
        Returns:
            对应的LangChain消息对象
        """
        if not isinstance(message, dict) or "role" not in message or "content" not in message:
            # 无效的格式，返回默认HumanMessage
            content = str(message) if not isinstance(message, dict) else message.get("content", str(message))
            return HumanMessage(content=content)
        
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            return HumanMessage(content=content)
        elif role == "assistant":
            # 检查是否有tool_calls
            if "tool_calls" in message:
                return AIMessage(content=content, tool_calls=message["tool_calls"])
            else:
                return AIMessage(content=content)
        elif role == "tool":
            # 工具消息需要tool_call_id和name
            if "tool_call_id" in message and "name" in message:
                return ToolMessage(
                    content=content,
                    tool_call_id=message["tool_call_id"],
                    name=message["name"]
                )
            else:
                logger.warning(f"工具消息缺少必要字段: {message}")
                return AIMessage(content=content)
        else:
            # 未知角色，默认为HumanMessage
            logger.warning(f"未知消息角色: {role}")
            return HumanMessage(content=content)
    
    @staticmethod
    def convert_message_list(messages: List[Any]) -> List[Dict[str, Any]]:
        """
        将消息列表转换为标准字典格式列表。
        
        Args:
            messages: 混合类型的消息列表
            
        Returns:
            标准字典格式的消息列表
        """
        result = []
        for msg in messages:
            # 处理嵌套消息结构
            if isinstance(msg, dict) and "messages" in msg:
                nested_messages = msg["messages"]
                for nested_msg in nested_messages:
                    result.append(MessageFormatter.to_dict_format(nested_msg))
            else:
                result.append(MessageFormatter.to_dict_format(msg))
        return result
    
    @staticmethod
    def prepare_litellm_messages(messages: List[Any]) -> List[Dict[str, Any]]:
        """
        准备用于LiteLLM的消息列表。
        
        Args:
            messages: 混合类型的消息列表
            
        Returns:
            适用于LiteLLM的标准消息列表
        """
        return MessageFormatter.convert_message_list(messages)
    
    @staticmethod
    def prepare_langchain_messages(messages: List[Dict[str, Any]]) -> List[Union[HumanMessage, AIMessage, ToolMessage]]:
        """
        准备用于LangChain的消息列表。
        
        Args:
            messages: 字典格式的消息列表
            
        Returns:
            LangChain消息对象列表
        """
        return [MessageFormatter.to_langchain_format(msg) for msg in messages]


# 创建全局实例，方便导入
message_formatter = MessageFormatter()