
# 📋 前端任务清单（详细版）

## 🚀 Step 1 - 项目初始化

1. 使用 Vite 创建项目：

   ```bash
   npm create vite@latest manus-frontend -- --template react-ts
   cd manus-frontend
   npm install
   ```

2. 安装依赖：

   ```bash
   npm install tailwindcss postcss autoprefixer
   npx tailwindcss init -p
   npm install axios zustand framer-motion react-markdown
   npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
   ```

3. 配置 `tailwind.config.js`：

   ```ts
   export default {
     content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
     theme: { extend: {} },
     plugins: [],
   }
   ```

4. 在 `index.css` 中加入：

   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   body {
     @apply bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100;
   }
   ```

---

## 🏗 Step 2 - 页面布局

### Layout 结构（`App.tsx`）

* 左侧 Sidebar（宽度固定 240px，移动端隐藏）
* 右侧主区域（ChatPanel）
* 样式参考：

  * 整体 `flex h-screen`
  * Sidebar `bg-white dark:bg-gray-800 border-r border-gray-200`
  * Main Panel `flex-1 flex flex-col`

👉 布局代码结构：

```tsx
<div className="flex h-screen">
  {/* Sidebar */}
  <aside className="w-60 hidden md:flex flex-col bg-white dark:bg-gray-800 border-r">
    {/* 会话列表 */}
  </aside>

  {/* Main Content */}
  <main className="flex-1 flex flex-col">
    <ChatPanel />
  </main>
</div>
```

---

## 💬 Step 3 - 聊天模块 MVP

### 1. ChatMessage 组件

* **文件**：`src/components/ChatMessage.tsx`
* **Props**：

  ```ts
  interface ChatMessageProps {
    sender: "user" | "ai";
    content: string;
    timestamp: string;
  }
  ```

* **布局**：

  * `flex items-start gap-2`
  * 用户消息：右对齐（`justify-end bg-blue-500 text-white`）
  * AI 消息：左对齐（`bg-gray-200 text-gray-900`）
* **样式**：气泡 `rounded-2xl px-4 py-2 max-w-[70%]`
* **示例 JSX**：

  ```tsx
  <div className={`flex ${sender === "user" ? "justify-end" : "justify-start"} mb-3`}>
    <div className={`px-4 py-2 rounded-2xl text-sm shadow-sm 
      ${sender === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-900"}
    `}>
      {content}
    </div>
  </div>
  ```

---

### 2. MessageList 组件

* **文件**：`src/components/MessageList.tsx`
* **功能**：

  * 接收 `messages: ChatMessageProps[]`
  * 渲染 `ChatMessage` 列表
  * 滚动到底部跟随最新消息（`useEffect + scrollRef`）
* **样式**：

  * `flex-1 overflow-y-auto p-4`
  * 背景保持纯净

---

### 3. ChatInput 组件

* **文件**：`src/components/ChatInput.tsx`
* **功能**：

  * 输入框（`textarea`，自动高度）
  * 右侧发送按钮（禁用状态时变灰）
  * Enter 发送消息，Shift+Enter 换行
* **样式**：

  * `flex items-center gap-2 border-t p-3 bg-white dark:bg-gray-800`
  * 输入框 `flex-1 resize-none p-2 rounded-lg border bg-gray-50 dark:bg-gray-700`
  * 按钮 `px-4 py-2 rounded-lg bg-blue-500 text-white hover:bg-blue-600`

---

### 4. ChatPanel 页面

* **文件**：`src/modules/chat/ChatPanel.tsx`
* **结构**：

  * `MessageList`（占据大部分空间）
  * `ChatInput`（固定在底部）
* **样式**：

  * `flex flex-col h-full`

示例：

```tsx
<div className="flex flex-col h-full">
  <MessageList messages={messages} />
  <ChatInput onSend={handleSend} />
</div>
```

---

📌 到这里，Claude Code 完成后应该能跑出一个 **基础聊天界面**：

* 左侧 Sidebar（静态）
* 右侧 ChatPanel，支持消息展示和输入

好的 ✅
我继续帮你把 **Step 4（状态管理接入）** 和 **Step 5（API 封装）** 拆解成详细任务清单，包含文件结构、状态字段设计、方法说明和样式规范。这样 Claude Code 在完成 Step 3 基础聊天界面之后，可以无缝进入数据流和后端交互部分。

---

# 📋 Step 4 - 状态管理接入（Zustand）

### 🎯 目标

把聊天消息和请求状态从本地 state 提升到全局 store，方便后续扩展多会话。

---

### 1. 安装 Zustand（如果没装）

```bash
npm install zustand
```

---

### 2. 定义数据模型

在 `src/types/chat.ts` 新建：

```ts
export interface Message {
  id: string;
  sender: "user" | "ai";
  content: string;
  timestamp: string;
  status?: "pending" | "success" | "error";
}
```

---

### 3. 创建 store

**文件**：`src/store/chatStore.ts`

```ts
import { create } from "zustand";
import { Message } from "../types/chat";

interface ChatState {
  messages: Message[];
  loading: boolean;
  addMessage: (msg: Message) => void;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setLoading: (loading: boolean) => void;
  clearMessages: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  loading: false,
  addMessage: (msg) => set((state) => ({ messages: [...state.messages, msg] })),
  updateMessage: (id, updates) =>
    set((state) => ({
      messages: state.messages.map((m) =>
        m.id === id ? { ...m, ...updates } : m
      ),
    })),
  setLoading: (loading) => set({ loading }),
  clearMessages: () => set({ messages: [] }),
}));
```

---

### 4. 替换 ChatPanel 内部 state

* 删除原来的 `useState(messages)`
* 使用 `useChatStore` 获取消息与操作方法：

  ```ts
  const { messages, addMessage, setLoading } = useChatStore();
  ```

* 发送消息时：

  ```ts
  addMessage({
    id: Date.now().toString(),
    sender: "user",
    content: text,
    timestamp: new Date().toLocaleTimeString(),
    status: "success",
  });
  ```

---

### 5. 样式/交互优化

* 输入中（loading 状态）：`ChatInput` 禁用输入框和按钮
* MessageList 最底部可显示“AI 正在回复中...”

---

# 📋 Step 5 - API 封装

### 🎯 目标

把发送消息的逻辑抽象成服务模块，支持后端对接（HTTP API / WebSocket / SSE）。

---

### 1. 服务层目录

`src/services/chatService.ts`

---

### 2. 基础封装

```ts
import axios from "axios";

export async function sendMessage(content: string): Promise<string> {
  try {
    const res = await axios.post("/api/chat", { content });
    return res.data.reply; // 假设返回格式 { reply: string }
  } catch (err) {
    console.error("API Error", err);
    throw err;
  }
}
```

---

### 3. 在 ChatPanel 调用 API

```ts
const handleSend = async (text: string) => {
  const id = Date.now().toString();
  addMessage({ id, sender: "user", content: text, timestamp: new Date().toLocaleTimeString(), status: "success" });
  
  setLoading(true);
  try {
    const reply = await sendMessage(text);
    addMessage({ id: id + "-ai", sender: "ai", content: reply, timestamp: new Date().toLocaleTimeString(), status: "success" });
  } catch {
    addMessage({ id: id + "-ai", sender: "ai", content: "⚠️ 出错了，请重试。", timestamp: new Date().toLocaleTimeString(), status: "error" });
  } finally {
    setLoading(false);
  }
};
```

---

### 4. 交互与样式优化

* **发送中状态**：

  * 输入框禁用
  * 在 MessageList 底部显示 “AI 正在输入...” 的虚拟气泡（灰色闪烁圆点）
* **错误消息样式**：

  * 红色背景 `bg-red-100 text-red-700`
  * 提供“重试”按钮

---

### 5. （可选扩展）流式返回（类似 Manus / ChatGPT）

* 替换 axios → `EventSource` 或 WebSocket
* 在 `updateMessage` 中逐步拼接内容，实现打字机效果

---

---

好嘞 ✅
我来帮你把 **Step 6（动画与体验优化）** 拆解成详细任务清单，包含组件实现、样式、动画细节，让 Claude Code 可以一步步实现更接近 **Manus / ChatGPT** 的体验。

---

# 📋 Step 6 - 动画与体验优化

### 🎯 目标

在已有聊天界面的基础上，增加动效与过渡，让交互更加流畅自然：

* 新消息 **渐入动画**
* AI 回复时的 **打字机效果** 或 **typing indicator**
* 切换/加载时的 **Skeleton 占位**
* 用户体验小细节（hover、按钮反馈）

---

## 1. 新消息渐入动画

**文件**：更新 `ChatMessage.tsx`

* 使用 [Framer Motion](https://www.framer.com/motion/) 包裹消息气泡：

```tsx
import { motion } from "framer-motion";

<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.2 }}
  className={`flex ${sender === "user" ? "justify-end" : "justify-start"} mb-3`}
>
  <div className={`px-4 py-2 rounded-2xl text-sm shadow-sm 
    ${sender === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-900"}
  `}>
    {content}
  </div>
</motion.div>
```

效果：消息由下方轻轻浮现，更自然。

---

## 2. Typing Indicator（AI 正在回复中…）

**文件**：`MessageList.tsx`

* 在 `loading === true` 时，在底部插入一个 AI 气泡，显示“打字中…”效果。
* 样式：灰色圆点闪烁。

```tsx
const TypingIndicator = () => (
  <div className="flex justify-start mb-3">
    <div className="px-4 py-2 rounded-2xl bg-gray-200 text-gray-900 flex gap-1">
      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
    </div>
  </div>
);
```

在 `MessageList` 末尾条件渲染：

```tsx
{loading && <TypingIndicator />}
```

---

## 3. 打字机效果（可选替代 Typing Indicator）

**文件**：`ChatMessage.tsx`

* AI 回复逐字显示（用一个 hook 控制）。

```tsx
import { useEffect, useState } from "react";

function useTypingEffect(text: string, speed = 30) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i + 1));
      i++;
      if (i === text.length) clearInterval(interval);
    }, speed);
    return () => clearInterval(interval);
  }, [text]);
  return displayed;
}
```

在 AI 消息中使用：

```tsx
{sender === "ai" ? useTypingEffect(content) : content}
```

---

## 4. Skeleton 占位（加载对话时）

**文件**：`MessageSkeleton.tsx`

* 使用灰色方块模拟消息气泡。

```tsx
const MessageSkeleton = () => (
  <div className="flex justify-start mb-3">
    <div className="w-40 h-5 bg-gray-300 dark:bg-gray-700 rounded-2xl animate-pulse"></div>
  </div>
);
```

在 `MessageList` 中，当 `messages` 还没加载时渲染多个 Skeleton：

```tsx
{loading && Array(3).fill(0).map((_, i) => <MessageSkeleton key={i} />)}
```

---

## 5. 按钮/交互反馈优化

* **ChatInput 按钮**：

  * hover：`hover:bg-blue-600`
  * 点击：`active:scale-95 transition-transform`
* **Sidebar 会话列表项**：

  * hover 高亮：`hover:bg-gray-100 dark:hover:bg-gray-700`
  * 当前选中项加边框/背景

---

## 6. 响应式/小屏优化

* 移动端：

  * Sidebar 默认隐藏，加一个汉堡按钮控制显示/隐藏
  * ChatPanel 占满屏幕
* 样式示例：

  * Sidebar `hidden md:flex`
  * 移动端 `absolute left-0 top-0 h-full w-60 z-50`

---

---

好嘞 ✅
我来帮你把 **Step 6（动画与体验优化）** 拆解成详细任务清单，包含组件实现、样式、动画细节，让 Claude Code 可以一步步实现更接近 **Manus / ChatGPT** 的体验。

---

# 📋 Step 6 - 动画与体验优化

### 🎯 目标

在已有聊天界面的基础上，增加动效与过渡，让交互更加流畅自然：

* 新消息 **渐入动画**
* AI 回复时的 **打字机效果** 或 **typing indicator**
* 切换/加载时的 **Skeleton 占位**
* 用户体验小细节（hover、按钮反馈）

---

## 1. 新消息渐入动画

**文件**：更新 `ChatMessage.tsx`

* 使用 [Framer Motion](https://www.framer.com/motion/) 包裹消息气泡：

```tsx
import { motion } from "framer-motion";

<motion.div
  initial={{ opacity: 0, y: 10 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.2 }}
  className={`flex ${sender === "user" ? "justify-end" : "justify-start"} mb-3`}
>
  <div className={`px-4 py-2 rounded-2xl text-sm shadow-sm 
    ${sender === "user" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-900"}
  `}>
    {content}
  </div>
</motion.div>
```

效果：消息由下方轻轻浮现，更自然。

---

## 2. Typing Indicator（AI 正在回复中…）

**文件**：`MessageList.tsx`

* 在 `loading === true` 时，在底部插入一个 AI 气泡，显示“打字中…”效果。
* 样式：灰色圆点闪烁。

```tsx
const TypingIndicator = () => (
  <div className="flex justify-start mb-3">
    <div className="px-4 py-2 rounded-2xl bg-gray-200 text-gray-900 flex gap-1">
      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
      <span className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></span>
    </div>
  </div>
);
```

在 `MessageList` 末尾条件渲染：

```tsx
{loading && <TypingIndicator />}
```

---

## 3. 打字机效果（可选替代 Typing Indicator）

**文件**：`ChatMessage.tsx`

* AI 回复逐字显示（用一个 hook 控制）。

```tsx
import { useEffect, useState } from "react";

function useTypingEffect(text: string, speed = 30) {
  const [displayed, setDisplayed] = useState("");
  useEffect(() => {
    let i = 0;
    const interval = setInterval(() => {
      setDisplayed(text.slice(0, i + 1));
      i++;
      if (i === text.length) clearInterval(interval);
    }, speed);
    return () => clearInterval(interval);
  }, [text]);
  return displayed;
}
```

在 AI 消息中使用：

```tsx
{sender === "ai" ? useTypingEffect(content) : content}
```

---

## 4. Skeleton 占位（加载对话时）

**文件**：`MessageSkeleton.tsx`

* 使用灰色方块模拟消息气泡。

```tsx
const MessageSkeleton = () => (
  <div className="flex justify-start mb-3">
    <div className="w-40 h-5 bg-gray-300 dark:bg-gray-700 rounded-2xl animate-pulse"></div>
  </div>
);
```

在 `MessageList` 中，当 `messages` 还没加载时渲染多个 Skeleton：

```tsx
{loading && Array(3).fill(0).map((_, i) => <MessageSkeleton key={i} />)}
```

---

## 5. 按钮/交互反馈优化

* **ChatInput 按钮**：

  * hover：`hover:bg-blue-600`
  * 点击：`active:scale-95 transition-transform`
* **Sidebar 会话列表项**：

  * hover 高亮：`hover:bg-gray-100 dark:hover:bg-gray-700`
  * 当前选中项加边框/背景

---

## 6. 响应式/小屏优化

* 移动端：

  * Sidebar 默认隐藏，加一个汉堡按钮控制显示/隐藏
  * ChatPanel 占满屏幕
* 样式示例：

  * Sidebar `hidden md:flex`
  * 移动端 `absolute left-0 top-0 h-full w-60 z-50`

---

---

# 📋 Step 7 - 扩展功能

### 🎯 目标

1. **Sidebar 会话管理**：支持新建 / 切换 / 删除会话
2. **Markdown 渲染**：消息支持代码块、列表、标题等格式
3. **多会话状态管理**：不同会话的消息独立存储
4. **整体 UX 提升**：响应式、选中高亮、暗黑模式适配

---

## 1. Sidebar 会话管理

**文件**：`src/components/Sidebar.tsx`

### 功能需求

* 展示会话列表（名称 + 最近一条消息摘要）
* 新建会话按钮（➕ 图标）
* 删除会话按钮（🗑 图标）
* 点击会话 → 切换当前会话

### UI 设计

* 样式：

  * `flex flex-col w-60 h-full border-r bg-white dark:bg-gray-800`
* 列表项：

  * `flex justify-between items-center px-3 py-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 rounded-md`
* 当前选中：

  * `bg-blue-100 text-blue-600 dark:bg-blue-900`

### 示例 JSX

```tsx
<div className="flex flex-col h-full p-2">
  <div className="flex justify-between items-center mb-4">
    <h2 className="text-lg font-semibold">会话</h2>
    <button className="text-blue-500 hover:text-blue-600">➕</button>
  </div>
  <div className="flex-1 overflow-y-auto space-y-1">
    {sessions.map((s) => (
      <div
        key={s.id}
        onClick={() => setCurrentSession(s.id)}
        className={`flex justify-between items-center px-3 py-2 rounded-md cursor-pointer ${
          currentSessionId === s.id
            ? "bg-blue-100 text-blue-600 dark:bg-blue-900"
            : "hover:bg-gray-100 dark:hover:bg-gray-700"
        }`}
      >
        <span className="truncate">{s.name}</span>
        <button className="text-gray-400 hover:text-red-500">🗑</button>
      </div>
    ))}
  </div>
</div>
```

---

## 2. Markdown 渲染

**文件**：更新 `ChatMessage.tsx`

* 使用 [`react-markdown`](https://github.com/remarkjs/react-markdown)
* 增强代码高亮（可选安装 `react-syntax-highlighter`）

```tsx
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

<div className="prose dark:prose-invert max-w-none">
  <ReactMarkdown remarkPlugins={[remarkGfm]}>
    {content}
  </ReactMarkdown>
</div>
```

### 样式规范

* Tailwind Prose 插件：

  * 安装 `@tailwindcss/typography`
  * `tailwind.config.js` 插件中加：`require('@tailwindcss/typography')`
* 代码块：灰色背景，圆角，滚动条美化

---

## 3. 多会话状态管理

**文件**：更新 `src/store/chatStore.ts`

### Store 设计

```ts
interface Session {
  id: string;
  name: string;
  messages: Message[];
}

interface ChatState {
  sessions: Session[];
  currentSessionId: string | null;
  addSession: (name: string) => void;
  deleteSession: (id: string) => void;
  setCurrentSession: (id: string) => void;
  addMessageToSession: (sessionId: string, msg: Message) => void;
}
```

### 方法逻辑

* `addSession(name)` → 新建会话，加入 `sessions`
* `deleteSession(id)` → 从数组移除
* `setCurrentSession(id)` → 切换当前会话
* `addMessageToSession(sessionId, msg)` → 给指定会话追加消息

### ChatPanel 调整

* 渲染当前会话 `messages = sessions.find(s => s.id === currentSessionId)?.messages || []`
* 发送消息时调用 `addMessageToSession(currentSessionId, msg)`

---

## 4. 响应式优化

* **移动端**：

  * Sidebar 默认隐藏，点击汉堡按钮显示
  * Sidebar 样式：

    ```css
    absolute left-0 top-0 h-full w-60 z-50 bg-white dark:bg-gray-800
    ```

* **Main Content**：

  * `flex-1 flex flex-col h-screen`
  * 确保 ChatPanel 在小屏幕下可全屏展示

---

## 5. 暗黑模式适配

* Tailwind `dark:` 方案
* 建议在根组件设置 `className={darkMode ? "dark" : ""}`
* 保证：

  * Sidebar 背景 `dark:bg-gray-800`
  * 气泡颜色对比足够明显
  * Markdown 内容 `prose dark:prose-invert`

---

---

# 📋 Step 8 - 最终优化

## 🎯 目标

* **性能优化**：懒加载模块、减少首屏体积
* **通用组件**：抽离常用 UI，保持风格统一
* **Skeleton & 占位优化**：切换会话、加载数据时更自然
* **UX 打磨**：错误提示、暗黑模式适配、流畅过渡动画

---

## 1. Skeleton 组件抽取

**文件**：`src/components/Skeleton.tsx`

```tsx
interface SkeletonProps {
  className?: string;
}
export const Skeleton = ({ className = "" }: SkeletonProps) => (
  <div className={`bg-gray-300 dark:bg-gray-700 animate-pulse rounded ${className}`} />
);
```

**使用场景**

* 会话切换时：

  * `MessageList` → 显示若干 Skeleton 消息气泡
* Sidebar 加载会话列表时：

  * 显示灰色方块占位

---

## 2. 通用 UI 组件抽取

### Button 组件

**文件**：`src/components/ui/Button.tsx`

```tsx
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "danger";
}
export const Button = ({ variant = "primary", className, ...props }: ButtonProps) => {
  const base = "px-4 py-2 rounded-lg font-medium transition-colors";
  const variants = {
    primary: "bg-blue-500 text-white hover:bg-blue-600",
    secondary: "bg-gray-200 text-gray-800 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600",
    danger: "bg-red-500 text-white hover:bg-red-600",
  };
  return <button className={`${base} ${variants[variant]} ${className}`} {...props} />;
};
```

### Card 组件

**文件**：`src/components/ui/Card.tsx`

```tsx
export const Card = ({ children }: { children: React.ReactNode }) => (
  <div className="rounded-2xl shadow-sm border bg-white dark:bg-gray-800 p-4">
    {children}
  </div>
);
```

---

## 3. 错误与空状态优化

### ErrorBanner

**文件**：`src/components/ErrorBanner.tsx`

```tsx
export const ErrorBanner = ({ message }: { message: string }) => (
  <div className="bg-red-100 text-red-700 p-3 rounded-md text-sm">
    ⚠️ {message}
  </div>
);
```

* 使用场景：API 调用失败时插入在 `MessageList` 底部

### EmptyState

**文件**：`src/components/EmptyState.tsx`

```tsx
export const EmptyState = ({ title }: { title: string }) => (
  <div className="flex flex-col items-center justify-center h-full text-gray-400">
    <span className="text-lg">{title}</span>
  </div>
);
```

* 使用场景：当会话没有消息时显示提示文案

---

## 4. 懒加载与代码分包

### React.lazy

* Sidebar、ChatPanel 等模块通过懒加载引入

```tsx
import { Suspense, lazy } from "react";

const ChatPanel = lazy(() => import("./modules/chat/ChatPanel"));

<Suspense fallback={<div>加载中...</div>}>
  <ChatPanel />
</Suspense>
```

### 路由级别懒加载

* 如果有 `/workspace` `/settings` 等页面，使用 React Router 的 `lazy`

---

## 5. 性能优化

* 使用 `React.memo` 优化 `ChatMessage`，避免整个列表重新渲染
* 对 MessageList 使用 **虚拟滚动**（如 `react-virtual`）提升性能
* 打包优化：

  * Vite 配置中开启 `splitChunks`，减少主包体积

---

## 6. 过渡与动效打磨

* **会话切换过渡**：

  * 使用 Framer Motion `AnimatePresence` 添加淡入淡出
* **Sidebar 折叠展开**：

  * 过渡宽度动画 `transition-all duration-300`
* **输入框聚焦效果**：

  * 聚焦时边框高亮 `focus:ring-2 focus:ring-blue-500`

---

## 7. 深色模式增强

* 确保所有通用组件（Button、Card、Skeleton、ErrorBanner）都有 `dark:` 样式
* Markdown 渲染使用 `prose dark:prose-invert`

---

## 8. 项目收尾

* 统一 ESLint + Prettier 格式化规则
* 在 `package.json` 添加 `lint` 和 `format` 脚本
* 添加一个简单的 README（说明项目启动方法、功能模块）

---
