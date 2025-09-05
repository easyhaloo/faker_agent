"""
Enhanced memory service for the Faker Agent with optimized conversation memory management.

This module provides services for managing different types of memory with improved
token efficiency and context retention:
- Short-term (working memory) with sliding window optimization
- Session-level episodic memory with semantic retrieval
- Global profile memory with caching
- Hierarchical conversation summaries
- Memory compression for efficient storage

It includes CRUD operations for memory entities and functions for
memory extraction, retrieval, and integration with the agent system.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any, Union, Tuple
from uuid import UUID

from backend.core.models.memory import (
    MemoryProfile, MemoryEpisode, ConversationSummary, MemoryAudit,
    MemoryProfileCreate, MemoryEpisodeCreate, MemorySettings,
    MemoryType, MemoryScope
)
from backend.core.models.conversation import Message, Conversation, ToolCall


class EnhancedMemoryService:
    """Enhanced service for managing agent memory operations with optimized strategies."""
    
    def __init__(self):
        """Initialize the enhanced memory service."""
        # In a production implementation, these would be initialized with actual models
        self.embedding_model = None  # SentenceTransformer or similar embedding model
        self.vector_db = None  # Vector database connection (Pinecone, Weaviate, etc.)
        
    async def create_profile_memory(self, memory: MemoryProfileCreate) -> MemoryProfile:
        """
        Create a new profile memory entry.
        
        Args:
            memory: The memory profile to create
            
        Returns:
            The created memory profile
        """
        # Create a new database record
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryProfileDB
        
        with db_session() as db:
            db_memory = MemoryProfileDB(
                user_id="default_user",
                scope=memory.scope,
                project_id=memory.project_id,
                key=memory.key,
                value=memory.value,
                memory_type=memory.memory_type,
                tags=memory.tags,
                source_msg_id=memory.source_msg_id,
                expires_at=memory.expires_at,
                extra_data=memory.metadata
            )
            db.add(db_memory)
            db.commit()
            db.refresh(db_memory)
            
            # Convert DB model to Pydantic model
            memory_profile = MemoryProfile.from_orm(db_memory)
        
        # Log the audit
        await self.log_memory_action(
            actor="system",
            action="create",
            target_id=memory_profile.id,
            target_type="profile",
            details={"memory": memory_profile.dict()}
        )
        
        return memory_profile
    
    async def get_profile_memories(
        self, 
        scope: Optional[MemoryScope] = None,
        project_id: Optional[UUID] = None,
        memory_type: Optional[MemoryType] = None,
        key: Optional[str] = None,
        user_id: str = "default_user"
    ) -> List[MemoryProfile]:
        """
        Get profile memories based on filters.
        
        Args:
            scope: Filter by memory scope
            project_id: Filter by project ID
            memory_type: Filter by memory type
            key: Filter by key
            user_id: Filter by user ID
            
        Returns:
            List of matching memory profiles
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryProfileDB
        from sqlalchemy import and_
        
        filters = []
        if scope:
            filters.append(MemoryProfileDB.scope == scope)
        if project_id:
            filters.append(MemoryProfileDB.project_id == project_id)
        if memory_type:
            filters.append(MemoryProfileDB.memory_type == memory_type)
        if key:
            filters.append(MemoryProfileDB.key == key)
        if user_id:
            filters.append(MemoryProfileDB.user_id == user_id)
            
        with db_session() as db:
            query = db.query(MemoryProfileDB)
            if filters:
                query = query.filter(and_(*filters))
                
            db_memories = query.all()
            memories = [MemoryProfile.from_orm(m) for m in db_memories]
            
        return memories
    
    async def update_profile_memory(
        self, 
        memory_id: UUID, 
        updates: Dict[str, Any]
    ) -> MemoryProfile:
        """
        Update an existing profile memory.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            The updated memory profile
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryProfileDB
        
        with db_session() as db:
            db_memory = db.query(MemoryProfileDB).filter(MemoryProfileDB.id == memory_id).first()
            
            if not db_memory:
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(db_memory, key):
                    setattr(db_memory, key, value)
                    
            db.commit()
            db.refresh(db_memory)
            
            # Convert to Pydantic model
            memory_profile = MemoryProfile.from_orm(db_memory)
        
        # Log the audit
        await self.log_memory_action(
            actor="system",
            action="update",
            target_id=memory_id,
            target_type="profile",
            details={"updates": updates}
        )
        
        return memory_profile
    
    async def delete_profile_memory(self, memory_id: UUID) -> bool:
        """
        Delete a profile memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryProfileDB
        
        with db_session() as db:
            db_memory = db.query(MemoryProfileDB).filter(MemoryProfileDB.id == memory_id).first()
            
            if not db_memory:
                return False
                
            db.delete(db_memory)
            db.commit()
        
        # Log the audit
        await self.log_memory_action(
            actor="system",
            action="delete",
            target_id=memory_id,
            target_type="profile",
            details={}
        )
        
        return True
    
    async def create_episode_memory(self, memory: MemoryEpisodeCreate) -> MemoryEpisode:
        """
        Create a new episode memory entry.
        
        Args:
            memory: The episode memory to create
            
        Returns:
            The created episode memory
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryEpisodeDB
        
        with db_session() as db:
            db_memory = MemoryEpisodeDB(
                conversation_id=memory.conversation_id,
                memory_type=memory.memory_type,
                title=memory.title,
                content=memory.content,
                tags=memory.tags,
                source_msg_id=memory.source_msg_id,
                expires_at=memory.expires_at,
                extra_data=memory.metadata
            )
            db.add(db_memory)
            db.commit()
            db.refresh(db_memory)
            
            # Convert DB model to Pydantic model
            memory_episode = MemoryEpisode.from_orm(db_memory)
        
        # Log the audit
        await self.log_memory_action(
            actor="system",
            action="create",
            target_id=memory_episode.id,
            target_type="episode",
            details={"memory": memory_episode.dict()}
        )
        
        return memory_episode
    
    async def get_episode_memories(
        self, 
        conversation_id: UUID,
        memory_type: Optional[MemoryType] = None
    ) -> List[MemoryEpisode]:
        """
        Get episode memories for a conversation.
        
        Args:
            conversation_id: ID of the conversation
            memory_type: Filter by memory type
            
        Returns:
            List of matching episode memories
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryEpisodeDB
        from sqlalchemy import and_
        
        filters = [MemoryEpisodeDB.conversation_id == conversation_id]
        if memory_type:
            filters.append(MemoryEpisodeDB.memory_type == memory_type)
            
        with db_session() as db:
            query = db.query(MemoryEpisodeDB).filter(and_(*filters))
            db_memories = query.all()
            memories = [MemoryEpisode.from_orm(m) for m in db_memories]
            
        return memories
    
    async def update_episode_memory(
        self, 
        memory_id: UUID, 
        updates: Dict[str, Any]
    ) -> MemoryEpisode:
        """
        Update an existing episode memory.
        
        Args:
            memory_id: ID of the memory to update
            updates: Dictionary of fields to update
            
        Returns:
            The updated episode memory
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryEpisodeDB
        
        with db_session() as db:
            db_memory = db.query(MemoryEpisodeDB).filter(MemoryEpisodeDB.id == memory_id).first()
            
            if not db_memory:
                return None
                
            # Update fields
            for key, value in updates.items():
                if hasattr(db_memory, key):
                    setattr(db_memory, key, value)
                    
            db.commit()
            db.refresh(db_memory)
            
            # Convert to Pydantic model
            memory_episode = MemoryEpisode.from_orm(db_memory)
        
        # Log the audit
        await self.log_memory_action(
            actor="system",
            action="update",
            target_id=memory_id,
            target_type="episode",
            details={"updates": updates}
        )
        
        return memory_episode
    
    async def delete_episode_memory(self, memory_id: UUID) -> bool:
        """
        Delete an episode memory.
        
        Args:
            memory_id: ID of the memory to delete
            
        Returns:
            True if successful, False otherwise
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryEpisodeDB
        
        with db_session() as db:
            db_memory = db.query(MemoryEpisodeDB).filter(MemoryEpisodeDB.id == memory_id).first()
            
            if not db_memory:
                return False
                
            db.delete(db_memory)
            db.commit()
        
        # Log the audit
        await self.log_memory_action(
            actor="system",
            action="delete",
            target_id=memory_id,
            target_type="episode",
            details={}
        )
        
        return True
    
    async def create_conversation_summary(
        self,
        conversation_id: UUID,
        content: str,
        range_start_msg_id: UUID,
        range_end_msg_id: UUID,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ConversationSummary:
        """
        Create a new conversation summary.
        
        Args:
            conversation_id: ID of the conversation
            content: Summary content
            range_start_msg_id: First message ID in the summarized range
            range_end_msg_id: Last message ID in the summarized range
            metadata: Optional metadata
            
        Returns:
            The created conversation summary
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import ConversationSummaryDB
        
        with db_session() as db:
            db_summary = ConversationSummaryDB(
                conversation_id=conversation_id,
                content=content,
                range_start_msg_id=range_start_msg_id,
                range_end_msg_id=range_end_msg_id,
                extra_data=metadata
            )
            db.add(db_summary)
            db.commit()
            db.refresh(db_summary)
            
            # Convert DB model to Pydantic model
            summary = ConversationSummary.from_orm(db_summary)
        
        # Log the audit
        await self.log_memory_action(
            actor="system",
            action="create",
            target_id=summary.id,
            target_type="summary",
            details={"summary": summary.dict()}
        )
        
        return summary
    
    async def get_latest_summary(self, conversation_id: UUID) -> Optional[ConversationSummary]:
        """
        Get the latest conversation summary.
        
        Args:
            conversation_id: ID of the conversation
            
        Returns:
            The latest summary or None if no summary exists
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import ConversationSummaryDB
        
        with db_session() as db:
            db_summary = db.query(ConversationSummaryDB)\
                .filter(ConversationSummaryDB.conversation_id == conversation_id)\
                .order_by(ConversationSummaryDB.created_at.desc())\
                .first()
            
            if not db_summary:
                return None
                
            return ConversationSummary.from_orm(db_summary)
    
    async def get_hierarchical_summaries(self, conversation_id: UUID, max_levels: int = 3) -> List[ConversationSummary]:
        """
        Get hierarchical conversation summaries for very long conversations.
        
        Args:
            conversation_id: ID of the conversation
            max_levels: Maximum number of summary levels to retrieve
            
        Returns:
            List of conversation summaries in hierarchical order
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import ConversationSummaryDB
        
        summaries = []
        with db_session() as db:
            # Get summaries ordered by creation time (newest first)
            db_summaries = db.query(ConversationSummaryDB)\
                .filter(ConversationSummaryDB.conversation_id == conversation_id)\
                .order_by(ConversationSummaryDB.created_at.desc())\
                .limit(max_levels)\
                .all()
            
            summaries = [ConversationSummary.from_orm(s) for s in db_summaries]
            
        return summaries
    
    async def extract_facts_from_message(self, message: Message) -> List[Dict[str, Any]]:
        """
        Extract facts and other memory-worthy information from a message.
        
        This function analyzes message content to identify information that
        should be persisted in memory, such as facts, goals, preferences, etc.
        
        Args:
            message: The message to extract information from
            
        Returns:
            List of extracted memory items with type, content, and metadata
        """
        from backend.core.infrastructure.llm.chat_model import get_chat_model
        
        # Only extract from user messages
        if message.role != "user":
            return []
            
        # Use LLM to extract memory items
        chat_model = get_chat_model()
        
        from backend.core.prompts.memory_prompts import MEMORY_EXTRACTION_PROMPT
        
        # Construct prompt for extraction
        prompt = [
            {"role": "system", "content": MEMORY_EXTRACTION_PROMPT}, 
            {"role": "user", "content": f"Extract memory items from this message:\n\n{message.content}"}
        ]
        
        try:
            response = await chat_model.complete(prompt)
            
            # Parse the response and extract the JSON
            import json
            import re
            
            # Find JSON array pattern in the response
            json_match = re.search(r'\[\s*{.*}\s*\]', response.replace('\n', ' '), re.DOTALL)
            
            if json_match:
                memory_items = json.loads(json_match.group(0))
                
                # Add metadata
                for item in memory_items:
                    item["metadata"] = {
                        "source": "llm_extraction",
                        "confidence": item.get("importance", 3) / 5.0,
                        "extracted_at": str(datetime.now())
                    }
                    
                return memory_items
            
            return []
        except Exception as e:
            # Log the error but don't fail the whole operation
            from backend.core.utils.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error extracting memory from message: {e}")
            return []
    
    async def should_create_summary(
        self, 
        conversation_id: UUID, 
        recent_messages: List[Message],
        settings: MemorySettings
    ) -> bool:
        """
        Determine if a new summary should be created based on conversation length.
        
        Args:
            conversation_id: ID of the conversation
            recent_messages: Recent messages in the conversation
            settings: Memory settings with thresholds
            
        Returns:
            True if a new summary should be created, False otherwise
        """
        # Simple token counting logic (in reality would be more sophisticated)
        total_tokens = sum(len(msg.content.split()) * 1.3 for msg in recent_messages)
        return total_tokens > settings.summary_token_threshold
    
    async def generate_summary(
        self,
        conversation_id: UUID,
        messages: List[Message],
        previous_summary: Optional[ConversationSummary] = None
    ) -> str:
        """
        Generate a summary of conversation messages.
        
        Args:
            conversation_id: ID of the conversation
            messages: Messages to summarize
            previous_summary: Previous summary to update
            
        Returns:
            Generated summary text
        """
        from backend.core.infrastructure.llm.chat_model import get_chat_model
        
        # Use LLM to generate summary
        chat_model = get_chat_model()
        
        # Prepare the conversation context
        conversation_content = ""
        for msg in messages:
            role = "User" if msg.role == "user" else "Assistant"
            conversation_content += f"{role}: {msg.content}\n\n"
            
        from backend.core.prompts.memory_prompts import MEMORY_SUMMARIZATION_PROMPT
        
        # Construct prompt for summarization
        system_prompt = MEMORY_SUMMARIZATION_PROMPT
        
        user_prompt = """
        Please summarize the following conversation:
        
        {previous_summary_text}
        
        {conversation_content}
        """
        
        previous_summary_text = ""
        if previous_summary:
            previous_summary_text = f"Previous summary: {previous_summary.content}\n\n"
            
        prompt = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt.format(
                previous_summary_text=previous_summary_text,
                conversation_content=conversation_content
            )}
        ]
        
        try:
            response = await chat_model.complete(prompt)
            return response.strip()
        except Exception as e:
            # Log the error but fall back to a simple concatenation
            from backend.core.utils.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error generating summary: {e}")
            
            # Fallback to simple concatenation
            summary_parts = []
            
            if previous_summary:
                summary_parts.append(f"Previous context: {previous_summary.content}")
            
            # Extract key points from each message
            for msg in messages:
                if msg.role == "user":
                    summary_parts.append(f"User asked: {msg.content[:50]}...")
                elif msg.role == "assistant":
                    summary_parts.append(f"Assistant replied: {msg.content[:50]}...")
            
            return " ".join(summary_parts)
    
    async def compress_memory_content(self, content: str, compression_ratio: float = 0.5) -> str:
        """
        Compress memory content to reduce token usage while preserving key information.
        
        Args:
            content: The content to compress
            compression_ratio: Target ratio of compressed to original length (0.0-1.0)
            
        Returns:
            Compressed content
        """
        from backend.core.infrastructure.llm.chat_model import get_chat_model
        
        # Use LLM to compress content
        chat_model = get_chat_model()
        
        from backend.core.prompts.memory_prompts import MEMORY_COMPRESSION_PROMPT
        
        # Construct prompt for compression
        prompt = [
            {"role": "system", "content": MEMORY_COMPRESSION_PROMPT.format(compression_ratio=compression_ratio * 100)}, 
            {"role": "user", "content": f"Compress this content:\n\n{content}"}
        ]
        
        try:
            response = await chat_model.complete(prompt)
            return response.strip()
        except Exception as e:
            # Log the error but return original content if compression fails
            from backend.core.utils.logging import get_logger
            logger = get_logger(__name__)
            logger.error(f"Error compressing memory content: {e}")
            return content
    
    async def get_sliding_window_context(
        self, 
        conversation_id: UUID, 
        max_messages: int = 10
    ) -> List[Message]:
        """
        Get recent messages using a sliding window approach.
        
        Args:
            conversation_id: ID of the conversation
            max_messages: Maximum number of recent messages to retrieve
            
        Returns:
            List of recent messages
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MessageDB
        from sqlalchemy import desc
        
        with db_session() as db:
            # Get recent messages ordered by creation time (newest first)
            db_messages = db.query(MessageDB)\
                .filter(MessageDB.conversation_id == conversation_id)\
                .order_by(desc(MessageDB.created_at))\
                .limit(max_messages)\
                .all()
            
            # Convert to Pydantic models and reverse order (oldest first)
            messages = [Message.from_orm(m) for m in reversed(db_messages)]
            
        return messages
    
    async def get_semantic_memories(
        self, 
        conversation_id: UUID, 
        query: str, 
        max_memories: int = 5
    ) -> List[MemoryEpisode]:
        """
        Get semantically relevant memories using vector similarity search.
        
        Args:
            conversation_id: ID of the conversation
            query: Query text to find relevant memories
            max_memories: Maximum number of memories to retrieve
            
        Returns:
            List of semantically relevant memories
        """
        # In a production implementation, this would use a vector database
        # For now, we'll use a simplified approach with keyword matching
        
        # Get all episode memories for this conversation
        all_memories = await self.get_episode_memories(conversation_id=conversation_id)
        
        # Score memories based on relevance to query
        scored_memories = []
        query_words = set(query.lower().split())
        
        for memory in all_memories:
            # Simple keyword matching score
            memory_words = set(memory.content.lower().split())
            common_words = query_words.intersection(memory_words)
            score = len(common_words) / len(query_words) if query_words else 0
            
            # Boost score for recent memories
            time_diff = (datetime.now() - memory.created_at).total_seconds()
            recency_boost = max(0.1, 1.0 - (time_diff / (24 * 3600)))  # Boost for last 24 hours
            
            # Boost score for important memory types
            importance_boost = 1.0
            if memory.memory_type in [MemoryType.GOAL, MemoryType.DECISION, MemoryType.CONSTRAINT]:
                importance_boost = 1.5
            
            final_score = score * recency_boost * importance_boost
            scored_memories.append((final_score, memory))
        
        # Sort by score and return top memories
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        top_memories = [memory for score, memory in scored_memories[:max_memories]]
        
        return top_memories
    
    async def get_memory_for_prompt(
        self,
        conversation_id: UUID,
        user_message: str,
        settings: MemorySettings
    ) -> Dict[str, Any]:
        """
        Retrieve relevant memory items to include in the prompt with optimized strategies.
        
        Args:
            conversation_id: ID of the conversation
            user_message: Current user message
            settings: Memory settings
            
        Returns:
            Dictionary with different memory types to include in the prompt
        """
        result = {
            "profile_memory": [],
            "episode_memory": [],
            "summary": None,
            "recent_context": [],
            "semantic_memories": []
        }
        
        # Only proceed if memory is enabled
        if not (settings.use_global_memory or settings.use_project_memory or settings.use_session_memory):
            return result
        
        # Get recent context using sliding window
        if settings.use_session_memory:
            result["recent_context"] = await self.get_sliding_window_context(
                conversation_id=conversation_id,
                max_messages=settings.max_context_messages
            )
        
        # Get profile memories if enabled
        if settings.use_global_memory:
            global_memories = await self.get_profile_memories(scope=MemoryScope.GLOBAL)
            result["profile_memory"].extend(global_memories)
        
        if settings.use_project_memory and settings.project_id:
            project_memories = await self.get_profile_memories(
                scope=MemoryScope.PROJECT,
                project_id=settings.project_id
            )
            result["profile_memory"].extend(project_memories)
        
        # Get session memories if enabled
        if settings.use_session_memory:
            episode_memories = await self.get_episode_memories(conversation_id=conversation_id)
            result["episode_memory"] = episode_memories
            
            # Get semantically relevant memories
            result["semantic_memories"] = await self.get_semantic_memories(
                conversation_id=conversation_id,
                query=user_message,
                max_memories=5
            )
            
            # Get the latest summary if rolling summaries are enabled
            if settings.enable_rolling_summary:
                result["summary"] = await self.get_latest_summary(conversation_id=conversation_id)
        
        return result
    
    async def log_memory_action(
        self,
        actor: str,
        action: str,
        target_id: UUID,
        target_type: str,
        details: Dict[str, Any]
    ) -> MemoryAudit:
        """
        Log a memory-related action for auditing.
        
        Args:
            actor: Who performed the action
            action: Action performed
            target_id: ID of the affected memory
            target_type: Type of memory affected
            details: Additional details about the action
            
        Returns:
            The created audit entry
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryAuditDB
        
        with db_session() as db:
            db_audit = MemoryAuditDB(
                actor=actor,
                action=action,
                target_id=target_id,
                target_type=target_type,
                details=details
            )
            db.add(db_audit)
            db.commit()
            db.refresh(db_audit)
            
            # Convert DB model to Pydantic model
            audit = MemoryAudit(
                id=db_audit.id,
                actor=db_audit.actor,
                action=db_audit.action,
                target_id=db_audit.target_id,
                target_type=db_audit.target_type,
                details=db_audit.details,
                created_at=db_audit.created_at
            )
            
        return audit

    async def get_memory_settings(
        self,
        user_id: str = "default_user"
    ) -> MemorySettings:
        """
        Get memory settings for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            The memory settings
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemorySettingsDB
        
        with db_session() as db:
            db_settings = db.query(MemorySettingsDB).filter(
                MemorySettingsDB.user_id == user_id
            ).first()
            
            if not db_settings:
                # Return default settings if not found
                return MemorySettings()
                
            # Convert DB model to Pydantic model
            settings = MemorySettings(
                use_global_memory=db_settings.use_global_memory,
                use_project_memory=db_settings.use_project_memory,
                project_id=db_settings.project_id,
                use_session_memory=db_settings.use_session_memory,
                enable_memory_writing=db_settings.enable_memory_writing,
                enable_rolling_summary=db_settings.enable_rolling_summary,
                max_context_messages=db_settings.max_context_messages,
                summary_token_threshold=db_settings.summary_token_threshold
            )
            
        return settings
    
    async def create_or_update_memory_settings(
        self,
        settings: MemorySettings,
        user_id: str = "default_user"
    ) -> MemorySettings:
        """
        Create or update memory settings for a user.
        
        Args:
            settings: The memory settings
            user_id: The user ID
            
        Returns:
            The updated memory settings
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemorySettingsDB
        
        with db_session() as db:
            db_settings = db.query(MemorySettingsDB).filter(
                MemorySettingsDB.user_id == user_id
            ).first()
            
            if not db_settings:
                # Create new settings
                db_settings = MemorySettingsDB(
                    user_id=user_id,
                    use_global_memory=settings.use_global_memory,
                    use_project_memory=settings.use_project_memory,
                    project_id=settings.project_id,
                    use_session_memory=settings.use_session_memory,
                    enable_memory_writing=settings.enable_memory_writing,
                    enable_rolling_summary=settings.enable_rolling_summary,
                    max_context_messages=settings.max_context_messages,
                    summary_token_threshold=settings.summary_token_threshold,
                    extra_data=None
                )
                db.add(db_settings)
            # Update existing settings
                db_settings.use_global_memory = settings.use_global_memory
                db_settings.use_project_memory = settings.use_project_memory
                db_settings.project_id = settings.project_id
                db_settings.use_session_memory = settings.use_session_memory
                db_settings.enable_memory_writing = settings.enable_memory_writing
                db_settings.enable_rolling_summary = settings.enable_rolling_summary
                db_settings.max_context_messages = settings.max_context_messages
                db_settings.summary_token_threshold = settings.summary_token_threshold
                db_settings.extra_data = None
                
            db.commit()
            db.refresh(db_settings)
            
            # Convert DB model to Pydantic model
            result = MemorySettings(
                use_global_memory=db_settings.use_global_memory,
                use_project_memory=db_settings.use_project_memory,
                project_id=db_settings.project_id,
                use_session_memory=db_settings.use_session_memory,
                enable_memory_writing=db_settings.enable_memory_writing,
                enable_rolling_summary=db_settings.enable_rolling_summary,
                max_context_messages=db_settings.max_context_messages,
                summary_token_threshold=db_settings.summary_token_threshold
            )
        
        return result
        
    async def get_memory_audit_logs(
        self,
        target_type: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[MemoryAudit]:
        """
        Get memory audit logs.
        
        Args:
            target_type: Filter by target type
            action: Filter by action
            limit: Maximum number of logs to return
            
        Returns:
            List of memory audit logs
        """
        from backend.core.infrastructure.database import db_session
        from backend.core.models.database_models import MemoryAuditDB
        from sqlalchemy import and_
        
        filters = []
        if target_type:
            filters.append(MemoryAuditDB.target_type == target_type)
        if action:
            filters.append(MemoryAuditDB.action == action)
            
        with db_session() as db:
            query = db.query(MemoryAuditDB)
            if filters:
                query = query.filter(and_(*filters))
                
            query = query.order_by(MemoryAuditDB.created_at.desc())
            query = query.limit(limit)
            
            db_logs = query.all()
            logs = [MemoryAudit(
                id=log.id,
                actor=log.actor,
                action=log.action,
                target_id=log.target_id,
                target_type=log.target_type,
                details=log.details,
                created_at=log.created_at
            ) for log in db_logs]
            
        return logs


# Singleton instance
enhanced_memory_service = EnhancedMemoryService()