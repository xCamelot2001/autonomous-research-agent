import asyncio
import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.agent.loop import AgentLoop
from app.models.events import GoalRequest

router = APIRouter(prefix="/agent", tags=["agent"])
agent = AgentLoop()


@router.post("/run")
async def run_agent(request: GoalRequest):
    async def event_stream():
        try:
            async for event in agent.run(request.goal):
                yield f"data: {event.model_dump_json()}\n\n"
                await asyncio.sleep(0)
        except Exception as e:
            error_payload = json.dumps({"type": "error", "content": str(e), "metadata": {}})
            yield f"data: {error_payload}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
