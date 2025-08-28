# 代码风格规范

本文档定义了 Faker Agent 项目的代码风格规范，包括命名约定、格式化规则、注释规范等。

## 1. 通用规范

### 1.1 文件组织

- 每个文件应专注于单一职责
- 相关功能应放在同一目录下
- 文件命名应反映其内容
- 避免过大的文件，建议单文件不超过500行

### 1.2 命名约定

- 使用有意义的、描述性的名称
- 避免使用缩写，除非是广为接受的缩写（如 HTTP, API 等）
- 保持一致的命名风格

### 1.3 注释规范

- 代码应该是自解释的，注释应该解释"为什么"而不是"做什么"
- 所有公共 API 应该有文档注释
- 复杂的算法或不明显的解决方案应该有注释
- 使用 TODO, FIXME, NOTE 等标记指出需要注意的地方

## 2. 后端代码规范 (Python)

### 2.1 代码风格

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 使用 [isort](https://pycqa.github.io/isort/) 进行导入排序
- 使用 [Flake8](https://flake8.pycqa.org/) 进行代码质量检查

### 2.2 命名约定

- **模块名**: 小写字母，使用下划线分隔，例如 `tool_registry.py`
- **类名**: 驼峰命名法，例如 `ToolRegistry`
- **函数名/方法名**: 小写字母，使用下划线分隔，例如 `register_tool`
- **变量名**: 小写字母，使用下划线分隔，例如 `tool_list`
- **常量名**: 大写字母，使用下划线分隔，例如 `MAX_RETRY_COUNT`

### 2.3 类和函数

- 类应该使用文档字符串描述其职责
- 函数应该使用文档字符串描述其功能、参数和返回值
- 函数应该专注于单一职责
- 避免副作用，推荐使用纯函数

### 2.4 类型注解

- 使用 [type hints](https://docs.python.org/3/library/typing.html) 注解函数参数和返回值
- 对于复杂类型，使用类型别名提高可读性
- 在项目中使用 `mypy` 进行静态类型检查

### 2.5 示例

```python
from typing import List, Dict, Optional, Any

# 常量定义
MAX_RETRY_COUNT = 3
DEFAULT_TIMEOUT = 60

class ToolRegistry:
    """
    工具注册中心，管理所有可用的工具。
    
    负责工具的注册、发现和检索。支持按名称、标签或类型过滤工具。
    """
    
    def __init__(self) -> None:
        self.tools: Dict[str, Any] = {}
        self.tags: Dict[str, List[str]] = {}
    
    def register_tool(self, name: str, tool: Any, tags: Optional[List[str]] = None) -> bool:
        """
        注册一个新工具到注册中心。
        
        Args:
            name: 工具的唯一名称
            tool: 工具实例
            tags: 工具标签列表，用于分类和过滤
            
        Returns:
            注册成功返回 True，否则返回 False
            
        Raises:
            ValueError: 当工具名称已存在时
        """
        if name in self.tools:
            raise ValueError(f"Tool with name '{name}' already exists")
        
        self.tools[name] = tool
        
        if tags:
            self.tags[name] = tags
            
        return True
    
    def get_tools_by_tag(self, tag: str) -> List[Any]:
        """返回具有指定标签的所有工具。"""
        return [self.tools[name] for name, tool_tags in self.tags.items() 
                if tag in tool_tags and name in self.tools]
```

## 3. 前端代码规范 (JavaScript/TypeScript)

### 3.1 代码风格

- 使用 [ESLint](https://eslint.org/) 进行代码检查
- 使用 [Prettier](https://prettier.io/) 进行代码格式化
- 首选 TypeScript 而非 JavaScript
- 使用最新的 ECMAScript 特性

### 3.2 命名约定

- **文件名**: 根据文件内容确定命名风格
  - 组件文件使用 PascalCase，例如 `Button.tsx`
  - 工具/服务文件使用 camelCase，例如 `apiClient.ts`
- **组件名**: 使用 PascalCase，例如 `ToolPanel`
- **函数名**: 使用 camelCase，例如 `fetchData`
- **变量名**: 使用 camelCase，例如 `userData`
- **常量名**: 使用 UPPER_CASE，例如 `API_BASE_URL`
- **类型名/接口名**: 使用 PascalCase，例如 `UserData`

### 3.3 组件规范

- 每个组件文件只包含一个组件
- 使用函数组件和 Hooks，避免使用类组件
- 将组件分为展示组件和容器组件
- 使用 PropTypes 或 TypeScript 类型进行属性验证

### 3.4 状态管理

- 对于简单组件，使用 React 内置的 useState 和 useReducer
- 对于复杂状态，使用 Zustand 进行集中管理
- 避免过深的组件嵌套和过多的属性传递

### 3.5 示例

```typescript
// 类型定义
interface ToolTagSelectorProps {
  selectedTags: string[];
  availableTags: string[];
  onTagToggle: (tag: string) => void;
  onClearAll: () => void;
  disabled?: boolean;
}

// 函数组件
const ToolTagSelector: React.FC<ToolTagSelectorProps> = ({
  selectedTags,
  availableTags,
  onTagToggle,
  onClearAll,
  disabled = false,
}) => {
  const [searchQuery, setSearchQuery] = useState<string>('');
  
  // 根据搜索过滤标签
  const filteredTags = useMemo(() => {
    if (!searchQuery) return availableTags;
    
    return availableTags.filter(tag => 
      tag.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [availableTags, searchQuery]);
  
  // 处理搜索输入变更
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };
  
  return (
    <div className="tool-tag-selector">
      {/* 搜索输入框 */}
      <input
        type="text"
        placeholder="搜索标签..."
        value={searchQuery}
        onChange={handleSearchChange}
        disabled={disabled}
        className="search-input"
      />
      
      {/* 标签列表 */}
      <div className="tag-list">
        {filteredTags.map(tag => (
          <Badge
            key={tag}
            variant={selectedTags.includes(tag) ? "primary" : "outline"}
            onClick={() => onTagToggle(tag)}
            disabled={disabled}
          >
            {tag}
          </Badge>
        ))}
      </div>
      
      {/* 操作按钮 */}
      {selectedTags.length > 0 && (
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={onClearAll}
          disabled={disabled}
        >
          清除全部
        </Button>
      )}
    </div>
  );
};

export default ToolTagSelector;
```

## 4. CSS/样式规范

### 4.1 方案选择

- 项目使用 TailwindCSS 作为主要样式解决方案
- 对于复杂组件，可以使用 CSS Modules 或组件库提供的样式解决方案

### 4.2 命名约定

- 使用 BEM 命名约定（当不使用 TailwindCSS 时）
- 类名使用小写字母和连字符，例如 `.tool-panel`
- 避免使用 ID 选择器进行样式设置

### 4.3 组织规则

- 相关的样式应该放在一起
- 使用注释分隔不同部分的样式
- 避免深层次的选择器嵌套（不超过3层）

## 5. 代码审查清单

提交代码前检查以下内容：

- [ ] 代码符合项目风格规范
- [ ] 所有必要的测试已添加并通过
- [ ] 没有未使用的代码或导入
- [ ] 代码已正确格式化
- [ ] 适当的错误处理已实现
- [ ] 代码中没有敏感信息（API密钥、密码等）
- [ ] 必要的文档已更新

## 6. 工具配置

### 6.1 Backend (Python)

```ini
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']

[tool.isort]
profile = "black"
line_length = 88

[tool.mypy]
python_version = "3.8"
disallow_untyped_defs = true
disallow_incomplete_defs = true
```

### 6.2 Frontend (JavaScript/TypeScript)

```json
// .eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
    "prettier"
  ],
  "rules": {
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off"
  }
}

// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5"
}
```