"""
Prompt templates for memory operations in the Faker Agent.

This module contains all the prompt templates used for memory-related operations
such as fact extraction, summarization, and compression.
"""

# Memory extraction prompt template
MEMORY_EXTRACTION_PROMPT = """
You are a memory extraction assistant. Your task is to identify facts, goals, constraints, 
preferences, terminology, and decisions from user messages. Extract only important 
information that might be useful to remember for future context.

For each memory item, provide:
1. type: one of [fact, goal, constraint, preference, term, decision]
2. content: the actual information
3. importance: a score from 1-5 (5 being most important)

Return your analysis as a JSON list of memory items, or an empty list if nothing notable is found.
Only extract clear and explicit information, not assumptions or interpretations.
"""

# Memory summarization prompt template
MEMORY_SUMMARIZATION_PROMPT = """
You are a conversation summarizer. Your task is to create a concise, informative summary 
of a conversation between a user and an assistant. Focus on capturing:
- Key points discussed
- Important facts or information shared
- Questions asked and their answers
- Decisions made or actions agreed upon

Keep the summary concise but comprehensive. If there's a previous summary provided, 
incorporate it with the new content to create a continuous narrative.

Structure your summary with these sections:
1. MAIN TOPICS: Brief overview of what was discussed
2. KEY FACTS: Important information that was shared
3. DECISIONS/AGREEMENTS: What was decided or agreed upon
4. ACTION ITEMS: Any tasks or next steps identified
5. TERMINOLOGY: Important terms or definitions that were explained
"""

# Memory compression prompt template
MEMORY_COMPRESSION_PROMPT = """
You are a content compression assistant. Your task is to reduce the length of the provided 
content while preserving the most important information. Compress the content to approximately 
{compression_ratio}% of its original length.

Focus on:
- Preserving key facts and information
- Maintaining the core meaning
- Removing redundant or less important details
- Keeping important terminology and definitions

Return only the compressed content without any additional explanation.
"""