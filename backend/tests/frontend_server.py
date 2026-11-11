"""E2E-only server with fake model/provider transport. Never used by application startup."""

import json
import os
from contextlib import asynccontextmanager
from pathlib import Path

import httpx2
import uvicorn
from test_checkout import Sandbox

from app.api.agent import get_intent_parser
from app.main import app, lifespan
from app.services.approvals import InMemoryApprovalService
from app.services.intent_parser import FakeIntentParser
from app.services.paypal import PayPalSandboxAdapter, PayPalSettings
from app.services.session import DemoSessions
from app.services.workspace import WorkspaceService

PASSWORD = "synthetic-browser-password"
os.environ.update(
    RYUK_DEMO_ENABLED="true",
    RYUK_DEMO_PASSWORD=PASSWORD,
    RYUK_APP_ORIGIN="http://localhost:3100",
    RYUK_SECURE_COOKIES="false",
    RYUK_CHECKOUT_DB_PATH=os.environ.get("RYUK_E2E_DB", "/tmp/ryuk-e2e.sqlite3"),
    PAYPAL_CLIENT_ID="synthetic-browser-client",
    PAYPAL_CLIENT_SECRET="synthetic-browser-secret",
    PAYPAL_MERCHANT_ID="DEMOSELLER",
)
cases = json.loads(
    (Path(__file__).resolve().parents[2] / "fixtures/intent_prompts.json").read_text()
)
gold = cases["cases"][0]
QUERY = (
    "Find a hotel in Switzerland for 5 nights under USD 1,500.\n"
    "Gym, mountain view and free cancellation are required.\n"
    "Private pool preferred. Ask me above USD 1,300."
)
# Quotes must match the actual prompt. Real fake parser runs the real Pydantic/source checks.
example = json.loads(json.dumps(gold["extraction"]))
example["budget"]["quote"] = "under USD 1,500"
for attribute in example["required_attributes"]:
    if attribute["name"] in {"gym", "mountain_view", "free_cancellation"}:
        attribute["quote"] = "Gym, mountain view and free cancellation are required"
parser = FakeIntentParser({gold["query"]: gold["extraction"], QUERY: example})
app.dependency_overrides[get_intent_parser] = lambda: parser
sandbox = Sandbox()


@asynccontextmanager
async def e2e_lifespan(application):
    async with lifespan(application):
        async with PayPalSandboxAdapter(
            PayPalSettings.from_env(), transport=httpx2.MockTransport(sandbox.handle)
        ) as paypal:
            application.state.checkout_service.paypal = paypal
            yield


# Test-only route simulates the SDK's provider approval, not browser financial authority.
@app.post("/__test__/approve/{order_id}")
def test_approve(order_id: str, mode: str = "success") -> dict:
    sandbox.approve(order_id)
    sandbox.capture_mode = mode
    return {"ok": True}


@app.post("/__test__/reset")
def test_reset() -> dict:
    store = app.state.workspace.store
    with store.transaction() as connection:
        for table in ("checkout_audit", "reservations", "checkouts"):
            connection.execute("DELETE FROM " + table)
        connection.execute("UPDATE accounts SET settled_minor=0, limit_minor=150000")
    approvals = InMemoryApprovalService()
    app.state.workspace = WorkspaceService(app.state.catalog, store, approvals)
    app.state.checkout_service.approvals = approvals
    app.state.demo_sessions = DemoSessions(PASSWORD, origin="http://localhost:3100", secure=False)
    sandbox.orders.clear()
    sandbox.calls.clear()
    sandbox.capture_mode = "success"
    return {"ok": True}


app.router.lifespan_context = e2e_lifespan
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8100, log_level="warning")
