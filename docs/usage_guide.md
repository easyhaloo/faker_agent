# 使用文档

本文档详细说明了如何搭建环境、启动系统以及访问Faker Agent的各项功能。

## 目录

1. [环境搭建](#环境搭建)
2. [后端启动](#后端启动)
3. [前端启动](#前端启动)
4. [系统访问](#系统访问)
5. [API接口说明](#api接口说明)
6. [功能使用指南](#功能使用指南)

## 环境搭建

### 后端环境准备

1. 安装Python 3.8或更高版本
2. 安装UV包管理器：
   ```bash
   pip install uv
   ```
3. 创建虚拟环境并安装依赖：
   ```bash
   cd backend
   uv venv
   uv pip install -r requirements.txt
   ```
4. 配置环境变量：
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入必要的API密钥
   ```

### 前端环境准备

1. 安装Node.js 16或更高版本
2. 安装npm依赖：
   ```bash
   cd frontend
   npm install
   ```

### 数据库准备（可选）

如果要使用Redis存储功能，需要安装并启动Redis服务器：
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Windows (使用WSL或Docker)
```

启动Redis服务器：
```bash
redis-server
```

## 后端启动

在项目根目录下执行以下命令启动后端服务：

```bash
cd backend
uvicorn main:app --reload
```

默认情况下，后端服务将在 `http://localhost:8000` 上运行。

### 后端配置

后端配置项位于 `backend/.env` 文件中，主要包括：
- `LITELLM_API_KEY`: LiteLLM API密钥
- `WEATHER_API_KEY`: 天气API密钥（可选）
- `REDIS_HOST`: Redis主机地址（默认: localhost）
- `REDIS_PORT`: Redis端口（默认: 6379）

## 前端启动

在项目根目录下执行以下命令启动前端开发服务器：

```bash
cd frontend
npm run dev
```

默认情况下，前端开发服务器将在 `http://localhost:5173` 上运行。

## 系统访问

启动后端和前端服务后，可以通过以下方式访问系统：

1. **Web界面访问**：
   打开浏览器访问 `http://localhost:5173`

2. **API接口访问**：
   直接访问后端API接口 `http://localhost:8000`

3. **API文档访问**：
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## API接口说明

### 核心接口

1. **提交任务**：
   - URL: `POST /api/agent/task`
   - 功能: 提交任务给智能体处理
   - 参数: `{ "query": "你的问题" }`

2. **异步提交任务**：
   - URL: `POST /api/agent/task/async`
   - 功能: 异步提交任务，支持实时状态更新
   - 参数: `{ "query": "你的问题" }`

3. **获取任务状态**：
   - URL: `GET /api/agent/task/{task_id}`
   - 功能: 获取指定任务的当前状态

4. **实时任务状态流**：
   - URL: `GET /api/agent/task/{task_id}/stream`
   - 功能: 通过Server-Sent Events实时获取任务进度

5. **列出可用工具**：
   - URL: `GET /api/tools`
   - 功能: 获取所有可用工具列表

6. **系统状态**：
   - URL: `GET /api/system/status`
   - 功能: 获取系统运行状态

### 模块接口

1. **天气查询**：
   - URL: `GET /api/weather/{city}`
   - 功能: 直接查询指定城市的天气信息

## 功能使用指南

### 1. 智能体交互

在Web界面或通过API向智能体提问，例如：
- "今天北京的天气怎么样？"
- "计算123乘以456等于多少？"
- "搜索人工智能的最新发展"

智能体会根据问题自动选择合适的工具进行处理。

### 2. 实时任务跟踪

使用异步任务接口可以实时跟踪任务进度：
1. 提交异步任务获取任务ID
2. 通过任务ID查询任务状态
3. 或者通过SSE流式接口实时接收进度更新

### 3. 工具使用

系统内置以下工具：
- **计算器**: 支持基本数学运算
- **网络搜索**: 通过DuckDuckGo搜索信息
- **天气查询**: 查询全球城市天气信息

### 4. 对话历史

系统会自动保存对话历史，支持：
- 基于内存的临时存储
- 基于Redis的持久化存储（需要配置Redis）

## 故障排除

### 常见问题

1. **后端无法启动**：
   - 检查端口是否被占用
   - 确认所有依赖已正确安装
   - 检查环境变量配置

2. **前端无法连接后端**：
   - 确认后端服务已启动
   - 检查CORS配置
   - 确认网络连接正常

3. **Redis连接失败**：
   - 确认Redis服务已启动
   - 检查Redis配置信息
   - 确认防火墙设置

### 日志查看

- 后端日志: 在终端中查看uvicorn输出
- 前端日志: 在浏览器开发者工具控制台中查看

## 系统维护

### 代码格式化

后端代码格式化：
```bash
cd backend
uv run black .
uv run isort .
```

前端代码格式化：
```bash
cd frontend
npm run format
```

### 测试运行

运行所有测试：
```bash
cd tests
python -m pytest
```

运行特定测试：
```bash
python test_redis_memory.py
python test_calculator.py
python test_web_search.py
python test_api_routes.py
python test_integration.py
```