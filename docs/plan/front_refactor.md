
# 高阶步骤一览

1. 准备工程 & 安装依赖
2. Tailwind & 全局样式配置（含暗黑模式）
3. 目录结构与示例数据
4. 页面主布局（左侧会话列表 + 中央对话区 + 底部输入）
5. 会话列表（Sidebar）实现（虚拟化 + 高亮）
6. 消息列表（MessageList）与消息气泡（MessageBubble）实现（响应式 + 悬停操作栏）
7. 输入区（Composer）：多行输入、快捷键、草稿保存、上传、发送逻辑（支持流式）
8. 状态管理（Zustand / Context）与 API / 流式输出设计（WebSocket / fetch streams）
9. 微交互与动效（framer-motion）
10. 可访问性、国际化、测试、性能与部署
11. PR / Commit 规范与回归测试


---

# 0. 前置与依赖（命令）

推荐使用 Vite + React + TypeScript。

```bash
# 创建项目
npm create vite@latest chatgpt-style-ui -- --template react-ts
cd chatgpt-style-ui
npm install

# 安装依赖
npm install lucide-react clsx zustand react-window react-markdown rehype-raw framer-motion
# dev deps
npm install -D tailwindcss postcss autoprefixer eslint prettier jest @testing-library/react @testing-library/jest-dom
npx tailwindcss init -p
```

说明与可替换项：

* 图标：`lucide-react`（可替换为 `react-icons`）。
* 状态：`zustand`（小巧）；若已有 Redux，使用 Redux 也可。
* 虚拟化：`react-window` 用于长会话列表。
* 动画：`framer-motion`。
* Markdown 渲染：`react-markdown`（安全性：可加 `rehype-sanitize`）。

---

# 1. Tailwind 配置（`tailwind.config.cjs`）

开启 `dark` 模式并指定路径：

```js
module.exports = {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: '#0ea5e9', // 可根据 design token 调整
        }
      }
    },
  },
  plugins: [],
};
```

`src/index.css`（最小）：

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 全局微调 */
html, body, #root {
  height: 100%;
}

body {
  @apply bg-gray-50 dark:bg-[#0b1220] text-gray-800 dark:text-gray-100;
}
```

---

# 2. 推荐项目目录

```
src/
  main.tsx
  App.tsx
  styles/
    index.css
  components/
    Sidebar.tsx
    ChatWindow.tsx
    MessageList.tsx
    MessageBubble.tsx
    Composer.tsx
    Header.tsx
  store/
    useChatStore.ts
  lib/
    api.ts
    stream.ts
  types/
    index.ts
  utils/
    format.ts
```

---

# 3. 全局布局（`src/App.tsx`）

核心结构：三栏布局（可在窄屏下折叠为单列）。

```tsx
import React from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';

export default function App() {
  return (
    <div className="h-screen grid grid-cols-[280px_1fr] dark:text-gray-100">
      <aside className="border-r dark:border-gray-800 bg-white dark:bg-[#071021]">
        <Sidebar />
      </aside>

      <main className="flex flex-col">
        <ChatWindow />
      </main>
    </div>
  );
}
```

要点：

* 左侧固定宽度 280px。
* 主区占剩余空间并在内部使用 flex 列布局实现消息列表与输入框衔接（输入框固定底部）。
* 使用 `dark` 类来切换主题（可以在 `<html>` 或顶层组件上切换 `class`）。

---

# 4. Sidebar（会话列表）`src/components/Sidebar.tsx`

要求：Hover 高亮、active 状态、搜索、新会话按钮、虚拟化（react-window）。

代码（简化版）：

```tsx
import React from 'react';
import { FixedSizeList as List } from 'react-window';
import useChatStore from '../store/useChatStore';
import { Plus } from 'lucide-react';
import clsx from 'clsx';

function ConversationItem({ index, style, data }: any) {
  const conv = data[index];
  const { selectConversation, selectedId } = data.actions;
  const active = selectedId === conv.id;

  return (
    <div
      style={style}
      onClick={() => selectConversation(conv.id)}
      className={clsx(
        'px-4 py-3 cursor-pointer flex items-center gap-3',
        active ? 'bg-sky-600/10 font-semibold' : 'hover:bg-gray-100 dark:hover:bg-[#06101a]'
      )}
    >
      <div className="w-9 h-9 rounded-md bg-sky-100 dark:bg-sky-900 flex items-center justify-center text-sky-600">
        C
      </div>
      <div className="flex-1 truncate">
        <div className="truncate">{conv.title}</div>
        <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{conv.snippet}</div>
      </div>
    </div>
  );
}

export default function Sidebar() {
  const conversations = useChatStore((s) => s.conversations);
  const selectedId = useChatStore((s) => s.selectedConversationId);
  const selectConversation = useChatStore((s) => s.selectConversation);

  const actions = { selectConversation, selectedId };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 flex items-center justify-between">
        <div className="text-lg font-bold">对话列表</div>
        <button className="p-2 rounded-md hover:bg-gray-100 dark:hover:bg-[#03121a]">
          <Plus size={18} />
        </button>
      </div>

      <div className="flex-1 overflow-hidden">
        <List
          height={window.innerHeight - 120}
          itemCount={conversations.length}
          itemSize={72}
          width="100%"
          itemData={{ ...conversations, actions }}
        >
          {ConversationItem}
        </List>
      </div>
    </div>
  );
}
```

要点：

* 使用 react-window 降低长列表渲染成本。
* 每个会话项 hover 高亮并显示 snippet。
* 点击后将会话设为 active（状态存储在 store 中）。

---

# 5. 状态管理（`src/store/useChatStore.ts`）—— 使用 Zustand

管理：会话列表、选中会话、消息 CRUD、草稿、loading 状态。

```ts
import create from 'zustand';
import { v4 as uuidv4 } from 'uuid';
import type { Conversation, Message } from '../types';

type ChatState = {
  conversations: Conversation[];
  selectedConversationId?: string;
  selectConversation: (id: string) => void;
  addConversation: (title?:string) => string;
  addMessage: (convId: string, msg: Message) => void;
  updateMessage: (convId: string, msgId: string, patch: Partial<Message>) => void;
};

const useChatStore = create<ChatState>((set, get) => ({
  conversations: [
    { id: '1', title: '示例会话', snippet: '你好，今天天气如何？', messages: [] },
  ],
  selectedConversationId: '1',
  selectConversation: (id) => set({ selectedConversationId: id }),
  addConversation: (title = '新会话') => {
    const id = uuidv4();
    set((s) => ({ conversations: [{ id, title, snippet: '', messages: [] }, ...s.conversations], selectedConversationId: id }));
    return id;
  },
  addMessage: (convId, msg) => {
    set((s) => ({
      conversations: s.conversations.map((c) => c.id === convId ? { ...c, messages: [...c.messages, msg], snippet: msg.content.slice(0, 120) } : c)
    }));
  },
  updateMessage: (convId, msgId, patch) => {
    set((s) => ({
      conversations: s.conversations.map((c) => c.id === convId ? {
        ...c,
        messages: c.messages.map(m => m.id === msgId ? { ...m, ...patch } : m)
      } : c)
    }));
  },
}));

export default useChatStore;
```

类型文件 `src/types/index.ts`：

```ts
export type Message = {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt?: string;
  meta?: Record<string, any>;
};

export type Conversation = {
  id: string;
  title: string;
  snippet: string;
  messages: Message[];
};
```

---

# 6. MessageList + MessageBubble（核心 UI）

需要支持：

* 用户消息靠右，助手消息靠左；
* 圆角气泡、最大宽度约 70\~80% 并自动换行；
* 每条消息在悬停时显示操作按钮（复制、编辑、更多）；
* 支持时间/作者显示、头像；
* 支持 Markdown 与代码块渲染（`react-markdown`）；
* 新消息进入时有入场动画（framer-motion）。

`src/components/MessageBubble.tsx`（核心）：

```tsx
import React, { useState } from 'react';
import clsx from 'clsx';
import { Copy, Edit2 } from 'lucide-react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

type Props = {
  isUser?: boolean;
  message: { id:string; content:string; role: string; createdAt?:string };
  onCopy?: (text:string) => void;
  onEdit?: (id:string, newContent:string) => void;
};

export default function MessageBubble({ isUser, message, onCopy, onEdit }: Props) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(message.content);

  const bubbleCls = clsx(
    'max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-6 break-words relative',
    isUser ? 'ml-auto bg-sky-600 text-white rounded-br-[6px]' : 'mr-auto bg-gray-100 dark:bg-[#0f1724] dark:text-gray-100'
  );

  return (
    <motion.div
      initial={{ opacity: 0, y: 6 }}
      animate={{ opacity: 1, y: 0 }}
      className={clsx('group w-full flex my-2', isUser ? 'justify-end' : 'justify-start')}
    >
      {!isUser && <div className="w-10 h-10 rounded-md bg-gray-300 dark:bg-gray-700 mr-3 flex items-center justify-center">AI</div>}

      <div className={bubbleCls}>
        {!editing ? (
          <>
            <div className="prose prose-sm max-w-full">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>

            {/* 悬停操作 */}
            <div className="absolute right-2 bottom-1 opacity-0 group-hover:opacity-100 transition-opacity flex gap-2">
              <button onClick={() => navigator.clipboard.writeText(message.content)} aria-label="复制">
                <Copy size={16} />
              </button>
              <button onClick={() => setEditing(true)} aria-label="编辑">
                <Edit2 size={16} />
              </button>
            </div>
          </>
        ) : (
          <div>
            <textarea
              className="w-full bg-transparent outline-none resize-none"
              rows={4}
              value={value}
              onChange={(e) => setValue(e.target.value)}
            />
            <div className="flex gap-2 justify-end mt-2">
              <button className="px-3 py-1 rounded-md bg-gray-200" onClick={() => setEditing(false)}>取消</button>
              <button className="px-3 py-1 rounded-md bg-sky-600 text-white" onClick={() => {
                setEditing(false);
                onEdit?.(message.id, value);
              }}>保存</button>
            </div>
          </div>
        )}
      </div>

      {isUser && <div className="w-8" />}
    </motion.div>
  );
}
```

`src/components/MessageList.tsx`（渲染多条消息 + 滚动到底）：

```tsx
import React, { useEffect, useRef } from 'react';
import MessageBubble from './MessageBubble';
import useChatStore from '../store/useChatStore';

export default function MessageList() {
  const conv = useChatStore((s) => s.conversations.find(c => c.id === s.selectedConversationId));
  const listRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: 'smooth' });
  }, [conv?.messages.length]);

  if (!conv) return <div className="p-6">请选择一个会话</div>;

  return (
    <div ref={listRef} className="flex-1 overflow-auto px-6 py-4">
      {conv.messages.map((m) => (
        <MessageBubble
          key={m.id}
          message={m}
          isUser={m.role === 'user'}
          onEdit={(id, content) => /* 调用 store 更新 */ null}
        />
      ))}
    </div>
  );
}
```

要点：

* 使用 `.group` + `group-hover` 来控制悬停显示动作按钮（无 JS）
* 保持 `max-w` 限制避免整行宽度过大
* 使用 `ReactMarkdown` 渲染富文本（支持代码块、列表）

---

# 7. Composer（输入框）`src/components/Composer.tsx`

功能：

* 自动撑高的多行输入（或使用 `textarea` 动态 height）
* Ctrl/Cmd+Enter 发送（回车换行）
* 发送后清空并将消息加入 store（本地回显），后端流式返回更新 assistant 消息
* 草稿保存在 localStorage（防止刷新丢失）
* 附件/上传按钮（可选）

代码示例：

```tsx
import React, { useState, useEffect, useRef } from 'react';
import useChatStore from '../store/useChatStore';
import { Send } from 'lucide-react';

export default function Composer() {
  const selectedId = useChatStore((s) => s.selectedConversationId);
  const addMessage = useChatStore((s) => s.addMessage);
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    const draft = localStorage.getItem(`draft:${selectedId}`);
    setText(draft || '');
  }, [selectedId]);

  useEffect(() => {
    localStorage.setItem(`draft:${selectedId}`, text);
  }, [text, selectedId]);

  function handleSend() {
    if (!text.trim()) return;
    const msg = {
      id: crypto.randomUUID(),
      role: 'user',
      content: text,
      createdAt: new Date().toISOString(),
    };
    if (!selectedId) return;
    addMessage(selectedId, msg);
    setText('');
    // 调用后端发送并用流式更新 assistant 的回复
    window.fetch('/api/chat', { method: 'POST', body: JSON.stringify({ conversationId: selectedId, text }) })
      .then(() => {/* 处理 */});
  }

  return (
    <div className="p-4 border-t dark:border-gray-800 bg-white dark:bg-[#071021]">
      <div className="flex items-end gap-3">
        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => { if ((e.ctrlKey||e.metaKey) && e.key === 'Enter') { e.preventDefault(); handleSend(); } }}
          className="flex-1 min-h-[44px] max-h-60 resize-none p-3 bg-gray-50 dark:bg-[#06101a] rounded-2xl outline-none"
          placeholder="输入消息，按 Ctrl/Cmd+Enter 发送"
        />
        <button onClick={handleSend} className="p-3 rounded-full bg-sky-600 text-white">
          <Send size={16} />
        </button>
      </div>
    </div>
  );
}
```

要点：

* 把 API 调用与 UI 回显分离（先回显用户消息，再根据后端流更新 AI 回复）。
* 发送逻辑应在服务端保管 API key，前端仅发到你自己的后端代理。

---

# 8. 流式输出（后端 / 前端读取流）

**实现思路**：后端（Node/Go/Python）向 LLM（OpenAI/Claude 等）发送请求并把返回的可读流（Server-Sent Events / fetch ReadableStream）透传给前端。前端将分块 Append 到 assistant 消息。

前端 fetch 流式读取示例（`lib/stream.ts`）：

```ts
export async function streamChat(url: string, body: any, onChunk: (text: string) => void) {
  const res = await fetch(url, {
    method: 'POST',
    body: JSON.stringify(body),
    headers: { 'Content-Type': 'application/json' }
  });
  if (!res.body) throw new Error('No stream');

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value, { stream: true });
    onChunk(chunk);
  }
}
```

后端务必将真实 LLM API Key 存在 server，并做权限/配额控制 & 限速。

---

# 9. 微交互（framer-motion）

示例：消息进入淡入 + 轻微位移（已在 MessageBubble 使用 `motion.div`）。对按钮 hover 使用 CSS 过渡即可。

---

# 10. 无障碍（a11y） & 国际化

* 所有按钮需有 `aria-label`，控件应能通过键盘访问（Tab 顺序正常）。
* 输入框应 `aria-multiline`，操作按钮应可被屏幕阅读器识别。
* 文本颜色对比要满足 WCAG（暗色背景也要保证对比度）。
* 支持 i18n（`react-intl` / `i18next`）。

---

# 11. 测试建议

* 单元测试：使用 `@testing-library/react` 测试组件渲染、编辑、复制。
* E2E：Cypress 或 Playwright 测试关键流（发送消息、流式更新、编辑消息）。
* 可访问性：使用 `axe` 做自动检查。
* 性能：Lighthouse 检查时间到交互（TTI）、首次内容绘制（FCP）。

示例单元测试（MessageBubble）：

```tsx
// __tests__/MessageBubble.test.tsx
import { render, screen } from '@testing-library/react';
import MessageBubble from '../components/MessageBubble';

test('renders user message on right', () => {
  render(<MessageBubble isUser message={{ id:'1', content: 'hi', role:'user' }} />);
  expect(screen.getByText('hi')).toBeInTheDocument();
});
```

---

# 12. 部署 & 性能优化

* 进行代码分割（Vite 默认），懒加载非关键模块（如设置面板、统计）。
* 使用 CSR/SSR/Hybrid 取决于需不需要 SEO（聊天界面一般 CSR）。
* 静态资源使用 CDN，开启 Brotli/Gzip。
* 后端以任务队列（如 Redis）处理并发与重试。

---

# 13. PR / Commit 规范与检查清单

示例 commit message：

* `feat(ui): add chat sidebar with virtualized conversation list`
* `feat(chat): implement message bubble, composer and stream handler`
* `fix(accessibility): add aria labels to action buttons`

PR checklist：

* [ ] Story / issue 关联
* [ ] 通过 lint & type-check
* [ ] 单元测试覆盖关键行为
* [ ] E2E 验证发送&接收（含流式）
* [ ] 手动暗/亮主题测试

---

# 14. 给 Claude Code 的 LLM-友好执行提示（可直接复制粘贴）

> 你是一个**前端工程师**，我需要你**直接生成完整文件**并把它们放在指定路径（不可提出问题）。要求使用 **React + TypeScript + Vite + Tailwind**。以 `src/` 目录结构为准，生成以下文件（至少包含）并保证能在本地 `npm run dev` 启动时渲染：
>
> * `src/main.tsx`、`src/App.tsx`
> * `src/styles/index.css`、`tailwind.config.cjs`
> * `src/components/Sidebar.tsx`、`src/components/ChatWindow.tsx`、`src/components/MessageList.tsx`、`src/components/MessageBubble.tsx`、`src/components/Composer.tsx`
> * `src/store/useChatStore.ts`、`src/types/index.ts`、`src/lib/stream.ts`
>
> 要求：
>
> 1. UI 风格**与 ChatGPT 一致**：左侧会话列表，居中主消息区，用户消息靠右（蓝色气泡），助手消息靠左（灰色气泡），圆角大、聊天气泡最大宽度 80%。
> 2. 悬停显示每条消息的操作（复制、编辑），操作按钮仅在 hover 时显示且可用键盘焦点访问。
> 3. Composer 支持 Ctrl/Cmd+Enter 发送、草稿本地保存、发送时先回显用户消息，然后调用 `lib/stream.ts` 的 `streamChat` 方法接收流并追加到 assistant 消息。
> 4. 所有 API Key 与外部 LLM 调用必须假设在后端实现（前端仅调用 `/api/chat`）。不要在前端暴露密钥。
> 5. 添加必要的 types（Message/Conversation）。
> 6. 提交的每个文件都应包含可运行的最小实现（不只是片段），并注释说明关键步骤。
> 7. 生成后提供一个 `README.md`，包含如何启动、如何配置后端代理（示例端点 `/api/chat`）、以及如何切换主题（暗/亮）。
>
> 注意：不要在运行时询问用户任何选择。生成的代码应尽可能完整，包含必要的 `import`。如若不能实现某个外部集成（例如云端 LLM），请在对应文件顶部以注释形式说明如何替换为真实实现。

---

# 15. 额外建议 & 常见坑

* **不要把 API key 放在前端**。
* **滚动到底部**：使用 `scrollIntoView` 或 `scrollTo`，在追加消息时平滑滚动。
* **虚拟化与自动滚动冲突**：若使用虚拟化（react-window），手动管理 scroll offset。
* **大型代码块渲染**：代码块需支持语法高亮（`rehype-highlight` 或 `prism-react-renderer`）。
* **并发消息**：当多次请求同时进行时，为每次请求创建唯一的 temp assistant message id 并合并更新，避免覆盖。

