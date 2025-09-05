# Agent与Conversation模块整合设计文档

## 1. 现有架构分析

### 1.1 Agent模块现状
- 位于 `backend/core/agent.py`
- 核心职责：处理用户查询，通过LangGraph编排工具执行流程
- 依赖：LangGraph、工具注册中心、LLM模型
- 当前问题：与Conversation模块分离，无法有效管理会话上下文

### 1.2 Conversation模块现状
- 位于 `backend/core/services/conversation_service.py`
- 核心职责：管理会话和消息的CRUD操作
- 依赖：数据库访问层、Conversation模型
- 当前问题：仅处理数据存储，不涉及LLM交互逻辑

### 1.3 存在的问题
1. **职责分离不清晰**：Agent处理LLM交互，Conversation处理数据存储，但两者缺乏有效整合
2. **耦合度高**：业务逻辑与数据库访问紧密耦合
3. **扩展性差**：难以支持不同的数据存储方案
4. **上下文管理不足**：Agent无法有效利用会话历史进行上下文理解

## 2. 整合目标

### 2.1 高内聚低耦合原则
- **高内聚**：将与会话相关的LLM交互和数据管理整合到统一模块中
- **低耦合**：通过SPI（Service Provider Interface）抽象数据访问层，实现业务逻辑与数据存储的解耦

### 2.2 核心功能
1. 统一会话管理：整合会话创建、更新、删除功能
2. 智能代理交互：在会话上下文中处理用户查询
3. 上下文感知：基于会话历史优化LLM响应
4. 数据访问抽象：通过SPI接口支持多种数据存储方案

## 3. 设计方案

### 3.1 整体架构
```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                        │
├─────────────────────────────────────────────────────────────┤
│                   Conversation Agent                        │
│  ┌─────────────────┐    ┌───────────────────────────────┐  │
│  │  Agent Service  │◄──►│    Conversation Service       │  │
│  └─────────────────┘    └───────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Business Logic Layer                   │
├─────────────────────────────────────────────────────────────┤
│        SPI Interfaces       │        Implementations        │
│  ┌─────────────────────┐   │   ┌────────────────────────┐  │
│  │ ConversationSPI     │◄──┼──►│  DatabaseConversation  │  │
│  │ MessageSPI          │◄──┼──►│   DatabaseMessage      │  │
│  └─────────────────────┘   │   └────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Data Access Layer                      │
├─────────────────────────────────────────────────────────────┤
│          Database Drivers (SQLAlchemy, etc.)              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 核心组件设计

#### 3.2.1 Conversation Agent（会话代理）
- **职责**：统一管理会话和LLM交互
- **功能**：
  - 会话生命周期管理（创建、更新、删除、查询）
  - 在会话上下文中处理用户查询
  - 管理会话历史和上下文
  - 协调Agent Service和Conversation Service

#### 3.2.2 Agent Service（代理服务）
- **职责**：处理LLM交互逻辑
- **功能**：
  - 使用LangGraph编排工具执行
  - 处理用户查询并生成响应
  - 管理工具调用和结果处理
  - 与Conversation Service协作管理上下文

#### 3.2.3 Conversation Service（会话服务）
- **职责**：管理会话和消息数据
- **功能**：
  - 会话和消息的CRUD操作
  - 会话历史查询和管理
  - 通过SPI接口与数据存储交互

### 3.3 SPI接口设计

#### 3.3.1 ConversationSPI接口
```python
class ConversationSPI(ABC):
    """会话数据访问SPI接口"""
    
    @abstractmethod
    async def create_conversation(self, conversation_data: ConversationCreate) -> Conversation:
        """创建会话"""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: UUID) -> Optional[ConversationResponse]:
        """获取会话"""
        pass
    
    @abstractmethod
    async def update_conversation(self, conversation_id: UUID, conversation_data: ConversationUpdate) -> Optional[Conversation]:
        """更新会话"""
        pass
    
    @abstractmethod
    async def delete_conversation(self, conversation_id: UUID) -> bool:
        """删除会话"""
        pass
```

#### 3.3.2 MessageSPI接口
```python
class MessageSPI(ABC):
    """消息数据访问SPI接口"""
    
    @abstractmethod
    async def add_message(self, conversation_id: UUID, message_data: MessageCreate) -> Optional[Message]:
        """添加消息"""
        pass
    
    @abstractmethod
    async def get_messages(self, conversation_id: UUID, limit: int = 50, offset: int = 0) -> List[Message]:
        """获取消息列表"""
        pass
```

### 3.4 数据流设计

#### 3.4.1 用户查询处理流程
1. 用户发起查询请求到Conversation Agent
2. Conversation Agent检查会话是否存在，如不存在则创建新会话
3. Conversation Agent调用Agent Service处理查询
4. Agent Service使用LangGraph处理查询，可能涉及工具调用
5. Agent Service生成响应并返回给Conversation Agent
6. Conversation Agent调用Conversation Service保存用户查询和助手响应
7. Conversation Agent返回最终响应给用户

#### 3.4.2 会话上下文管理
1. 在处理用户查询前，Conversation Agent从数据存储中获取会话历史
2. Conversation Agent将会话历史作为上下文传递给Agent Service
3. Agent Service在LLM调用中使用上下文信息生成更准确的响应
4. 处理完成后，Conversation Agent将会话历史更新到数据存储

## 4. 实现计划

### 4.1 第一阶段：SPI接口和实现
1. 定义ConversationSPI和MessageSPI接口
2. 实现基于数据库的ConversationSPI和MessageSPI实现类
3. 创建SPI工厂用于获取具体实现

### 4.2 第二阶段：服务层重构
1. 重构Conversation Service以使用SPI接口
2. 创建Agent Service处理LLM交互逻辑
3. 实现上下文管理功能

### 4.3 第三阶段：Conversation Agent整合
1. 创建Conversation Agent作为统一入口
2. 实现会话生命周期管理
3. 整合Agent Service和Conversation Service

### 4.4 第四阶段：测试和优化
1. 进行单元测试和集成测试
2. 验证解耦效果和功能完整性
3. 优化性能和错误处理

## 5. 预期收益

### 5.1 架构优势
1. **高内聚**：将相关功能整合到统一模块中，提高代码组织性
2. **低耦合**：通过SPI抽象数据访问，业务逻辑与数据存储解耦
3. **可扩展性**：支持不同的数据存储方案，易于扩展
4. **可测试性**：SPI接口便于模拟和测试

### 5.2 功能改进
1. **上下文感知**：Agent能够基于会话历史生成更准确的响应
2. **统一管理**：通过Conversation Agent统一管理会话和LLM交互
3. **灵活配置**：支持不同的数据存储后端

### 5.3 维护性提升
1. **清晰职责**：各模块职责明确，便于维护和扩展
2. **接口标准化**：SPI接口提供标准化的数据访问方式
3. **降低复杂性**：解耦后的架构降低了系统复杂性