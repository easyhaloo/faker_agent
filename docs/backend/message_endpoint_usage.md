# Message Endpoint Usage

This document explains how to properly use the message endpoint in the Faker Agent API.

## Creating a Conversation

First, create a conversation:

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/?title=My%20Conversation" \
  -H "accept: application/json"
```

This will return a conversation ID that you'll use in subsequent requests.

## Sending Messages

To send a message to a conversation, use the following format:

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/{conversation_id}/messages" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how can you help me today?", "metadata": {}}'
```

### Example with actual conversation ID:

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/8328277d-d2db-43c1-ae7d-e5223f39650e/messages" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好！你能帮我做什么？", "metadata": {}}'
```

### With metadata:

```bash
curl -X POST "http://localhost:8000/api/v1/conversations/8328277d-d2db-43c1-ae7d-e5223f39650e/messages" \
  -H "Content-Type: application/json" \
  -d '{"message": "你好！你能帮我做什么？", "metadata": {"source": "api_client", "priority": "normal"}}'
```

## Key Changes Made

1. **API Parameter Format**: Messages are now sent in the request body as JSON rather than as query parameters.

2. **Data Validation**: Added proper validation for `tool_calls` and `metadata` fields to handle database storage format differences.

3. **Pydantic V2 Compatibility**: Updated all models to use `from_attributes = True` instead of the deprecated `orm_mode = True`.

## Error Handling

If you encounter errors, check:
1. That you're using the correct Content-Type header (`application/json`)
2. That your message is properly formatted as JSON
3. That you're using the correct conversation ID
4. That the backend service is running

## Response Format

Successful responses will follow this format:
```json
{
  "status": "success",
  "data": {
    // Response data here
  }
}
```

Error responses will follow this format:
```json
{
  "status": "error",
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description"
  }
}
```