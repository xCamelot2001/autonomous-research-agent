# 🤖 Autonomous AI Research Agent

A full-stack agentic AI system that accepts a high-level goal, plans sub-tasks,
executes tools (web search, APIs), reasons over results, and delivers a structured
output — all streamed in real time.

## Tech Stack

| Layer     | Tech                                      |
|-----------|-------------------------------------------|
| Backend   | Python · FastAPI · LangGraph              |
| AI/LLM    | Claude API (claude-sonnet) · Tool use     |
| Memory    | ChromaDB · short-term context             |
| Frontend  | React · TypeScript · Tailwind · Zustand   |
| Streaming | Server-Sent Events (SSE)                  |
| Deploy    | Docker · Railway/Render                   |

## Agent Architecture

```
User Goal → Planner → Tool Executor → Reasoner → Memory → Synthesizer → Output
```

## Quick Start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```
