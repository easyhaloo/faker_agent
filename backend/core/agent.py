"""
Conversation agent integration for the Faker Agent.

This module provides a unified interface that integrates the agent service
with the conversation service, implementing high cohesion and low coupling
principles with SPI-based data access abstraction.
"""
from typing import Any, Dict, List, Optional
from uuid import UUID

from backend.core.services.agent_service import AgentService
from backend.core.services.conversation_service import conversation_service
from backend.core.services.memory_service import enhanced_memory_service
from backend.core.models.conversation import (
    ConversationCreate, ConversationUpdate, MessageCreate
)
from backend.core.models.memory import MemorySettings
from backend.core.utils.logging import get_logger

# Configure logger
logger = get_logger(__name__)


class ConversationAgent:
    """Unified agent that integrates conversation management with LLM processing."""
    
    def __init__(self):
        """Initialize the conversation agent with required services."""
        self.agent_service = AgentService()
        self.conversation_service = conversation_service
        self.memory_service = enhanced_memory_service
        
        # Use elegant logging for initialization
        from backend.core.utils.logging import log_initialization
        log_initialization(
            "ConversationAgent",
            "with integrated services",
            agent_service=True,
            conversation_service=True,
            memory_service=True
        )
    
    async def create_conversation(self, title: str = "New Conversation", metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a new conversation.
        
        Args:
            title: The title for the new conversation
            metadata: Optional metadata for the conversation
            
        Returns:
            Dictionary with conversation creation result
        """
        try:
            conversation_data = ConversationCreate(title=title, metadata=metadata)
            conversation = await self.conversation_service.create_conversation(conversation_data)
            
            return {
                "status": "success",
                "data": {
                    "conversation_id": conversation.id,
                    "title": conversation.title,
                    "created_at": conversation.created_at
                }
            }
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            return {
                "status": "error",
                "error": {
                    "code": "CONVERSATION_CREATION_ERROR",
                    "message": str(e)
                }
            }
    
    async def process_message(
        self, 
        conversation_id: UUID, 
        user_message: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a user message within a conversation context.
        
        This method integrates:
        1. Conversation management (adding messages)
        2. Memory retrieval (context, profiles, summaries)
        3. LLM processing with context
        4. Result storage (conversation updates)
        
        Args:
            conversation_id: The ID of the conversation
            user_message: The user's message
            metadata: Optional metadata for the message
            
        Returns:
            Dictionary with processing result
        """
        try:
            # 1. Add user message to conversation
            user_message_data = MessageCreate(
                role="user",
                content=user_message,
                metadata=metadata
            )
            user_msg = await self.conversation_service.add_message(conversation_id, user_message_data)
            
            if not user_msg:
                return {
                    "status": "error",
                    "error": {
                        "code": "MESSAGE_ADD_ERROR",
                        "message": "Failed to add user message to conversation"
                    }
                }
            
            # 2. Get memory settings
            memory_settings = await self.memory_service.get_memory_settings()
            
            # 3. Retrieve relevant memories for context
            memory_context = await self.memory_service.get_memory_for_prompt(
                conversation_id=conversation_id,
                user_message=user_message,
                settings=memory_settings
            )
            
            # 4. Prepare context messages for the LLM
            context_messages = []
            
            # Add conversation summary if available
            if memory_context.get("summary"):
                context_messages.append({
                    "role": "system",
                    "content": f"Conversation summary: {memory_context['summary'].content}"
                })
            
            # Add recent conversation context
            for msg in memory_context.get("recent_context", []):
                context_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # 5. Process query with context through agent service
            agent_result = await self.agent_service.process_query_with_context(
                query=user_message,
                context_messages=context_messages
            )
            
            if agent_result["status"] != "success":
                return agent_result
            
            # 6. Add assistant response to conversation
            assistant_content = agent_result["data"]["result"]
            assistant_message_data = MessageCreate(
                role="assistant",
                content=assistant_content,
                metadata={"source": "llm_response"}
            )
            assistant_msg = await self.conversation_service.add_message(conversation_id, assistant_message_data)
            
            if not assistant_msg:
                return {
                    "status": "error",
                    "error": {
                        "code": "RESPONSE_ADD_ERROR",
                        "message": "Failed to add assistant response to conversation"
                    }
                }
            
            # 7. Extract and store memories from the conversation
            if memory_settings.enable_memory_writing:
                # Extract facts from user message
                extracted_memories = await self.memory_service.extract_facts_from_message(user_msg)
                
                # Store extracted memories
                for memory_item in extracted_memories:
                    # Store as episode memory for now
                    # In a more sophisticated implementation, we would categorize by type
                    pass  # Implementation would go here
            
            # 8. Return successful result
            return {
                "status": "success",
                "data": {
                    "conversation_id": conversation_id,
                    "user_message_id": user_msg.id,
                    "assistant_message_id": assistant_msg.id,
                    "result": assistant_content,
                    "actions": agent_result["data"].get("actions", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "status": "error",
                "error": {
                    "code": "MESSAGE_PROCESSING_ERROR",
                    "message": str(e)
                }
            }
    
    async def get_conversation_history(
        self, 
        conversation_id: UUID, 
        limit: int = 50, 
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Get conversation history with messages.
        
        Args:
            conversation_id: The ID of the conversation
            limit: Maximum number of messages to return
            offset: Number of messages to skip
            
        Returns:
            Dictionary with conversation history
        """
        try:
            # Get conversation details
            conversation = await self.conversation_service.get_conversation(conversation_id)
            if not conversation:
                return {
                    "status": "error",
                    "error": {
                        "code": "CONVERSATION_NOT_FOUND",
                        "message": "Conversation not found"
                    }
                }
            
            # Get messages
            messages = await self.conversation_service.get_messages(conversation_id, limit, offset)
            
            return {
                "status": "success",
                "data": {
                    "conversation": conversation,
                    "messages": [msg.dict() for msg in messages]
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return {
                "status": "error",
                "error": {
                    "code": "HISTORY_RETRIEVAL_ERROR",
                    "message": str(e)
                }
            }
    
    async def list_conversations(self, page: int = 1, page_size: int = 20) -> Dict[str, Any]:
        """
        List all conversations with pagination.
        
        Args:
            page: Page number (1-based)
            page_size: Number of conversations per page
            
        Returns:
            Dictionary with conversations list and pagination info
        """
        try:
            result = await self.conversation_service.list_conversations(page, page_size)
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"Error listing conversations: {e}")
            return {
                "status": "error",
                "error": {
                    "code": "CONVERSATION_LIST_ERROR",
                    "message": str(e)
                }
            }
    
    async def update_conversation(
        self, 
        conversation_id: UUID, 
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update conversation details.
        
        Args:
            conversation_id: The ID of the conversation to update
            title: New title for the conversation
            metadata: New metadata for the conversation
            
        Returns:
            Dictionary with update result
        """
        try:
            update_data = ConversationUpdate(title=title, metadata=metadata)
            conversation = await self.conversation_service.update_conversation(conversation_id, update_data)
            
            if not conversation:
                return {
                    "status": "error",
                    "error": {
                        "code": "CONVERSATION_NOT_FOUND",
                        "message": "Conversation not found"
                    }
                }
            
            return {
                "status": "success",
                "data": {
                    "conversation_id": conversation.id,
                    "title": conversation.title,
                    "updated_at": conversation.updated_at
                }
            }
        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
            return {
                "status": "error",
                "error": {
                    "code": "CONVERSATION_UPDATE_ERROR",
                    "message": str(e)
                }
            }
    
    async def delete_conversation(self, conversation_id: UUID) -> Dict[str, Any]:
        """
        Delete a conversation and all its messages.
        
        Args:
            conversation_id: The ID of the conversation to delete
            
        Returns:
            Dictionary with deletion result
        """
        try:
            success = await self.conversation_service.delete_conversation(conversation_id)
            
            if not success:
                return {
                    "status": "error",
                    "error": {
                        "code": "CONVERSATION_NOT_FOUND",
                        "message": "Conversation not found"
                    }
                }
            
            return {
                "status": "success",
                "message": "Conversation deleted successfully"
            }
        except Exception as e:
            logger.error(f"Error deleting conversation: {e}")
            return {
                "status": "error",
                "error": {
                    "code": "CONVERSATION_DELETE_ERROR",
                    "message": str(e)
                }
            }


# Global conversation agent instance
conversation_agent = ConversationAgent()