"""
Web search tool using DuckDuckGo API.
"""
import httpx
from typing import List

from backend.core.tools.base import BaseTool, ToolParameter


class WebSearchTool(BaseTool):
    """A web search tool that uses DuckDuckGo API."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Searches the web for information using DuckDuckGo",
            parameters=[
                ToolParameter(
                    name="query",
                    type="string",
                    description="Search query",
                    required=True
                ),
                ToolParameter(
                    name="max_results",
                    type="integer",
                    description="Maximum number of results to return (default: 5)",
                    required=False
                )
            ]
        )
    
    async def run(self, query: str, max_results: int = 5) -> dict:
        """
        Search the web using DuckDuckGo API.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            Dictionary with search results or error
        """
        try:
            # DuckDuckGo API endpoint
            url = "https://api.duckduckgo.com/"
            
            # Parameters for the API request
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            # Make the API request
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                
                # Parse the JSON response
                data = response.json()
                
                # Extract relevant information
                results = []
                if "RelatedTopics" in data:
                    for item in data["RelatedTopics"][:max_results]:
                        if "FirstURL" in item and "Text" in item:
                            results.append({
                                "title": item["FirstURL"].split("/")[-1].replace("_", " "),
                                "url": item["FirstURL"],
                                "snippet": item["Text"]
                            })
                
                return {
                    "query": query,
                    "results": results,
                    "total_results": len(results)
                }
        except httpx.HTTPError as e:
            return {
                "error": f"HTTP error occurred: {str(e)}",
                "query": query
            }
        except Exception as e:
            return {
                "error": f"An error occurred during search: {str(e)}",
                "query": query
            }