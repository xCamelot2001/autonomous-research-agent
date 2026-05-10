from enum import Enum
from typing import Any
from pydantic import BaseModel


class EventType(str, Enum):
    PLAN = "plan"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    REASON = "reason"
    OUTPUT = "output"
    ERROR = "error"
    DONE = "done"


class AgentEvent(BaseModel):
    type: EventType
    content: str
    metadata: dict[str, Any] = {}


class GoalRequest(BaseModel):
    goal: str


class AgentOutput(BaseModel):
    goal: str
    summary: str
    sections: list[dict[str, Any]]
    citations: list[str] = []
