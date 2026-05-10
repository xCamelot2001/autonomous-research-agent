"""
Core agent loop — Phase 1 implementation.

ReAct-style loop:
  1. Planner breaks the goal into sub-tasks
  2. Tool executor runs tools as Claude requests them
  3. Reasoner evaluates results and decides next step
  4. Loop continues until Claude stops requesting tools
  5. Synthesizer produces structured final output
"""
import json
from typing import AsyncGenerator

import anthropic

from app.config import settings
from app.models.events import AgentEvent, EventType
from app.tools.executor import TOOL_DEFINITIONS, execute_tool

SYSTEM_PROMPT = """You are an autonomous research agent. Your job is to:

1. PLAN: Break the user's goal into clear sub-tasks
2. EXECUTE: Use your tools to gather information
3. REASON: Evaluate what you've found and decide what to do next
4. SYNTHESIZE: Produce a structured, well-cited final output

Behaviour rules:
- Always start by briefly stating your plan (2-4 bullet points)
- Use tools iteratively — search, read results, search again if needed
- Reason explicitly: "Based on X, I now need to Y"
- When you have enough information, produce a structured final report
- Format your final output as JSON with keys: summary, sections (list of {title, content}), citations (list of URLs)

Be thorough but efficient. Quality over quantity.
"""


class AgentLoop:
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def run(self, goal: str) -> AsyncGenerator[AgentEvent, None]:
        messages = [{"role": "user", "content": goal}]

        yield AgentEvent(
            type=EventType.PLAN,
            content=f"Starting agent for goal: {goal}",
        )

        iteration = 0
        max_iterations = 10

        while iteration < max_iterations:
            iteration += 1

            response = await self.client.messages.create(
                model=settings.model,
                max_tokens=settings.max_tokens,
                system=SYSTEM_PROMPT,
                tools=TOOL_DEFINITIONS,
                messages=messages,
            )

            tool_calls_made = False

            for block in response.content:
                if block.type == "text" and block.text.strip():
                    event_type = EventType.PLAN if iteration == 1 else EventType.REASON
                    yield AgentEvent(type=event_type, content=block.text)

                elif block.type == "tool_use":
                    tool_calls_made = True
                    yield AgentEvent(
                        type=EventType.TOOL_CALL,
                        content=f"Calling tool: {block.name}",
                        metadata={"tool": block.name, "inputs": block.input},
                    )

                    result = await execute_tool(block.name, block.input)

                    yield AgentEvent(
                        type=EventType.TOOL_RESULT,
                        content=result,
                        metadata={"tool": block.name},
                    )

                    messages.append({"role": "assistant", "content": response.content})
                    messages.append({
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        ],
                    })
                    break

            if not tool_calls_made or response.stop_reason == "end_turn":
                final_text = next(
                    (b.text for b in response.content if b.type == "text"), ""
                )

                structured = _parse_output(final_text, goal)

                yield AgentEvent(
                    type=EventType.OUTPUT,
                    content=json.dumps(structured),
                    metadata={"iterations": iteration},
                )
                yield AgentEvent(type=EventType.DONE, content="Agent complete")
                return

        yield AgentEvent(
            type=EventType.ERROR,
            content=f"Agent reached max iterations ({max_iterations}) without completing.",
        )
        yield AgentEvent(type=EventType.DONE, content="Agent stopped")


def _parse_output(text: str, goal: str) -> dict:
    if "```json" in text:
        try:
            json_str = text.split("```json")[1].split("```")[0].strip()
            return json.loads(json_str)
        except Exception:
            pass
    try:
        return json.loads(text)
    except Exception:
        pass
    return {
        "summary": text[:500] if len(text) > 500 else text,
        "sections": [{"title": "Research Results", "content": text}],
        "citations": [],
    }
