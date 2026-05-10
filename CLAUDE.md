# Autonomous Research Agent — Project Notes

## What this project does

A user types a research goal ("What are the best open-source LLMs in 2025?") into a web UI. The backend runs an AI agent that plans, calls tools, reasons over results, and streams its thought process back to the frontend in real time. When done, it delivers a structured report with a summary, sections, and citations.

---

## Project structure

```
autonomous-research-agent/
├── backend/                  # Python / FastAPI
│   ├── app/
│   │   ├── main.py           # FastAPI app, CORS middleware
│   │   ├── config.py         # Settings loaded from .env
│   │   ├── api/
│   │   │   └── agent.py      # POST /api/agent/run  (SSE endpoint)
│   │   ├── agent/
│   │   │   └── loop.py       # Core ReAct agent loop
│   │   ├── models/
│   │   │   └── events.py     # Pydantic models: AgentEvent, GoalRequest, etc.
│   │   └── tools/
│   │       └── executor.py   # Tool definitions + dispatch (stubs for now)
│   ├── tests/
│   │   └── test_phase1.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                 # React + TypeScript + Vite
│   ├── src/
│   │   ├── main.tsx          # React entry point
│   │   ├── App.tsx           # Main UI component
│   │   ├── index.css         # Tailwind directives
│   │   ├── hooks/
│   │   │   └── useAgent.ts   # SSE fetch logic
│   │   ├── store/
│   │   │   └── agentStore.ts # Zustand global state
│   │   └── types/
│   │       └── agent.ts      # TypeScript types
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── Dockerfile
├── docker-compose.yml
├── Makefile
└── .gitignore
```

---

## Tech stack

| Layer | Tech |
|-------|------|
| Backend framework | FastAPI (Python) |
| AI SDK | Anthropic Python SDK (`anthropic>=0.40.0`) |
| AI model | `claude-sonnet-4-6` |
| Frontend framework | React 18 + TypeScript |
| Build tool | Vite |
| State management | Zustand |
| Styling | Tailwind CSS v3 |
| Backend–frontend link | Server-Sent Events (SSE) over HTTP |

---

## How the backend works

### Entry point — `app/main.py`

Creates the FastAPI app, attaches CORS middleware, and mounts the agent router at `/api`.

CORS is configured to allow:
- Explicit origins from `settings.cors_origins` (set via `CORS_ORIGINS` in `.env`)
- Any `http://localhost:<port>` via regex — this handles Vite picking a random port when 5173 is busy

### Settings — `app/config.py`

Uses `pydantic-settings` to load config from the environment / `.env` file:

```
ANTHROPIC_API_KEY=sk-ant-...
MODEL=claude-sonnet-4-6
MAX_TOKENS=4096
CORS_ORIGINS=["http://localhost:5173"]
```

`CORS_ORIGINS` must be a JSON array string because pydantic-settings v2 parses list fields as JSON.

### API endpoint — `app/api/agent.py`

Single endpoint: `POST /api/agent/run`

Accepts `{ "goal": "..." }` and returns a **streaming SSE response**. Each event is a JSON-encoded `AgentEvent` pushed as:

```
data: {"type":"plan","content":"...","metadata":{}}\n\n
```

The endpoint creates a single shared `AgentLoop` instance and streams events from it directly to the client. The `asyncio.sleep(0)` between yields hands control back to the event loop so the stream flushes incrementally rather than buffering.

### Agent loop — `app/agent/loop.py`

This is the core of the project. It implements a **ReAct loop** (Reason + Act):

```
while iterations < 10:
    1. Call Claude API with current message history + tool definitions
    2. For each content block in the response:
       - If text → yield a PLAN or REASON event to the frontend
       - If tool_use → yield TOOL_CALL event, execute the tool,
                       yield TOOL_RESULT event, append both to message
                       history, break inner loop
    3. If no tool was called (or stop_reason == "end_turn"):
       → parse final output, yield OUTPUT event, yield DONE, return
```

The message history grows with each iteration, giving Claude full context of what it has already done. Claude decides on its own when to stop calling tools and produce a final answer.

The system prompt instructs Claude to:
- Start with a 2–4 bullet plan
- Use tools iteratively
- Reason explicitly between steps
- Produce a final JSON report with `summary`, `sections`, and `citations`

The final output is parsed by `_parse_output()`, which tries to extract a JSON block from the response (Claude wraps it in ```json ... ```) and falls back to a plain text wrapper if parsing fails.

### Tools — `app/tools/executor.py`

Two tools are defined and passed to Claude:

| Tool | Description | Status |
|------|-------------|--------|
| `web_search` | Search the web for a query | Stub (returns fake results) |
| `fetch_url` | Fetch content from a URL | Stub (returns fake content) |

Claude sees the tool definitions and calls them autonomously. The executor dispatches to the right function. Real implementations (Tavily, BeautifulSoup, etc.) replace the stubs in Phase 2.

### Models — `app/models/events.py`

```python
class EventType(str, Enum):
    PLAN, TOOL_CALL, TOOL_RESULT, REASON, OUTPUT, ERROR, DONE

class AgentEvent(BaseModel):
    type: EventType
    content: str        # always a string — JSON is stringified into this
    metadata: dict      # optional extra info (tool name, inputs, iteration count)

class GoalRequest(BaseModel):
    goal: str
```

---

## How the frontend works

### Entry point — `src/main.tsx`

Mounts React into `#root`, imports `index.css` (Tailwind), wraps app in `StrictMode`.

### UI — `src/App.tsx`

One page:
- Text input + "Run Agent" button
- Scrolling thought stream showing every agent event colour-coded by type
- Final output panel showing summary, sections, and citations once the agent finishes

No routing, no pages — all state comes from the Zustand store.

### State — `src/store/agentStore.ts`

Zustand store holds:

```typescript
status: 'idle' | 'running' | 'complete' | 'error'
events: AgentEvent[]   // the live thought stream
output: AgentOutput | null  // final structured report
goal: string
```

Actions: `setStatus`, `addEvent`, `setOutput`, `reset`.

### SSE hook — `src/hooks/useAgent.ts`

`runAgent(goal)` does the following:

1. Resets the store, sets status to `running`
2. Opens a `fetch` POST to `/api/agent/run` with the goal
3. Reads the response body as a **ReadableStream** (not `EventSource` — `fetch` streaming gives more control)
4. Accumulates chunks into a buffer, splits on `\n\n`, strips the `data: ` prefix, JSON-parses each event
5. Dispatches each event to the store:
   - `output` event → also parses `event.content` as JSON and calls `setOutput`
   - `done` → sets status to `complete`
   - `error` → sets status to `error`

Why `fetch` instead of `EventSource`? `EventSource` doesn't support POST requests or custom headers.

### Types — `src/types/agent.ts`

```typescript
interface AgentEvent {
  type: EventType       // 'plan' | 'tool_call' | 'tool_result' | 'reason' | 'output' | 'error' | 'done'
  content: string
  metadata: Record<string, unknown>
}

interface AgentOutput {
  summary: string
  sections: Array<{ title: string; content: string }>
  citations: string[]
}
```

These mirror the backend Pydantic models exactly — keep them in sync if you change either side.

---

## How frontend and backend connect

```
Browser (localhost:517x)
  │
  │  POST /api/agent/run  { goal: "..." }
  ▼
FastAPI (localhost:8000)
  │
  │  StreamingResponse (text/event-stream)
  │  data: {"type":"plan","content":"..."}\n\n
  │  data: {"type":"tool_call","content":"..."}\n\n
  │  ...
  ▼
Browser reads stream chunk by chunk
  → parses events
  → pushes to Zustand store
  → React re-renders thought stream in real time
```

The connection stays open for the entire agent run (could be 30–60 seconds for a real multi-step run). The browser never polls — it just reads until the stream closes.

---

## How to run locally

```bash
# 1. Install dependencies (first time only)
make install

# 2. Add your API key
cp backend/.env.example backend/.env
# edit backend/.env and set ANTHROPIC_API_KEY=sk-ant-...

# 3. Start both servers
make dev
```

Backend runs at `http://localhost:8000` — API docs at `http://localhost:8000/docs`
Frontend runs at `http://localhost:5173` (or next available port)

### Docker (alternative)

```bash
docker-compose up --build
```

---

## What is stubbed / not real yet

| Thing | Current state | Phase it gets real |
|-------|--------------|-------------------|
| `web_search` tool | Returns hardcoded fake results | Phase 2 |
| `fetch_url` tool | Returns hardcoded fake content | Phase 2 |
| Memory / vector store | ChromaDB is in requirements but unused | Phase 3 |
| UI polish | Inline styles, no Tailwind classes used yet | Phase 4 |
| Deployment | Docker works locally, not deployed | Phase 5 |

---

## Known limitations in the current loop

- **One tool call per iteration**: if Claude returns text + multiple tool_use blocks in one response, only the first tool is executed. This is intentional for simplicity — Claude rarely batches tool calls in a ReAct setup.
- **No retry logic**: if the Claude API call fails mid-run, the SSE stream sends an error event and stops. Tenacity is in requirements for Phase 2.
- **Shared agent instance**: `agent_router.py` creates one `AgentLoop` at import time. Concurrent requests share it. Fine for solo use, needs per-request instances for multi-user.

---

## Phase roadmap

| Phase | What gets built |
|-------|----------------|
| 1 ✅ | Scaffold, Claude API wired, basic tool-use loop, SSE streaming |
| 2 | Real web search (Tavily/SerpAPI), URL fetching, multi-step planner, self-reflection |
| 3 | ChromaDB vector store, conversation memory, context injection |
| 4 | Polished React UI — task timeline, thought stream, structured output display |
| 5 | Docker deploy to Railway/Render, README, demo video |
