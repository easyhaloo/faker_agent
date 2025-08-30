# LangChain 和 LiteLLM 集成错误避免清单

## 开发前准备

- [ ] 阅读并理解 LangChain 和 LiteLLM 的最新文档
- [ ] 确认项目依赖版本兼容性
  - langchain
  - langchain-core
  - litellm
  - langgraph
- [ ] 检查环境变量配置
  - LITELLM_API_KEY
  - LITELLM_MODEL
  - LITELLM_BASE_URL (如果使用自定义端点)
- [ ] 规划状态管理策略
- [ ] 准备测试环境和 mock 机制

## 编码阶段

### 状态管理

- [ ] 避免使用全局状态或类变量存储状态
  - 不使用 `_current_additional_fields` 等静态类变量
- [ ] 定义明确的状态类型
  ```python
  class AgentState(TypedDict):
      messages: List[Any]  # 对话中的消息
  ```
- [ ] 使用 `StateGraph` 代替 `MessageGraph`
  ```python
  graph = StateGraph(state_schema=AgentState, context_schema=AgentContext)
  ```
- [ ] 参数显式传递，而非隐式访问
  ```python
  # 正确: 参数显式传递
  def process_node(state: AgentState, context: AgentContext) -> Dict[str, Any]:
      # 处理逻辑...
      return updated_state
      
  # 错误: 通过全局变量或类变量访问状态
  def process_node():
      # 访问全局状态...
      global_state.update(...)
  ```

### 消息处理

- [ ] 统一消息格式，内部一致使用 LangChain 消息对象
  - `SystemMessage`
  - `HumanMessage`
  - `AIMessage`
  - `ToolMessage`
- [ ] 在系统边界处理消息格式转换
  ```python
  # 在 API 层将字典转换为 LangChain 格式
  langchain_messages = message_formatter.prepare_langchain_messages(dict_messages)
  
  # 在 LLM 调用层将 LangChain 格式转换为 LiteLLM 格式
  litellm_messages = self._convert_messages_to_litellm_format(langchain_messages)
  ```
- [ ] 避免重复的消息格式转换
  - 转换一次，多次使用
  - 检查是否已经是目标格式
- [ ] 验证消息格式的正确性
  ```python
  if not isinstance(message, dict) or "role" not in message or "content" not in message:
      # 处理无效格式...
  ```

### 错误处理

- [ ] 实现结构化异常处理
  ```python
  try:
      # 调用 LiteLLM
      response = await litellm.acompletion(**params)
      # 处理响应...
  except litellm.exceptions.AuthenticationError as e:
      logger.error(f"身份验证错误: {e}")
      # 创建适当的错误响应...
  except litellm.exceptions.RateLimitError as e:
      logger.error(f"速率限制错误: {e}")
      # 创建适当的错误响应...
  except Exception as e:
      logger.error(f"调用 LLM 时出错: {e}")
      # 创建适当的错误响应...
  ```
- [ ] 使用标准日志级别
  - INFO: 普通操作信息
  - WARNING: 潜在问题警告
  - ERROR: 操作失败错误
  - DEBUG: 调试信息
- [ ] 确保工具调用中的错误不会中断整个流程
  ```python
  try:
      result = await matching_tool.ainvoke(tool_args)
  except Exception as e:
      result = f"Error executing tool: {str(e)}"
      # 继续处理...
  ```

### 接口设计

- [ ] 为方法提供明确的参数和返回类型注释
  ```python
  async def invoke(
      self,
      input_message: str,
      conversation_id: Optional[str] = None,
      event_callback: Optional[Callable[[Event], None]] = None
  ) -> Dict[str, Any]:
      """方法文档字符串..."""
  ```
- [ ] 遵循"调用者负责"原则传递参数
  - 由调用者负责提供正确格式的参数
  - 在被调用方法中添加验证和错误处理
- [ ] 每个方法只负责一个明确的任务
  - 消息转换
  - LLM 调用
  - 工具执行
- [ ] 为每个公共方法提供清晰的文档字符串

### 异步处理

- [ ] 一致使用异步方法进行 I/O 操作
  ```python
  # 正确: 使用异步方法
  async def _agenerate(self, messages, **kwargs):
      response = await litellm.acompletion(**params)
      
  # 错误: 在异步方法中使用同步调用
  async def _agenerate(self, messages, **kwargs):
      response = litellm.completion(**params)  # 阻塞调用
  ```
- [ ] 避免在异步代码中使用阻塞调用
- [ ] 使用 `asyncio.gather` 并行执行多个任务
  ```python
  results = await asyncio.gather(
      tool1.ainvoke(args1),
      tool2.ainvoke(args2)
  )
  ```
- [ ] 实现适当的超时和取消机制
  ```python
  try:
      async with asyncio.timeout(10):  # 10秒超时
          result = await litellm.acompletion(**params)
  except asyncio.TimeoutError:
      # 处理超时...
  ```

## 测试阶段

- [ ] 实现 LiteLLM 响应的 mock
  ```python
  class MockLiteLLMChatModel(LiteLLMChatModel):
      async def _agenerate(self, messages, **kwargs):
          # 返回模拟响应...
  ```
- [ ] 为每个组件编写独立的单元测试
  - 测试消息转换函数
  - 测试工具执行流程
  - 测试错误处理
- [ ] 测试各种错误情况和边界条件
  - 空消息列表
  - 格式不正确的消息
  - API 异常
  - 工具调用错误
- [ ] 验证状态管理在复杂场景下的正确性
  - 多轮对话
  - 嵌套工具调用
  - 并发请求

## 部署前检查

- [ ] 检查所有依赖版本的兼容性
  ```bash
  pip freeze | grep -E 'langchain|litellm|langgraph'
  ```
- [ ] 验证环境变量和配置的正确性
  - 检查 `.env` 文件
  - 确认 API 密钥和端点配置
- [ ] 执行集成测试验证完整流程
  - 从用户输入到最终响应的端到端测试
- [ ] 检查错误处理和恢复机制
  - 验证系统在各种错误情况下的行为
- [ ] 确保文档与实际实现一致
  - 更新 API 文档
  - 更新使用示例

## 常见错误和解决方案

### 1. `'list' object has no attribute 'update'` 错误

- **原因**: 尝试对列表使用字典方法
- **解决方案**: 
  - 检查返回的状态类型
  - 确保始终返回符合 `AgentState` 类型定义的对象
  - 不要使用 `_current_additional_fields` 类变量

### 2. `Module not found` 错误

- **原因**: 缺少必要的依赖或依赖版本不匹配
- **解决方案**:
  - 检查 `requirements.txt` 中是否包含所有必要依赖
  - 检查导入路径是否正确
  - 使用 `pip install -e .` 安装开发版本

### 3. 消息格式不一致错误

- **原因**: 不同组件使用不同的消息格式
- **解决方案**:
  - 使用 `message_formatter` 统一消息格式
  - 在系统边界处理格式转换
  - 避免在代码中混合使用不同的消息格式

### 4. LiteLLM API 异常

- **原因**: API 密钥无效、网络问题或服务端错误
- **解决方案**:
  - 实现详细的异常处理
  - 捕获 `litellm.exceptions` 中的特定异常类型
  - 提供适当的错误恢复机制和用户友好的错误消息

## 性能优化检查

- [ ] 缓存 LLM 响应减少 API 调用
  ```python
  from langchain.cache import InMemoryCache
  langchain.llm_cache = InMemoryCache()
  ```
- [ ] 批处理减少 API 调用次数
  ```python
  responses = await litellm.abatch_completion([
      {"messages": messages1},
      {"messages": messages2}
  ])
  ```
- [ ] 优化消息格式转换逻辑
  - 减少不必要的转换
  - 在关键路径上使用高效算法
- [ ] 使用 asyncio 并发处理多个任务

## 最终检查

- [ ] 代码符合项目编码规范
- [ ] 所有测试通过
- [ ] 文档完整并与实现一致
- [ ] 没有遗留 TODO 或 FIXME 标记
- [ ] 性能满足需求