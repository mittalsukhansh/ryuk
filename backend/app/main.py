"""AgentPay foundation API. No AI or payment endpoints are exposed."""

from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="AgentPay API", version="0.1.0")


class HealthResponse(BaseModel):
    """Process liveness only; does not assert database or provider readiness."""

    status: Literal["ok"]


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return API liveness without requiring credentials or external services."""
    return HealthResponse(status="ok")
