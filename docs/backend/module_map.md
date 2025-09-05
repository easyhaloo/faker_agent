# Faker Agent Module Map

## Overview

This document provides a clear mapping of modules in the Faker Agent backend, indicating which ones should be used going forward and which ones should be considered deprecated. This map is based on the time dimension analysis, with newer and more comprehensive implementations taking precedence.

## Module Status Legend

- ✅ **Primary** - The primary implementation that should be used going forward
- ⚠️ **Legacy** - Older implementation that should be considered deprecated
- 🔄 **Transitional** - Module that is being refactored to act as a wrapper or compatibility layer
- 🆕 **New** - Recently added module that represents the latest architecture

## LLM Integration Modules

| Module Path | Status | Last Modified | Notes |
|-------------|--------|---------------|-------|
| `backend/core/infrastructure/llm/litellm_client.py` | ✅ Primary | Aug 31 13:32 | Main LiteLLM client implementation |
| `backend/core/infrastructure/llm/factory.py` | ✅ Primary | Aug 31 00:15 | Factory for creating LLM clients |
| `backend/core/infrastructure/llm/llm_port_impl.py` | ✅ Primary | Aug 31 00:15 | LLM port implementation |
| `backend/core/infrastructure/llm/litellm_custom.py` | ✅ Primary | Aug 31 00:15 | Custom LiteLLM implementation |
| `backend/core/llm/litellm_chat_model.py` | ⚠️ Legacy | Aug 30 09:49 | Older LiteLLM implementation |
| `backend/core/llm/chat_model_factory.py` | ⚠️ Legacy | Aug 30 09:49 | Older factory implementation |
| `backend/core/llm/agent_utils.py` | ⚠️ Legacy | Aug 30 10:14 | Older agent utilities |

## Agent Implementation Modules

| Module Path | Status | Last Modified | Notes |
|-------------|--------|---------------|-------|
| `backend/core/graph/flow_orchestrator.py` | ✅ Primary | Aug 31 16:13 | Main orchestrator implementation |
| `backend/core/graph/agent_graph.py` | ✅ Primary | Aug 31 00:45 | LangGraph implementation |
| `backend/core/agent.py` | 🔄 Transitional | Aug 31 16:12 | Simplified wrapper |
| `backend/core/assembler/llm_assembler.py` | ✅ Primary | Aug 31 00:38 | Tool chain assembler |

## API Modules

| Module Path | Status | Last Modified | Notes |
|-------------|--------|---------------|-------|
| `backend/api/agent_routes.py` | ✅ Primary | Aug 31 16:14 | Enhanced agent API routes |
| `backend/api/integrated_agent_routes.py` | 🆕 New | Sep 5 17:30 | Integrated agent and conversation management |
| `backend/api/routes.py` | ✅ Primary | Aug 31 17:04 | Main router |

## Protocol Modules

| Module Path | Status | Last Modified | Notes |
|-------------|--------|---------------|-------|
| `backend/core/protocol/sse_protocol.py` | ✅ Primary | Aug 31 15:24 | SSE protocol handler |
| `backend/core/protocol/protocol_factory.py` | ✅ Primary | - | Protocol factory |

## Tool Modules

| Module Path | Status | Last Modified | Notes |
|-------------|--------|---------------|-------|
| `backend/core/tools/registry.py` | ✅ Primary | Aug 31 00:34 | Tool registry |
| `backend/core/tools/base.py` | ✅ Primary | - | Base tool classes |
| `backend/core/tools/filtered_registry.py` | ✅ Primary | - | Filtered tool registry |

## Import Guidance

When importing modules, follow these guidelines:

### LLM Integration

```python
# ✅ Use these imports
from backend.core.infrastructure.llm.factory import llm_factory
from backend.core.infrastructure.llm.litellm_client import LiteLLMClient

# ⚠️ Avoid these imports
from backend.core.llm.chat_model_factory import get_chat_model  # Legacy
from backend.core.llm.litellm_chat_model import LiteLLMChatModel  # Legacy
```

### Agent Implementation

```python
# ✅ Use these imports
from backend.core.graph.flow_orchestrator import FlowOrchestrator
from backend.core.graph.agent_graph import AgentGraph

# 🔄 Use for backwards compatibility only
from backend.core.agent import Agent  # Transitional wrapper
```

### API Routes

```python
# ✅ Use these imports
from backend.api.agent_routes import router as agent_router
from backend.api.integrated_agent_routes import router as integrated_agent_router
from backend.api.routes import router as api_router
```

## Module Dependencies

The following diagram illustrates the key dependencies between the primary modules:

```
API Layer
  ├── agent_routes.py ───────────┐
  ├── integrated_agent_routes.py │
  └── routes.py                  ▼
                          ConversationAgent
                                  │
                                  ▼
                          FlowOrchestrator
                           /          \
                          /            \
                         ▼              ▼
                  LLMAdapter       ToolRegistry
                      │
                      ▼
                LiteLLMClient
```

## Migration Path

For modules marked as Legacy (⚠️), the migration path is as follows:

1. **LLM Integration**:
   - Replace `backend/core/llm/chat_model_factory.py` with `backend/core/infrastructure/llm/factory.py`
   - Replace `backend/core/llm/litellm_chat_model.py` with `backend/core/infrastructure/llm/litellm_client.py`

2. **Agent Implementation**:
   - Phase out direct usage of `Agent` class in favor of `FlowOrchestrator`

3. **Utility Functions**:
   - Move unique functionality from legacy modules to appropriate primary modules
   - Update imports throughout the codebase

## Conclusion

By following this module map, developers can ensure they're using the most up-to-date and appropriate modules in the Faker Agent backend. This will help eliminate redundancies, improve code organization, and make the system easier to understand and extend.