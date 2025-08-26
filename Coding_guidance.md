
# 通用智能体开发蓝图（前后端分离版）

## 1. 项目目标

构建一个 **通用智能体（类似 Manus.ai）**，特性：

* 前后端分离：**前端 Web (React)**，**后端 Python**
* 核心智能体位于后端，由前端调用
* 模块化 + 插件化，方便扩展
* 渐进式迭代：通过 **能力声明 / 问题声明** 驱动开发

---

## 2. 技术栈

### 前端（Web）

* **框架**：React (可选 Next.js)
* **状态管理**：Redux Toolkit / Zustand
* **UI 框架**：TailwindCSS + shadcn/ui
* **构建工具**：Vite / Next.js 内置工具
* **职责**：

  * 提供用户交互界面
  * 可视化任务管理、插件管理、日志面板
  * 调用后端 API

### 后端（Python）

* **框架**：FastAPI（推荐，支持异步 + OpenAPI）
* **核心模块**：

  * Planner（任务分解）
  * Executor（动作执行，工具调用）
  * Memory（短期/长期记忆，支持 Redis/向量数据库）
  * Registry（工具与插件注册中心）
* **职责**：

  * 提供智能体服务与 API
  * 处理前端请求
  * 统一管理插件、工具与执行逻辑

---

## 3. 项目架构

```text
project-root/
├── backend/ (Python)          # 智能体核心 + API 服务
│   ├── core/                  # 核心智能体逻辑
│   │   ├── planner/           # 任务分解
│   │   ├── executor/          # 执行器
│   │   ├── memory/            # 记忆
│   │   └── registry/          # 插件/工具注册
│   ├── api/                   # FastAPI 路由
│   ├── modules/               # 后端扩展模块（可插拔）
│   └── main.py                # FastAPI 入口
│
├── frontend/ (React)          # Web 前端
│   ├── features/              # 功能模块（任务面板、插件管理、日志）
│   ├── components/            # 原子化 UI 组件
│   ├── services/              # API 调用层
│   └── App.jsx                # React 入口
│
├── docs/                      # 开发文档
│   ├── progress/              # 每次迭代的进度记录
│   └── roadmap.md             # 长期计划
└── ...
```

---

## 4. 模块说明（抽象级别）

### 后端（Python）

* **Planner**

  * 输入：自然语言任务
  * 输出：任务计划（步骤流）

* **Executor**

  * 输入：任务步骤
  * 输出：执行结果
  * 特性：可调用 API、本地函数、外部插件

* **Memory**

  * 输入：上下文、历史
  * 输出：可查询/持久化的记忆
  * 可选实现：Redis、SQLite、向量数据库

* **Registry**

  * 职责：统一管理工具与插件
  * 接口：注册 / 发现 / 调用

### 前端（Web）

* **Features**

  * 功能区块（任务面板、日志监控、插件管理）
* **Components**

  * 原子 UI 组件（按钮、表单、对话框）
* **Services**

  * 调用后端 API（任务提交、结果查询）

---

## 5. 开发流程（渐进式迭代）

1. **初始化**

   * 定义后端核心接口（Planner/Executor/Memory/Registry）
   * 搭建前端 React 应用框架
   * 建立前后端 API 契约

2. **迭代循环**

   * 写入 **能力声明**（新功能需求）
   * 写入 **问题声明**（需要修复的 Bug）
   * Claude Code 依据声明生成或修改代码
   * 更新 `docs/progress/日期.md`

---

## 6. 进度文档模板

```markdown
# 进度报告 – YYYY-MM-DD

## 新能力声明
- [Backend] Memory 模块支持 Redis 存储
- [Frontend] 新增任务进度面板 (TaskPanel)

## 问题声明
- [Backend] Executor 执行未捕获异常
- [Frontend] API 服务调用缺少错误提示

## 下一步计划
- [Backend] 定义插件接口 (Registry)
- [Frontend] 集成 WebSocket 用于实时任务状态
```

---

## 7. Claude Code 使用示例

* **新增能力**

  > “根据 `能力声明：Memory 模块支持 Redis 存储`，请在 `backend/core/memory/redis_memory.py` 生成实现，并更新 Registry 以支持注册。”

* **修复问题**

  > “根据 `问题声明：Executor 执行未捕获异常`，请修改 `backend/core/executor/base_executor.py`，增加 try/except 与日志记录。”

---

✨ 总结

* 架构：**前端 Web (React) + 后端 Python (FastAPI)**
* 后端提供智能体核心，前端作为管理与交互界面
* 模块化、可插拔、渐进式迭代
* 开发流程：**能力声明 + 问题声明 → Claude Code 生成实现 → 文档更新**


