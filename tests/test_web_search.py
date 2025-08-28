"""
Test for web search tool.
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.core.tools.web_search import WebSearchTool


async def test_web_search():
    """Test web search tool functionality."""
    # Initialize web search tool
    searcher = WebSearchTool()
    
    # Test queries
    queries = [
        "Python programming",
        "FastAPI framework",
        "Redis database",
        "Machine learning"
    ]
    
    print("Testing web search tool...")
    for query in queries:
        print(f"\nSearching for: {query}")
        result = await searcher.run(query, max_results=3)
        
        if "error" in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Found {result['total_results']} results:")
            for i, res in enumerate(result['results'], 1):
                print(f"{i}. {res['title']}")
                print(f"   URL: {res['url']}")
                print(f"   Snippet: {res['snippet'][:100]}...")
    
    print("\nTest completed!")


if __name__ == "__main__":
    asyncio.run(test_web_search())