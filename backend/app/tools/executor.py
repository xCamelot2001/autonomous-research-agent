"""
Tool definitions passed to the Claude API.
Phase 1: stub implementations. Phase 2: real web search + APIs.
"""
from typing import Any

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": "Search the web for current information on a topic. Returns a list of results with titles, URLs, and snippets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "fetch_url",
        "description": "Fetch the content of a specific URL and return the text.",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch",
                }
            },
            "required": ["url"],
        },
    },
]


async def execute_tool(name: str, inputs: dict[str, Any]) -> str:
    """
    Dispatch a tool call to the correct implementation.
    Phase 1 returns realistic stub data so the agent loop can be tested end-to-end.
    Real implementations are added in Phase 2.
    """
    if name == "web_search":
        return _stub_web_search(inputs["query"])
    elif name == "fetch_url":
        return _stub_fetch_url(inputs["url"])
    else:
        return f"Unknown tool: {name}"


def _stub_web_search(query: str) -> str:
    return f"""Search results for "{query}":

1. Title: "Complete Guide to {query}"
   URL: https://example.com/guide
   Snippet: A comprehensive overview covering all key aspects...

2. Title: "{query} — Top Resources 2025"
   URL: https://example.com/resources
   Snippet: Updated list of the best resources, compared by quality and depth...

3. Title: "How to get started with {query}"
   URL: https://example.com/getting-started
   Snippet: Beginner-friendly introduction with practical examples...

Note: These are stub results. Real web search will be wired in Phase 2.
"""


def _stub_fetch_url(url: str) -> str:
    return f"""Content from {url}:

This page contains detailed information about the topic.
Key points:
- Point 1: Important detail about the subject
- Point 2: Comparison with alternatives
- Point 3: Pricing and availability
- Point 4: Expert recommendation

Note: This is stub content. Real URL fetching will be wired in Phase 2.
"""
