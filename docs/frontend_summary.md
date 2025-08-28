---

# 📋 前端开发任务清单（类似 Manus 的交互界面）

## 🚀 Step 1 - 项目初始化

* 使用 Vite + React + TypeScript 初始化项目
* 安装依赖：

  * `tailwindcss` + `postcss` + `autoprefixer`
  * `@radix-ui/react-*`（shadcn/ui 基础）
  * `framer-motion`（动画）
  * `zustand`（状态管理）
  * `axios`（API 调用）
* 配置 Tailwind（`tailwind.config.js` + `index.css`）
* 设置 ESLint + Prettier

---

## 🏗 Step 2 - 项目结构搭建

* 建立目录结构：

```
src/
 ├─ components/       # 通用组件
 ├─ modules/          # 功能模块
 ├─ store/            # 状态管理
 ├─ services/         # API 封装
 ├─ utils/            # 工具函数
 ├─ pages/            # 页面
 ├─ App.tsx
 └─ main.tsx
```

* 在 `App.tsx` 搭建基础布局：Sidebar + 主内容区

---

## 💬 Step 3 - 聊天核心模块 MVP

1. **ChatMessage 组件**

   * Props: `sender: "user" | "ai"`, `content: string`, `timestamp: string`
   * 左右对齐区分消息
   * 样式简洁（气泡样式 + 头像）

2. **MessageList 组件**

   * 渲染 ChatMessage 数组
   * 支持滚动到底部自动跟随

3. **ChatInput 组件**

   * 多行输入框 + 发送按钮
   * Enter 发送，Shift+Enter 换行
   * `disabled` 状态

4. **ChatPanel 页面**

   * 组合 `MessageList` + `ChatInput`
   * 管理一个简单的 `messages` state

---

## 🔄 Step 4 - 状态管理接入

* 在 `store/chatStore.ts` 中用 Zustand 管理：

  * `messages: Message[]`
  * `addMessage(message: Message)`
  * `setLoading(boolean)`
* 将 ChatPanel 切换为从 `chatStore` 获取消息

---

## 🌐 Step 5 - API 封装

* 在 `services/chatService.ts` 中实现：

  ```ts
  export async function sendMessage(content: string): Promise<string> {
    const res = await axios.post("/api/chat", { content });
    return res.data.reply;
  }
  ```

* 在 `ChatPanel` 中调用 `sendMessage`，并更新 `chatStore`

---

## 🎨 Step 6 - 动画与体验优化

* 使用 Framer Motion 给新消息添加“渐入”动画
* 添加“typing indicator”（AI 回复中时显示打字中…）
* 优化输入框交互体验

---

## 📚 Step 7 - 扩展功能

1. **Sidebar**

   * 会话列表（支持新建 / 删除）
   * 响应式（移动端折叠）

2. **Markdown 渲染**

   * 消息支持 Markdown（安装 `react-markdown`）

3. **Editor 模块（可选）**

   * 富文本 / Markdown 编辑区
   * 按钮将 AI 回复插入编辑区

4. **多会话管理**

   * `chatStore` 扩展支持多会话
   * Sidebar 与 ChatPanel 联动

---

## ✅ Step 8 - 最终优化

* 添加 Loading Skeleton（切换会话时）
* 支持暗黑模式（Tailwind `dark:` 方案）
* 提炼通用组件（按钮、卡片、Modal 等）
* 代码分包 & 懒加载（提高性能）

---

⚡ 建议执行方式：
Claude Code 每次只处理 **一个 Step**，完成后再进行下一个，避免范围过大。
