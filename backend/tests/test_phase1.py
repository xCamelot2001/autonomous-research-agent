import pytest
from app.models.events import AgentEvent, EventType
from app.tools.executor import execute_tool


@pytest.mark.asyncio
async def test_web_search_stub():
    result = await execute_tool("web_search", {"query": "AI courses 2025"})
    assert "AI courses 2025" in result
    assert len(result) > 50


@pytest.mark.asyncio
async def test_fetch_url_stub():
    result = await execute_tool("fetch_url", {"url": "https://example.com"})
    assert "example.com" in result


def test_agent_event_serialisation():
    event = AgentEvent(type=EventType.PLAN, content="Testing", metadata={"key": "val"})
    dumped = event.model_dump_json()
    assert '"plan"' in dumped
    assert "Testing" in dumped


def test_unknown_tool():
    import asyncio
    result = asyncio.run(execute_tool("nonexistent_tool", {}))
    assert "Unknown tool" in result
