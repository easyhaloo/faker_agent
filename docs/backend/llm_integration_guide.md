# LangChain 和 LiteLLM 集成指南

## 简介

本指南提供了在 Faker Agent 项目中集成 LangChain 和 LiteLLM 的详细步骤和最佳实践。这种集成允许我们充分利用 LangChain 的工具和代理功能，同时通过 LiteLLM 灵活地接入各种大语言模型提供商。

## 集成架构

集成架构采用分层设计，确保清晰的职责分离和灵活的组件替换：

```
backend/core/llm/
├── __init__.py              # 包导出
├── litellm_chat_model.py    # 自定义 LangChain 聊天模型
├── chat_model_factory.py    # 工厂函数，创建不同配置的模型
└── agent_utils.py           # LangChain 代理工具
```

### 核心组件

1. **LiteLLMChatModel 类**：实现 LangChain 的 `BaseChatModel` 接口，提供与 LiteLLM 的直接集成
2. **模型工厂**：提供创建各种配置模型实例的工厂函数
3. **代理工具**：提供创建和使用 LangChain 代理的辅助函数
4. **消息格式化**：统一消息格式转换，确保不同组件之间无缝通信

## 实现步骤

### 1. 安装依赖

确保项目中安装了以下依赖：

```bash
pip install langchain langchain-core litellm
```

### 2. 创建自定义聊天模型

在 `litellm_chat_model.py` 中实现自定义聊天模型，继承自 LangChain 的 `BaseChatModel`：

```python
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

class LiteLLMChatModel(BaseChatModel):
    """自定义 LangChain 聊天模型，使用 LiteLLM 作为后端。"""
    
    model_name: str = settings.LITELLM_MODEL
    temperature: float = settings.LITELLM_TEMPERATURE
    max_tokens: int = settings.LITELLM_MAX_TOKENS
    api_key: Optional[str] = settings.LITELLM_API_KEY
    api_base: Optional[str] = settings.LITELLM_BASE_URL
    
    # 实现必要的方法
    @property
    def _llm_type(self) -> str:
        """返回模型类型。"""
        return "litellm-chat"
    
    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        """生成聊天响应。"""
        # 实现逻辑...
    
    async def _agenerate(self, messages, stop=None, run_manager=None, **kwargs):
        """异步生成聊天响应。"""
        # 实现逻辑...
```

### 3. 实现消息格式转换

在模型类中实现消息格式转换方法，确保 LangChain 和 LiteLLM 之间的消息格式兼容：

```python
def _convert_message_to_litellm_format(self, message: BaseMessage) -> Dict[str, Any]:
    """将 LangChain 消息转换为 LiteLLM 格式。"""
    if isinstance(message, SystemMessage):
        return {"role": "system", "content": message.content}
    elif isinstance(message, HumanMessage):
        return {"role": "user", "content": message.content}
    # 处理其他消息类型...
```

### 4. 创建模型工厂

在 `chat_model_factory.py` 中实现模型工厂函数，提供不同配置的模型实例：

```python
def get_chat_model(
    model_name: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    **kwargs
) -> BaseChatModel:
    """获取配置的聊天模型实例。"""
    # 实现逻辑...
    return LiteLLMChatModel(...)

def get_planner_model() -> BaseChatModel:
    """获取适用于规划任务的模型。"""
    return get_chat_model(temperature=0.0)

def get_executor_model() -> BaseChatModel:
    """获取适用于执行任务的模型。"""
    return get_chat_model(temperature=0.2)
```

### 5. 实现代理工具

在 `agent_utils.py` 中实现创建和使用 LangChain 代理的辅助函数：

```python
def create_agent_executor(
    tools: List[BaseTool],
    llm: Optional[BaseLanguageModel] = None,
    system_message: Optional[str] = None,
    verbose: bool = False
) -> AgentExecutor:
    """创建 LangChain 代理执行器。"""
    # 实现逻辑...
    return AgentExecutor(...)

def convert_to_langchain_tools(tools: List[Dict]) -> List[BaseTool]:
    """将内部工具格式转换为 LangChain 工具实例。"""
    # 实现逻辑...
```

### 6. 配置状态管理

使用 LangGraph 的 `StateGraph` 进行状态管理，定义明确的状态类型：

```python
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    """代理图的状态模式。"""
    messages: List[Any]  # 对话中的消息

class AgentContext(TypedDict):
    """代理图的运行时上下文。"""
    conversation_id: Optional[str]  # 可选的对话 ID
    event_callback: Optional[Callable[[Event], Any]]  # 事件回调
```

## 使用示例

### 创建和使用聊天模型

```python
from backend.core.llm import get_chat_model

# 创建默认配置模型
chat_model = get_chat_model()

# 创建自定义配置模型
custom_model = get_chat_model(
    model_name="gpt-4",
    temperature=0.5,
    max_tokens=2000
)

# 生成响应
from langchain_core.messages import HumanMessage
messages = [HumanMessage(content="你好，请告诉我今天的天气")]
response = await chat_model._agenerate(messages)
print(response.generations[0].message.content)
```

### 创建和使用代理执行器

```python
from backend.core.llm.agent_utils import create_agent_executor
from backend.core.tools.registry import get_tools

# 获取工具
tools = get_tools(tags=["weather"])

# 创建代理执行器
agent_executor = create_agent_executor(tools, verbose=True)

# 执行查询
result = await agent_executor.ainvoke({"input": "北京今天的天气怎么样？"})
print(result["output"])
```

## 使用工作流编排器

```python
from backend.core.graph.flow_orchestrator import FlowOrchestrator

# 创建流程编排器
orchestrator = FlowOrchestrator(
    filter_strategy="default",
    tool_tags=["weather"]
)

# 使用编排器处理查询
result = await orchestrator.invoke(
    input_message="北京今天的天气怎么样？",
    conversation_id="user123"
)

# 使用流式响应
async for event in orchestrator.stream_invoke(
    input_message="上海今天的天气怎么样？",
    conversation_id="user123"
):
    print(f"Event type: {event.type}")
    if event.type == "final":
        print(f"Final response: {event.response}")
```

## 最佳实践

### 1. 状态管理

* 使用 TypedDict 或 Pydantic 模型定义明确的状态结构
* 避免使用全局状态变量
* 参数显式传递，而非隐式访问
* 使用 `StateGraph` 代替 `MessageGraph` 进行状态管理

### 2. 消息格式转换

* 在系统边界进行消息格式转换
* 内部保持一致的消息格式
* 集中处理消息转换逻辑
* 避免重复的消息格式转换

### 3. 错误处理

* 使用结构化异常处理
* 捕获特定类型的异常
* 提供有意义的错误消息
* 记录详细的错误信息用于调试

### 4. 异步处理

* 一致使用异步方法进行 I/O 操作
* 避免在异步代码中使用阻塞调用
* 适当使用 `asyncio.gather` 并行执行任务
* 实现适当的超时和取消机制

## 常见问题与解决方案

### 1. 状态管理错误

**问题**：使用 `'list' object has no attribute 'update'` 错误。

**解决方案**：检查返回的状态类型，确保始终返回符合 `AgentState` 类型定义的对象。不要使用类变量存储状态。

### 2. 消息格式不一致

**问题**：不同组件使用不同的消息格式，导致转换错误。

**解决方案**：使用 `message_formatter` 统一消息格式，在系统边界处理格式转换。

### 3. LiteLLM API 异常

**问题**：调用 LiteLLM 时遇到 API 异常。

**解决方案**：实现详细的异常处理，捕获 `litellm.exceptions` 中的特定异常类型，并提供适当的错误恢复机制。

## 测试

为确保集成正常工作，应创建以下类型的测试：

### 单元测试

```python
def test_litellm_chat_model():
    """测试 LiteLLM 聊天模型。"""
    chat_model = get_chat_model()
    messages = [HumanMessage(content="Hello")]
    response = chat_model._generate(messages)
    assert response.generations
    assert response.generations[0].message.content

def test_message_conversion():
    """测试消息格式转换。"""
    human_message = HumanMessage(content="Hello")
    litellm_format = chat_model._convert_message_to_litellm_format(human_message)
    assert litellm_format["role"] == "user"
    assert litellm_format["content"] == "Hello"
```

### 集成测试

```python
async def test_agent_workflow():
    """测试完整的代理工作流。"""
    orchestrator = FlowOrchestrator(tool_tags=["weather"])
    result = await orchestrator.invoke("北京天气怎么样？")
    assert "messages" in result
    assert len(result["messages"]) > 1
```

## 结论

通过正确集成 LangChain 和 LiteLLM，我们可以创建灵活、强大的智能代理系统，同时保持代码的清晰结构和可维护性。遵循本指南中的最佳实践，可以避免常见的集成错误并实现高效的开发流程。