# 🔹生成任务：类 ChatGPT 的多轮对话 & 记忆管理（前后端一体实现）

## 🎯 目标产物（交付清单）

1. **多会话对话系统（前端 + 后端）**：支持创建/重命名/切换/删除会话、消息流、打字中状态、失败重试。
2. **记忆系统（三层）**：

   * **短期（工作窗 / Context Window）**：最近 N 条消息 + 可选"滚动摘要"。
   * **会话级长期（Episodic Memory）**：对单会话的要点（目标/约束/术语）。
   * **全局长期（Profile/Preference）**：用户偏好、风格、常用参数；支持"项目级（Project-only）"作用域。([OpenAI][1], [TechRadar][7])
3. **记忆读/写策略（Policy）** 与 **治理控制台**：开关、作用域选择（全局/项目/仅当前会话）、导出/清空、可审计日志。([OpenAI Help Center][2])
4. **工具/函数调用（Function Calling）**：检索(RAG)/搜索/代码执行等；稳健的工具选择与超时回退策略。([OpenAI平台][5], [OpenAI Cookbook][6])
5. **隐私与数据合规基线**：内置红线（敏感信息默认不持久化）、最小化存储、数据生命周期策略与审计。([Microsoft Learn][10])

---

## 🧱 架构蓝图（建议）

* **前端**：React + Tailwind + shadcn/ui + Zustand（会话/记忆可视化）+ Framer Motion（动效）。
* **后端**：FastAPI（REST）+ PostgreSQL（会话/消息/记忆表）+ 向量库（pgvector/Weaviate/Chroma 任选其一）+ 任务队列（RQ/Celery）处理长耗时工具。
* **模型接入**：按"消息数组 + 工具规范（OpenAI 样式函数调用）"组织提示；保留工具调用轨迹（traces）。([OpenAI平台][5])

---

## 🧠 记忆分层与策略（核心）

### 1) 短期记忆（Context Window）

* **输入规则**：

  * 采用「**消息滑窗 + 主题摘要**」混合：

    * 最近 **K** 条原文（如 12–30 条，视模型上下文长度）
    * 更早历史收敛为结构化"对话滚动摘要（rolling summary）"：

      * 结构：`{主题, 目标, 已做决定, 未决问题, 关键事实, 术语表}`
      * 每轮超过阈值（如新增 800 tokens）时刷新一次
* **清理规则**：移除重复/无关/寒暄，优先保留决定、约束、引用来源与数据口径。
* **失败保护**：若超长，则优先剔除多余工具日志与中间态，保留"指令/事实/结论"。
  （社区与经验做法广泛采用该思路以降低上下文成本与幻觉。([OpenAI 社区][11])）

### 2) 会话级长期记忆（Episodic）

* **写入触发**（任一命中则写入）：

  * 该会话的**持久目标/约束**（如"生成周报的格式、口径、口吻"）。
  * 多次重复出现且跨回合引用的信息（如"术语映射/关键人名/项目代号"）。
  * 模型或用户显式指令："请记住本会话的规则/模板"。
* **写入格式**（结构化，便于检索）：

  ```
  {conversation_id, keys:[{type, title, content, tags[], source_msg_id, created_at, expires_at?}]}
  ```
* **读取策略**：

  * 在会话首轮合成提示时做一次"语义检索（top-k=5）+ 规则白名单"注入。
  * 若冲突，以**最新**与**显式确认**的记忆为准；将冲突记录入审计日志。

### 3) 全局长期记忆（Profile/Preference）

* **作用域**：默认 **用户级全局**；支持切到 **项目级（Project-only）**，限制记忆只在该项目中生效（模仿 ChatGPT 的项目记忆开关）。([TechRadar][7])
* **写入触发**：

  * 明确偏好（写作语气/编程栈/输出格式/度量单位/语言）。
  * 明确的"从现在起""以后默认"等提示。
  * 需通过**敏感词过滤器**与**黑名单字段**（PII/健康/政治立场等）后才允许持久化（默认拒收）。([OpenAI Help Center][2], [Microsoft Learn][10])
* **读取策略**：

  * 合成系统提示（system）前拼装"偏好卡片（Preference Card）"，仅包含本轮任务相关条目（最多 5 条），避免过载。
* **项目切换逻辑**：

  * 若项目模式开启，优先注入项目记忆；全局记忆仅在不冲突时补充。([TechRadar][7])

---

## 🧩 工具/函数调用（Function Calling）策略

* **定义**：所有外部能力（搜索/RAG/计算/代码执行）均以"函数签名 + JSON 参数"暴露；模型选择是否调用。([OpenAI平台][5])
* **规模**：常见建议为**<100 个工具**、**每工具 <20 参数**的设置最稳妥；超出需做分组与工具候选筛选。([OpenAI Cookbook][6])
* **调用流程**：

  1. 合成提示（含短期上下文 + 命中的会话/全局记忆）
  2. 让模型决定是否调用工具（或多步调用）
  3. 记录调用轨迹（tool name, args, outputs, latency）
  4. 输出注入对话，并更新"滚动摘要"与会话关键事实
* **超时/降级**：单工具超时>10s → 返回"部分答案 + 延迟结果"策略；或改用缓存/轻量检索。

---

## 🔐 隐私与治理（必做）

* **记忆开关**：全局、项目、会话三级；可随时关闭与清空。用户可"临时对话"不引用记忆。([OpenAI Help Center][2])
* **数据最小化**：默认不保存敏感字段；显式"记住"也要二次确认（前端弹窗）。
* **生命周期**：给每条记忆可选 `expires_at`（默认 90 天）；到期自动归档/清除。
* **审计**：所有记忆写入/读取/覆盖/删除都有审计记录；可导出 JSON。
* **合规参考**：若使用 Azure OpenAI，沿用其数据处理与访问控制建议。([Microsoft Learn][12])

---

## 🗂️ 数据模型（建议表）

* `conversations(id, title, scope(project_id|null), created_at, updated_at)`
* `messages(id, conversation_id, role, content, tool_calls jsonb, created_at)`
* `mem_profile(id, user_id, scope(global|project), key, value, tags[], created_at, expires_at)`
* `mem_episode(id, conversation_id, type, title, content, tags[], source_msg_id, created_at, expires_at)`
* `summary(id, conversation_id, content, range_start_msg_id, range_end_msg_id, created_at)`
* `audit_memory(id, actor, action, target_id, target_type, details jsonb, created_at)`

---

## 🧪 读/写策略（可直接落地的伪代码）

### 写入（Memory Write Policy）

```
on_assistant_response(final_msg):
  facts = extract_facts(final_msg)            # 决定/约束/术语/引用数据口径
  if is_repeated(facts) or user_said("记住") or matches_long_term_pattern(facts):
      if scope == "project-only": write_to(mem_profile, scope=project)
      else: write_to(mem_profile, scope=global)
  epi = extract_session_goals_and_terms(final_msg)
  if epi: write_to(mem_episode, conversation_id=current)
```

### 读取（Memory Read Policy）

```
build_prompt(user_msg):
  recent = last_K_messages(conversation)
  rollup = get_latest_summary(conversation)
  epi_ctx = semantic_retrieve(mem_episode, user_msg, top_k=5)
  pref_ctx = scoped_preferences(user/project/global, filter_relevant(user_msg), limit=5)
  system = compose_system_instructions(pref_ctx, governance_rules)
  return {system, rollup, recent, epi_ctx}
```

### 滚动摘要（Rolling Summary）

```
if token_estimate(recent + summary) > THRESHOLD:
    new_summary = summarizer(recent, prev_summary)
    save(summary=new_summary, covers=recent_range)
    prune_old_messages()
```

---

## 🎨 前端交互与可视化（重点）

* **记忆中心**：

  * "全局/项目/会话"三列视图；每条记忆可编辑/删除/设定过期。
  * 开关：

    * [x] 使用全局记忆
    * [x] 使用项目记忆（选择项目）
    * [x] 在本会话写入记忆
    * [x] 临时会话（本轮不引用记忆）
* **会话标题来源**：首条用户消息前 20 字符；太短则"会话 - {日期}"；支持手动改名。
* **提示注入可见**（开发者模式）：展开可查看当前轮被注入的"偏好卡片/会话摘要/检索片段"，便于调试。
* **治理入口**：一键导出/清空记忆；查看审计日志。

---

## 🚦 验收标准（Checklist）

* [x] 同一用户可创建、切换、删除会话；标题自动/手动均可用
* [x] 模型在**关闭记忆**时不引用任何持久化信息（通过审计与提示可视化验证）([OpenAI Help Center][2])
* [x] 开启 **Project-only** 时，只注入项目作用域的偏好，且与全局不冲突或按优先级覆盖。([TechRadar][7])
* [x] 超长对话时，**滚动摘要**能维持回答一致性；token 占用稳定
* [ ] 工具调用在参数缺失/超时/失败时有兜底（重试或降级答案）([OpenAI平台][5])
* [x] 审计日志完整记录记忆读/写/删/覆盖事件，支持导出

---

## 🧭 实施顺序（建议两天分步）

**Day 1**：后端数据表 → 基础 API（会话/消息/记忆 CRUD）→ 滚动摘要服务 → 读/写策略落地
**Day 2**：前端 UI（对话区 + 记忆中心）→ 开关与作用域 → 提示可视化 → 工具调用与错误兜底 → 测试用例

---

## 🔌 关键 API（示例约定）

```
POST /conversations                -> {id, title, scope}
PUT  /conversations/{id}/title     -> {title}
GET  /conversations/{id}/messages  -> [ ... ]
POST /conversations/{id}/messages  -> {role:"user", content, options:{use_memory:bool, project_id?}}

GET  /memory/profile?scope=global|project&project_id? -> [...]
POST /memory/profile               -> {scope, key, value, tags, expires_at?}
GET  /memory/episode/{conversation_id}                -> [...]
POST /memory/episode               -> {conversation_id, type, title, content, tags, expires_at?}

GET  /audit/memory?conversation_id?&scope?            -> [...]
```







---

# 🔹Claude Code 多轮对话 & 记忆管理任务拆解

## 🟢 阶段 1：后端基础（FastAPI + DB）

### 1.1 项目初始化

* [x] 初始化 FastAPI 项目结构
* [x] 配置数据库（PostgreSQL 或 SQLite）
* [x] 建立基础依赖（SQLAlchemy, Alembic 迁移, UUID 生成工具）

### 1.2 数据模型（Models）

* [x] `Conversation` 表：`id, title, scope(project_id|null), created_at, updated_at`
* [x] `Message` 表：`id, conversation_id, role, content, tool_calls(jsonb), created_at`
* [x] `MemoryProfile`（全局/项目偏好）
* [x] `MemoryEpisode`（会话记忆）
* [x] `Summary`（滚动摘要）
* [x] `AuditMemory`（审计日志）

### 1.3 API 路由

* [x] `POST /conversations` 新建会话（默认标题"新会话"）
* [x] `PUT /conversations/{id}/title` 修改会话标题
* [x] `GET /conversations` 获取会话列表
* [x] `GET /conversations/{id}/messages` 获取消息列表
* [x] `POST /conversations/{id}/messages` 添加用户消息 → 触发 AI 回复
* [x] `DELETE /conversations/{id}` 删除会话

### 1.4 记忆 API

* [x] `GET /memory/profile?scope=` 获取偏好记忆
* [x] `POST /memory/profile` 写入偏好记忆
* [x] `GET /memory/episode/{conversation_id}` 获取会话记忆
* [x] `POST /memory/episode` 写入会话记忆
* [x] `GET /audit/memory` 获取记忆审计记录

---

## 🟡 阶段 2：记忆管理逻辑

### 2.1 写入策略

* [x] 提取用户/助手消息中的"关键事实/术语/目标/约束"
* [x] 判断是否持久化 → 写入 `MemoryEpisode` 或 `MemoryProfile`
* [x] 添加审计日志（写入事件）

### 2.2 读取策略

* [x] 获取最近 K 条消息
* [x] 获取最近一次摘要（Summary）
* [x] 语义检索相关的会话记忆（Episode Memory）
* [x] 加载相关的偏好（Profile Memory，作用域优先：Project > Global）
* [x] 组装提示 → 返回给 LLM

### 2.3 滚动摘要

* [x] 检测 token 数超阈值
* [x] 调用 summarizer（内部 LLM）生成新摘要
* [x] 存储到 `Summary` 表
* [x] 清理过长历史，只保留近 K 条消息

### 2.4 生命周期管理

* [x] 所有记忆允许 `expires_at` 字段
* [ ] 后台任务：定期清理过期记忆
* [x] 审计日志记录删除事件

---

## 🔵 阶段 3：前端 UI（React + Tailwind + shadcn/ui）

### 3.1 布局

* [x] `AppLayout`：左侧 Sidebar + 右侧 ChatWindow
* [x] Sidebar 宽度 280px，深灰背景
* [x] ChatWindow 白/浅灰背景

### 3.2 Sidebar

* [x] 显示会话列表（标题 + 最近一条消息）
* [x] 高亮当前会话
* [x] "+ 新建会话"按钮（蓝色）
* [x] 会话右键菜单：重命名 / 删除
* [x] 切换会话时刷新消息区

### 3.3 ChatWindow

* [x] 消息列表（User 气泡右对齐蓝色，Assistant 左对齐灰色）
* [x] 输入框 + 发送按钮（蓝色，圆角）
* [x] 支持多行输入（自动扩展高度）
* [x] AI 回复显示打字机动画
* [x] 滚动到最新消息

### 3.4 Memory Center（记忆中心面板）

* [x] Tabs：全局记忆 / 项目记忆 / 会话记忆
* [x] 每条记忆可编辑 / 删除 / 设置过期时间
* [x] 顶部开关：是否启用记忆
* [x] "临时对话"模式开关（关闭记忆引用）

### 3.5 Debug 模式（开发者可见）

* [x] 显示本轮提示中注入的内容（记忆片段 / 摘要 / 偏好卡片）
* [x] 显示工具调用轨迹

---

## 🟣 阶段 4：工具调用与对话流程

### 4.1 工具定义

* [ ] 所有工具以 JSON schema 暴露（仿 OpenAI function calling）
* [ ] 工具调用记录写入消息表 `tool_calls`

### 4.2 调用流程

* [ ] 用户发消息 → 组装提示（包含记忆）
* [ ] 模型决定是否调用工具
* [ ] 执行工具 → 返回结果
* [ ] 模型生成最终回复 → 写入消息表

### 4.3 容错策略

* [ ] 工具调用超时 → 返回"部分答案 + 延迟补充"
* [ ] 参数缺失 → 引导用户补充信息
* [ ] 多次失败 → 记录审计日志并降级为纯文本回答

---

## 🟤 阶段 5：治理与合规

### 5.1 记忆管理

* [x] 用户可一键清空全局 / 项目 / 会话记忆
* [x] 所有记忆变更写入审计日志
* [x] 提供 JSON 导出

### 5.2 隐私与安全

* [x] 默认屏蔽敏感字段（PII、隐私、健康数据）
* [x] 用户显式"记住" → 二次确认弹窗
* [ ] 过期清理任务定期运行

---

## 🚦 验收清单

* [x] **多会话管理**：创建 / 切换 / 删除 / 重命名正常工作
* [x] **标题来源**：首次消息自动更新标题
* [x] **短期记忆**：上下文滑窗 + 滚动摘要
* [x] **会话长期记忆**：目标/约束可被引用
* [x] **全局长期记忆**：偏好注入 + 项目模式覆盖
* [x] **记忆开关**：关闭时，不引用持久化信息
* [ ] **工具调用**：正常触发 + 容错处理
* [x] **治理**：用户可清空 / 导出记忆，审计日志可查
* [x] **UI**：Sidebar + ChatWindow + Memory Center 三大区域可用



👌 好的，你的意思是把 **Memory Center（记忆中心）** 和 **Debug 模式** 不放在左侧 Sidebar，而是作为 **系统设置面板中的二级功能**。这样可以避免主界面过于复杂，用户在正常对话时不会被打扰。下面是调整后的设计方案：

---

# 🔹系统设置调整版

## 🟢 系统设置入口

* 位置：右上角齿轮按钮（固定在 ChatWindow 顶部导航栏右上角）
* 点击后弹出 **系统设置抽屉/Modal**
* 分区（Tabs）：

  1. **常规设置**（主题、语言、快捷键等）
  2. **记忆中心**（Memory Center）
  3. **开发者工具**（Debug 模式）

---

## 🟡 记忆中心（Memory Center Tab）

### UI

* 三个 Tabs：**全局记忆** / **项目记忆** / **会话记忆**
* 每条记忆显示：

  * 内容预览
  * 来源（自动 / 用户写入）
  * 时间戳
  * 过期时间（可编辑）
* 操作：

  * ✏️ 编辑
  * ❌ 删除
  * ⏳ 设置过期时间
* 顶部开关：

  * [x] **启用记忆**（总开关）
  * [x] **临时对话模式**（本会话不引用记忆）

### 功能

* 用户可以直接管理持久化的记忆（Profile / Episode）
* 支持一键清空：全局 / 项目 / 当前会话

---

## 🔵 Debug 模式（开发者工具 Tab）

### UI

* 折叠面板（Accordion）显示每次请求的调试信息
* 内容：

  * [x] **注入的记忆片段**（Profile、Episode、Summary）
  * [x] **Prompt 拼接结果**（最终发给 LLM 的上下文）
  * [x] **工具调用轨迹**（调用参数 + 返回结果）
  * [x] **Token 使用情况**（输入 / 输出 token）
* 顶部开关：

  * [x] **启用 Debug 模式**（默认关闭，仅开发/测试时启用）

### 功能

* 方便开发者验证记忆注入是否正确
* 定位 LLM 工具调用错误
* 检查 token 压缩（摘要机制）是否触发