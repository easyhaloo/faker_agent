# 通用智能体开发指南更新 - 代码重构与规范

## 1. 代码重构说明

本次重构主要针对系统中的天气功能进行了集中化和标准化处理，解决了以下问题：

1. 消除了代码重复：移除了多处相似的天气查询检测和响应生成逻辑
2. 统一了功能实现：所有天气相关功能都集中在专门的工具模块中
3. 提高了可维护性：更改和扩展天气功能只需修改一处代码
4. 增强了一致性：所有组件通过相同的接口访问天气功能

## 2. 重构内容详细说明

### 新增集中式天气工具模块

创建了 `backend/core/utils/weather_utils.py` 模块，集中处理天气相关功能：

- `is_weather_query()`: 统一判断是否为天气查询
- `extract_city_from_query()`: 从查询中提取城市信息
- `get_weather_response()`: 生成标准化天气响应
- `get_sse_weather_event()`: 生成 SSE 格式天气事件

### 更新现有代码

- `agent.py`: 使用集中式工具进行天气检测和响应
- `flow_orchestrator.py`: 统一天气查询判断逻辑
- `agent_routes.py`: 使用集中式工具生成 SSE 响应

## 3. 代码开发规范更新

为确保代码质量和一致性，所有开发者必须遵循以下规范：

### 单一实现原则

**每种功能只应有一个权威实现版本**

- ✅ **正确**: 创建集中式工具模块，由所有组件共同调用
- ❌ **错误**: 在多个文件中重复实现相似功能

```python
# ✅ 正确方式：集中式实现
# 在 utils/weather_utils.py 中
def is_weather_query(query: str) -> bool:
    return "天气" in query or "weather" in query.lower()

# 在其他文件中
from backend.core.utils.weather_utils import is_weather_query
if is_weather_query(query):
    # 处理天气查询
```

```python
# ❌ 错误方式：重复实现
# 在 agent.py 中
is_weather_query = "天气" in query or "weather" in query.lower()

# 在 routes.py 中
is_weather_query = "天气" in input or "weather" in input.lower()
```

### 功能增强策略

**增强现有功能而非重新实现**

1. 首先检查是否已有相关功能的实现
2. 如有，在现有实现基础上进行增强
3. 如需添加新特性，扩展现有实现而非创建新实现
4. 删除被替代的旧实现，保持代码库干净

### 模块组织规范

1. 工具函数应使用清晰的动词前缀:
   - `is_*`: 判断或检查（如 `is_weather_query`）
   - `get_*`: 获取或生成数据（如 `get_weather_response`）
   - `extract_*`: 从数据中提取信息（如 `extract_city_from_query`）
   - `format_*`: 格式化数据（如 `format_weather_data`）

2. 工具模块应按功能领域组织:
   - `*_utils.py`: 通用工具函数（如 `weather_utils.py`）
   - `*_helpers.py`: 辅助函数（如 `string_helpers.py`）
   - `*_manager.py`: 管理类（如 `connection_manager.py`）

3. 集中式工具模块命名规则:
   - 使用具体功能领域作为前缀（如 `weather_*`）
   - 使用 `utils` 后缀表示通用工具集合
   - 使用 `service` 后缀表示带状态的服务类

## 4. 重构时机判断

遇到以下情况时，应考虑进行重构：

1. **发现多处相似代码**：相同功能在多个文件中实现
2. **修改需要同步多处**：一个逻辑变更需要修改多个文件
3. **功能分散难以维护**：相关功能分散在不同模块中
4. **新增功能与现有重叠**：要添加的功能与现有功能有重叠

## 5. 重构流程指南

1. **分析现有实现**：识别所有相关代码的位置和功能
2. **确定最佳实现**：选择最完善的实现作为基础
3. **创建集中式模块**：将功能提取到专门的工具模块
4. **更新调用代码**：修改所有调用点使用新的集中式实现
5. **删除冗余实现**：在确认新实现正常工作后移除旧代码
6. **更新文档**：在 `docs/progress` 记录重构内容和原因

## 6. 特定功能实现指南

### 天气功能实现规范

- 天气查询检测必须使用 `weather_utils.is_weather_query()`
- 天气响应生成必须使用 `weather_utils.get_weather_response()`
- SSE 事件生成必须使用 `weather_utils.get_sse_weather_event()`
- 城市提取必须使用 `weather_utils.extract_city_from_query()`

### 未来扩展计划

1. **参数提取增强**：使用 LLM 提取更复杂的天气查询参数
2. **多语言支持**：扩展天气查询检测支持更多语言
3. **实时天气 API**：集成真实的天气 API 服务
4. **用户偏好记忆**：添加对用户位置偏好的记忆功能

## 7. 文档要求

所有代码更改必须遵循以下文档规范：

1. **模块级文档**：每个模块必须包含说明其目的和用途的文档
2. **函数级文档**：每个函数必须包含参数和返回值说明
3. **更改记录**：重要更改应记录在 `docs/progress/YYYY-MM-DD.md` 中
4. **代码注释**：复杂逻辑必须包含解释性注释

## 8. 重构前后对比示例

### 重构前 (分散实现)

```python
# 在 agent.py 中
is_weather_query = False
chinese_weather = "天气" in query
english_weather = "weather" in query.lower()
if chinese_weather or english_weather:
    is_weather_query = True

# 在 agent_routes.py 中
is_weather_query = "天气" in input or "weather" in input.lower()

# 在 flow_orchestrator.py 中
if "weather" in str(messages).lower() or "天气" in str(messages).lower():
    final_response = "请稍等，我来为您查询天气信息。"
```

### 重构后 (集中实现)

```python
# 在 weather_utils.py 中
def is_weather_query(query: str) -> bool:
    """
    判断是否为天气查询.
    
    Args:
        query: 用户输入的查询
        
    Returns:
        是否为天气查询
    """
    if isinstance(query, bytes):
        try:
            query = query.decode('utf-8')
        except:
            query = str(query)
    
    return "天气" in query or "weather" in query.lower()

# 在其他模块中统一使用
from backend.core.utils.weather_utils import is_weather_query

if is_weather_query(query):
    # 处理天气查询
```

## 9. 结论

通过本次重构，我们实现了代码的集中化和标准化，提高了系统的可维护性和扩展性。所有开发者应遵循上述规范，确保代码库的一致性和质量。

---

✨ **核心原则**
* 每种功能只有一个权威实现
* 优先扩展现有功能而非重新实现
* 相关功能应集中在专门的工具模块中
* 删除被替代的旧实现，保持代码库干净
* 更新文档，记录重要更改