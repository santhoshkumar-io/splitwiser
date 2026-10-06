"""Health check endpoints.

Kept in its own router so `main.py` stays a thin assembly point as the
app grows (users, groups, expenses, settlements each get a router).
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Declaring the response shape lets FastAPI validate what we return
    and document it automatically in /docs."""

    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness probe: confirms the process is up and serving requests."""
    return HealthResponse(status="ok", version="0.1.0")
