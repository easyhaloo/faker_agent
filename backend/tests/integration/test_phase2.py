"""
Integration test for Phase 2 components.

This test script demonstrates the integration of the LLM integration layer,
Flow Orchestrator, and LLM Assembler components.
"""
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from backend.core.assembler.llm_assembler import LLMAssembler
from backend.core.contracts.base import Message
from backend.core.graph.event_types import Event, EventType
from backend.core.graph.flow_orchestrator import FlowOrchestrator
from backend.core.infrastructure.llm.factory import llm_factory
from backend.core.tools.registry import tool_registry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Sample query for testing
SAMPLE_QUERY = "What's the weather like in San Francisco and calculate 25 * 37?"


async def handle_event(event: Event) -> None:
    """Handle events from the orchestrator."""
    if event.type == EventType.TOOL_CALL_START:
        logger.info(f"🔧 Starting tool: {event.tool_name}")
        logger.info(f"   Arguments: {json.dumps(event.tool_args)}")
        
    elif event.type == EventType.TOOL_CALL_RESULT:
        if event.error:
            logger.error(f"❌ Tool error: {event.error}")
        else:
            logger.info(f"✅ Tool result: {event.result}")
        
    elif event.type == EventType.TOKEN:
        pass  # Ignore token events for cleaner output
        
    elif event.type == EventType.FINAL:
        logger.info(f"🏁 Final response: {event.response}")
        
    elif event.type == EventType.ERROR:
        logger.error(f"💥 Error: {event.error}")
        if event.stack_trace:
            logger.debug(f"Stack trace: {event.stack_trace}")


async def test_with_assembler() -> None:
    """Test the full flow with the LLM Assembler."""
    logger.info("=== Starting test with LLM Assembler ===")
    
    # Create the assembler
    assembler = LLMAssembler()
    
    # Generate an execution plan
    logger.info(f"Generating execution plan for query: {SAMPLE_QUERY}")
    execution_plan = await assembler.create_execution_plan(SAMPLE_QUERY)
    
    logger.info(f"Generated plan: {execution_plan.plan}")
    logger.info(f"Tool chain with {len(execution_plan.tool_chain.nodes)} tools")
    
    # Create the orchestrator with the execution plan
    orchestrator = FlowOrchestrator(
        execution_plan=execution_plan,
        system_message="You are a helpful assistant that can use tools to answer questions."
    )
    
    # Execute the plan
    logger.info("Executing the plan...")
    result = await orchestrator.invoke(SAMPLE_QUERY, event_callback=handle_event)
    
    # Get the final message
    messages = result.get("messages", [])
    final_message = messages[-1] if messages else None
    
    if final_message:
        logger.info(f"Final result: {final_message.content}")
    else:
        logger.warning("No final message returned")


async def test_with_default_flow() -> None:
    """Test the default flow without the assembler."""
    logger.info("=== Starting test with default flow ===")
    
    # Create a default LLM node using the factory
    llm_adapter = llm_factory.get_default_adapter()
    
    async def llm_node(state: Dict[str, Any]) -> Dict[str, Any]:
        """Simple LLM node for testing."""
        messages = state.get("messages", [])
        
        # Convert to Message objects
        faker_messages = []
        for msg in messages:
            role = msg.get("role", "user") if isinstance(msg, dict) else getattr(msg, "role", "user")
            content = msg.get("content", "") if isinstance(msg, dict) else getattr(msg, "content", "")
            faker_messages.append(Message(role=role, content=content))
        
        # Add system message if not present
        if not any(msg.role == "system" for msg in faker_messages):
            faker_messages.insert(0, Message(
                role="system",
                content="You are a helpful assistant that can use tools to answer questions."
            ))
        
        # Get response from LLM
        response = await llm_adapter.chat(faker_messages)
        
        # Convert back to expected format
        response_dict = {"role": "assistant", "content": response.content}
        
        # Update messages in state
        return {"messages": messages + [response_dict]}
    
    # Create the orchestrator
    orchestrator = FlowOrchestrator(
        llm_node=llm_node,
        filter_strategy="threshold_5"  # Use threshold filter strategy
    )
    
    # Execute with the query
    logger.info(f"Executing query: {SAMPLE_QUERY}")
    result = await orchestrator.invoke(SAMPLE_QUERY, event_callback=handle_event)
    
    # Get the final message
    messages = result.get("messages", [])
    final_message = messages[-1] if messages else None
    
    if final_message:
        logger.info(f"Final result: {final_message.content}")
    else:
        logger.warning("No final message returned")


async def main() -> None:
    """Run the integration tests."""
    # Display available tools
    tools = tool_registry.list_tools()
    logger.info(f"Available tools: {len(tools)}")
    for i, tool in enumerate(tools, 1):
        logger.info(f"{i}. {tool.name}: {tool.description}")
    
    # Run tests
    await test_with_assembler()
    logger.info("\n")
    await test_with_default_flow()


if __name__ == "__main__":
    asyncio.run(main())