"""AgentPay API; checkout routes fail closed until trusted auth/services are provisioned."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Literal

from fastapi import FastAPI
from pydantic import BaseModel

from app.api.agent import router as agent_router
from app.api.checkout import router as checkout_router
from app.api.offers import router as offers_router
from app.services.catalog import CatalogService


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    """Load trusted fixtures once; invalid data prevents the API from starting."""
    application.state.catalog = CatalogService()
    yield


app = FastAPI(title="AgentPay API", version="0.1.0", lifespan=lifespan)
app.include_router(offers_router)
app.include_router(agent_router)
app.include_router(checkout_router)


class HealthResponse(BaseModel):
    """Process liveness only; does not assert database or provider readiness."""

    status: Literal["ok"]


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Return API liveness without requiring credentials or external services."""
    return HealthResponse(status="ok")
