# 前端开发规范

## 技术栈

### UI & Styling
- shadcn/ui 用于组件
- Tailwind CSS 用于样式
- Lucide React 用于图标

### 状态管理与数据
- Zustand 用于本地状态管理
- Axios 用于 HTTP 请求
- @tanstack/react-query 用于服务器状态管理（计划引入）

### 显示设置
- CSS 变量用于动态样式调整
- localStorage 用于设置持久化

### 表单处理
- react-hook-form + zod 用于表单验证（计划引入）

## 组件库集成

### 安装 shadcn/ui
```bash
npx shadcn-ui@latest init
```

### 常用组件
```bash
npx shadcn-ui@latest add button input textarea select checkbox form card dialog dropdown-menu badge table tabs toast
```

## 开发规范

### 组件开发
1. 优先使用 shadcn/ui 组件
2. 遵循 shadcn/ui 的样式模式保持一致性
3. 使用 `cn` 工具处理条件类名
4. 实现适当的加载和错误状态
5. 使用语义化的 HTML 元素
6. 确保键盘导航正常工作

### 代码组织
```
src/
├── components/           # 可复用的 UI 组件
│   ├── ui/              # shadcn/ui 组件
│   └── layout/          # 布局组件
├── features/            # 功能模块
├── hooks/               # 自定义 Hooks
├── lib/                 # 工具函数和库
├── services/            # API 服务
└── store/               # 状态管理
    └── displayStore.js  # 显示设置状态管理
```

### 命名约定
- 组件文件使用 PascalCase (`Button.jsx`)
- 组件名称与文件名一致
- Hook 文件使用 camelCase 并以 `use` 开头 (`useAuth.js`)
- 工具函数文件使用 camelCase (`utils.js`)

### 样式规范
- 优先使用 Tailwind CSS 类
- 避免使用内联样式
- 复杂样式可使用 CSS 模块
- 响应式设计使用 Tailwind 的断点

### 状态管理
- 本地 UI 状态使用 useState/useReducer
- 全局应用状态使用 Zustand
- 服务器状态使用 React Query
- 状态更新使用不可变模式
- 使用 Zustand 中间件进行状态持久化

### 错误处理
- 所有异步操作都需要错误处理
- 用户友好的错误消息
- 适当的重试机制
- 错误边界捕获渲染错误

### 性能优化
- 使用 React.memo 优化组件重渲染
- 懒加载非关键组件
- 虚拟化长列表
- 图片懒加载和优化

### 测试
- 单元测试使用 Vitest 和 React Testing Library
- 组件测试关注用户行为而非实现细节
- 集成测试覆盖关键用户流程
- 测试文件放在前端目录下的 `tests` 文件夹中
- 使用 `*.test.jsx` 命名测试文件

## 最佳实践

### 可访问性
- 正确使用语义化 HTML
- 确保足够的颜色对比度
- 支持键盘导航
- 为图像提供 alt 文本

### 国际化
- 使用 i18next 进行国际化（计划引入）
- 将文本内容外部化
- 支持 RTL 布局

### 安全性
- 验证和清理用户输入
- 防止 XSS 攻击
- 使用 HTTPS 连接
- 保护敏感信息

### 用户体验
- 提供直观的设置界面
- 保存用户偏好设置
- 支持多种显示模式
- 确保设置更改即时生效