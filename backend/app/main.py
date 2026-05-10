from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.agent import router as agent_router
from app.config import settings

app = FastAPI(
    title="Autonomous Research Agent",
    description="Agentic AI that plans, searches, reasons, and delivers structured output.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": "Autonomous Research Agent",
        "version": "0.1.0",
        "phase": "Phase 1 — Foundation",
        "docs": "/docs",
    }
