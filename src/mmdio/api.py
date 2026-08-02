"""mmdio REST API."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mmdio.detect import detect_diagram_type


class DiagramDetectRequest(BaseModel):
    """Candidate Mermaid source submitted for non-actuating inspection."""

    source: str = Field(min_length=1, max_length=100_000)


class DiagramDetectResponse(BaseModel):
    """Bounded detection result for a candidate Mermaid document."""

    diagram_type: str
    source_length: int


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Handle FastAPI startup and shutdown events."""
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    yield


app = FastAPI(
    title="mmdio",
    description="Mermaid diagrams as universal, non-actuating information I/O.",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
async def health() -> dict[str, str]:
    """Report API process liveness without claiming subsystem standing."""
    return {"status": "alive", "scope": "api-process"}


@app.post("/api/v1/diagrams/detect", response_model=DiagramDetectResponse)
async def detect_diagram(request: DiagramDetectRequest) -> DiagramDetectResponse:
    """Detect a Mermaid type without parsing, executing, or mutating machine state."""
    return DiagramDetectResponse(
        diagram_type=detect_diagram_type(request.source), source_length=len(request.source)
    )


@app.get("/compute")
async def compute(n: int = 42) -> int:
    """Compute the result of a CPU-bound function."""

    def fibonacci(value: int) -> int:
        return value if value <= 1 else fibonacci(value - 1) + fibonacci(value - 2)

    return await asyncio.to_thread(fibonacci, n)
