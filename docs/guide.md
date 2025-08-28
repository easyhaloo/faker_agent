# Faker Agent 使用指南

## 简介

Faker Agent 是一个模块化、可扩展的智能体系统，支持多种协议和工具过滤策略。本指南将帮助您了解如何使用和扩展 Faker Agent。

## 安装与启动

### 环境要求
- Python 3.9+
- Node.js 16+

### 后端安装

```bash
# 克隆仓库
git clone https://github.com/yourusername/faker_agent.git
cd faker_agent

# 使用 uv 创建虚拟环境（Windows）
setup_uv.bat

# 使用 uv 创建虚拟环境（Linux/Mac）
./start_dev.sh setup

# 创建 .env 文件
cp backend/.env.example backend/.env
# 编辑 .env 添加 API 密钥
```

### 前端安装

```bash
cd frontend
npm install
```

### 启动服务

```bash
# 启动后端（从项目根目录）
cd backend
uvicorn main:app --reload
# 后端地址: http://localhost:8000

# 启动前端（从项目根目录）
cd frontend
npm run dev
# 前端地址: http://localhost:5173
```

## 使用 API

### HTTP 请求示例

```bash
curl -X POST http://localhost:8000/api/agent/v1/respond \
  -H "Content-Type: application/json" \
  -d '{
    "input": "北京的天气怎么样？",
    "protocol": "http",
    "mode": "sync"
  }'
```

### SSE 流式请求

```javascript
// 前端 JavaScript 示例
const eventSource = new EventSource(
  "/api/agent/v1/respond?protocol=sse&mode=stream"
);

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
  
  // 根据事件类型处理数据
  if (data.type === "tool_call_start") {
    console.log("开始调用工具:", data.tool_name);
  } else if (data.type === "tool_call_result") {
    console.log("工具调用结果:", data.result);
  } else if (data.type === "final") {
    console.log("最终响应:", data.response);
    eventSource.close();
  }
};

// 发送请求
fetch("/api/agent/v1/respond", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    input: "北京的天气怎么样？",
    protocol: "sse",
    mode: "stream"
  })
});
```

### WebSocket 示例

```javascript
// 前端 JavaScript 示例
const socket = new WebSocket("ws://localhost:8000/api/agent/v1/ws");

socket.onopen = () => {
  console.log("WebSocket 连接已建立");
  
  // 发送请求
  socket.send(JSON.stringify({
    input: "北京的天气怎么样？",
    tool_tags: ["weather"]
  }));
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
  
  // 根据事件类型处理数据
  if (data.type === "final") {
    console.log("最终响应:", data.response);
    socket.close();
  }
};
```

## 过滤工具

您可以使用 `filter_strategy` 和 `tool_tags` 参数过滤工具：

```json
{
  "input": "北京的天气怎么样？",
  "protocol": "http",
  "filter_strategy": "threshold_5",
  "tool_tags": ["weather"]
}
```

可用的过滤策略：
- `threshold_5`: 限制工具数量为 5 个
- `threshold_10`: 限制工具数量为 10 个
- `priority`: 按优先级排序，取前 5 个工具
- 您也可以通过 `/api/agent/v1/strategies` 获取所有可用策略

## 扩展 Faker Agent

### 创建新工具

1. 在 `backend/modules` 目录下创建新模块
2. 创建工具类继承 `BaseTool`
3. 实现 `run` 方法和定义工具元数据

```python
from backend.core.registry.base_registry import BaseTool, registry

class MyNewTool(BaseTool):
    """自定义工具示例"""
    
    name = "my_new_tool"
    description = "这是一个自定义工具"
    tags = ["custom", "example"]
    priority = 5
    parameters = [
        {
            "name": "param1",
            "type": "string",
            "description": "参数1描述",
            "required": True
        }
    ]
    
    async def run(self, param1: str, **kwargs) -> dict:
        """运行工具"""
        result = f"处理参数: {param1}"
        return {
            "result": result
        }

# 注册工具
registry.register_tool(MyNewTool)
```

### 创建新过滤策略

```python
from backend.core.filters.tool_filter_strategy import ToolFilterStrategy
from backend.core.registry.base_registry import BaseTool
from backend.core.filters.filter_manager import filter_manager

class MyCustomFilter(ToolFilterStrategy):
    """自定义过滤策略"""
    
    def __init__(self, keyword: str):
        self.keyword = keyword
    
    def filter(self, tools: List[BaseTool]) -> List[BaseTool]:
        """按关键词过滤工具"""
        return [
            tool for tool in tools 
            if self.keyword.lower() in tool.name.lower() or 
               self.keyword.lower() in tool.description.lower()
        ]

# 注册策略
filter_manager.register_strategy("keyword_filter", MyCustomFilter("weather"))
```

### 创建新协议处理器

```python
from backend.core.protocol.base_protocol import BaseProtocol
from backend.core.graph.event_types import Event
from backend.core.protocol.protocol_factory import protocol_factory

class MyCustomProtocol(BaseProtocol):
    """自定义协议处理器"""
    
    async def handle_events(self, events, **kwargs):
        """处理事件流"""
        # 实现自定义处理逻辑
        pass
    
    async def format_event(self, event: Event) -> Any:
        """格式化事件"""
        # 实现自定义格式化逻辑
        pass
    
    async def format_error(self, error: str, details: Optional[Dict[str, Any]] = None) -> Any:
        """格式化错误"""
        # 实现自定义错误格式化逻辑
        pass

# 注册协议处理器
protocol_factory.register_protocol("custom", MyCustomProtocol())
```

## 故障排除

### 常见问题

1. **API 密钥未设置**
   - 确保在 `.env` 文件中设置了 `LITELLM_API_KEY` 和其他必要的 API 密钥

2. **工具未注册**
   - 检查工具是否已在模块的 `__init__.py` 中正确导入和注册

3. **协议不匹配**
   - 确保请求中的 `protocol` 与请求方式匹配（例如，WebSocket 请求应使用 WebSocket 协议）

### 调试提示

1. 查看 FastAPI 日志获取详细错误信息
2. 使用 `/api/system/status` 检查系统状态
3. 使用 `/api/tools` 检查已注册工具列表