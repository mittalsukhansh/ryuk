<<<<<<< HEAD
"""Regression evidence for confirmed review findings; synthetic credentials only."""
# ruff: noqa: F811

import pytest
from test_workspace import ORIGIN, PASSWORD, client, investigate, login  # noqa: F401

from app.api.agent import get_intent_parser
from app.main import app
from app.services.intent_parser import IntentClarificationRequired
from app.services.proposal_binding import canonical_proposal_digest
from app.services.session import DemoSessions


def test_anonymous_parser_never_calls_model(client):
    calls = []

    class Parser:
        async def parse(self, query):
            calls.append(query)
            raise AssertionError("Model must not be invoked")

    app.dependency_overrides[get_intent_parser] = lambda: Parser()
    result = client.post("/v1/agent/parse", json={"query": "private request"}, headers=ORIGIN)
    assert result.status_code == 401
    assert not calls


@pytest.mark.parametrize(
    "path,body",
    [
        ("/v1/session", {"password": "private-sentinel-" * 100}),
        ("/v1/session", {"password": {"private-sentinel": "credential"}}),
        ("/v1/session", {"password": PASSWORD, "private-sentinel": "credential"}),
        ("/v1/requests", {"query": "private-sentinel-" * 1000}),
    ],
)
def test_validation_never_reflects_secret_input(client, path, body):
    login(client)
    response = client.post(path, json=body, headers=ORIGIN)
    assert response.status_code == 422
    assert "private-sentinel" not in response.text
    assert PASSWORD not in response.text


def test_clarification_exception_not_reflected(client):
    login(client)

    class Parser:
        async def parse(self, query):
            raise IntentClarificationRequired("private-sentinel-provider-credential")

    app.dependency_overrides[get_intent_parser] = lambda: Parser()
    response = client.post("/v1/agent/parse", json={"query": "request"}, headers=ORIGIN)
    assert response.status_code == 422
    assert "private-sentinel" not in response.text


def test_every_model_candidate_requires_explicit_review(client):
    candidates = investigate(client)
    for candidate in candidates:
        assert candidate["proposal"]["requires_intent_review"] is True
        if candidate["policy"]["decision"] != "DENY":
            assert candidate["policy"]["decision"] == "REQUIRE_APPROVAL"
            assert "INTENT_REVIEW_REQUIRED" in candidate["policy"]["reason_codes"]
            assert (
                client.post(
                    "/v1/checkouts",
                    json={"proposal_id": candidate["proposal"]["proposal_id"]},
                    headers=ORIGIN,
                ).status_code
                == 409
            )


def test_review_marker_is_digest_bound(client):
    candidate = investigate(client)[0]
    proposal = app.state.workspace.approvals.get_proposal(
        candidate["proposal"]["proposal_id"], actor_user_id="ryuk-demo-buyer"
    )
    changed = proposal.model_copy(update={"requires_intent_review": False})
    assert canonical_proposal_digest(changed) != proposal.proposal_digest


@pytest.mark.parametrize("origin", ["https://demo.example", "https://localhost"])
def test_https_cannot_use_insecure_cookie(origin):
    with pytest.raises(ValueError, match="secure cookies"):
        DemoSessions(PASSWORD, origin=origin, secure=False)


def test_session_allocation_bounded():
    auth = DemoSessions(PASSWORD, origin="https://demo.example")
    auth._sessions = {str(i).encode(): float("inf") for i in range(64)}
    assert auth.login(PASSWORD, "client") is None
    for i in range(1024):
        auth._attempts[str(i)]
    assert auth.login(PASSWORD, "new-client") is None


def test_model_limit_does_not_disable_status_or_financial_recovery(client):
    login(client)
    auth = app.state.demo_sessions
    for _ in range(10):
        assert auth.allow_model_request()
    assert not auth.allow_model_request()
    response = client.post("/v1/requests", json={"query": "request"}, headers=ORIGIN)
    assert response.status_code == 429
    assert client.get("/v1/workspace").status_code == 200
=======
"""Step 12 adversarial regressions; only synthetic secrets and isolated mock providers."""

import asyncio
from copy import deepcopy

import httpx2
import pytest
from test_checkout import ACTOR, grant, ready, run
from test_checkout import env as env
from test_provisioning import boot
from test_provisioning import settings as settings
from test_workspace import GOLD, ORIGIN, investigate, login
from test_workspace import client as client

from app.api.agent import get_intent_parser
from app.main import app
from app.services.approvals import ApprovalPolicyError
from app.services.checkout import CheckoutBlocked, CheckoutService
from app.services.intent_parser import FakeIntentParser, InvalidParserOutput
from app.services.paypal import PayPalSandboxAdapter, PayPalSettings
from app.services.proposal_binding import InvalidProposalBinding, require_proposal_binding


def test_direct_parser_requires_authentication_before_provider_initialization(client):
    initialized = []

    def parser():
        initialized.append(True)
        return FakeIntentParser({GOLD["query"]: GOLD["extraction"]})

    app.dependency_overrides[get_intent_parser] = parser
    response = client.post("/v1/agent/parse", json={"query": GOLD["query"]}, headers=ORIGIN)
    assert response.status_code == 401
    assert initialized == []


@pytest.mark.parametrize("body", [
    {"password": "synthetic-sensitive-marker" * 100},
    {"password": "wrong", "client_secret": "synthetic-sensitive-marker"},
    {"password": {"nested": "synthetic-sensitive-marker"}},
])
def test_validation_errors_never_reflect_credentials(client, body):
    response = client.post("/v1/session", json=body, headers=ORIGIN)
    assert response.status_code == 422
    assert "synthetic-sensitive-marker" not in response.text
    assert "input" not in response.text


def test_remote_https_cannot_disable_secure_cookies(settings, monkeypatch):
    monkeypatch.setenv("RYUK_APP_ORIGIN", "https://demo.example")
    monkeypatch.setenv("RYUK_SECURE_COOKIES", "false")
    with pytest.raises(RuntimeError, match="RYUK_SECURE_COOKIES"):
        boot()


def test_short_quote_cannot_hide_mandatory_role():
    payload = deepcopy(GOLD["extraction"])
    gym = next(a for a in payload["required_attributes"] if a["name"] == "gym")
    payload["required_attributes"].remove(gym)
    gym["quote"] = "Gym"
    payload["preferred_attributes"].append(gym)
    with pytest.raises(InvalidParserOutput, match="wording"):
        asyncio.run(FakeIntentParser({GOLD["query"]: payload}).parse(GOLD["query"]))


@pytest.mark.parametrize("omission", ["gym", "private_pool"])
def test_omitted_model_requirements_cannot_bypass_bound_buyer_review(client, omission):
    payload = deepcopy(GOLD["extraction"])
    for role in ("required_attributes", "preferred_attributes"):
        payload[role] = [a for a in payload[role] if a["name"] != omission]
    app.dependency_overrides[get_intent_parser] = lambda: FakeIntentParser({GOLD["query"]: payload})
    candidate = investigate(client)[0]
    proposal = candidate["proposal"]
    assert proposal["intent"]["query"] == GOLD["query"]
    assert proposal["intent_review_required"] is True
    assert candidate["policy"]["decision"] == "REQUIRE_APPROVAL"
    assert "INTENT_REVIEW_REQUIRED" in candidate["policy"]["reason_codes"]
    pid = proposal["proposal_id"]
    assert (
        client.post("/v1/checkouts", json={"proposal_id": pid}, headers=ORIGIN).status_code == 409
    )
    assert not client.sandbox.orders
    approval = client.post(f"/v1/proposals/{pid}/approval", json={}, headers=ORIGIN).json()
    assert approval["proposal_digest"] == proposal["proposal_digest"]
    aid = approval["approval_request_id"]
    assert client.post(f"/v1/approvals/{aid}/decision", json={"decision": "REJECT"},
                       headers=ORIGIN).status_code == 200
    assert (
        client.post("/v1/checkouts", json={"proposal_id": pid}, headers=ORIGIN).status_code == 409
    )
    assert not client.sandbox.orders


def test_intent_review_flag_is_bound_and_cannot_reuse_old_consent(env):
    original = env["proposal"]
    grant(env, original)
    changed = original.model_copy(deep=True)
    changed.intent_review_required = True
    with pytest.raises(InvalidProposalBinding):
        require_proposal_binding(changed)
    env["approvals"].register_proposal(changed, at=env["now"][0],
                                        expected_digest=original.proposal_digest)
    with pytest.raises(ApprovalPolicyError):
        run(env["service"].create_checkout(original.proposal_id, **ACTOR))
    assert not env["sandbox"].orders


@pytest.mark.parametrize("header", [{}, {"Authorization": "Bearer forged"},
                                   {"X-User-Id": "ryuk-demo-buyer"}])
def test_all_private_api_paths_reject_unsigned_identity(client, header):
    paths = [("GET", "/v1/workspace", None), ("POST", "/v1/requests", {"query": GOLD["query"]}),
             ("POST", "/v1/agent/parse", {"query": GOLD["query"]}),
             ("GET", "/v1/proposals/unknown", None),
             ("POST", "/v1/proposals/unknown/select", {}),
             ("POST", "/v1/proposals/unknown/approval", {}),
             ("POST", "/v1/approvals/unknown/decision", {"decision": "APPROVE"}),
             ("GET", "/v1/proposals/unknown/audit", None),
             ("POST", "/v1/checkouts", {"proposal_id": "unknown"}),
             ("GET", "/v1/checkouts/unknown", None)]
    paths += [("POST", f"/v1/checkouts/unknown/{action}", {})
              for action in ("capture", "reconcile", "cancel")]
    for method, path, body in paths:
        response = client.request(method, path, json=body, headers=ORIGIN | header)
        assert response.status_code == 401, (method, path)
    assert not client.sandbox.calls


@pytest.mark.parametrize("origin", [None, "https://evil.test", "https://localhost:3100"])
def test_direct_parser_rejects_origin_before_provider(client, origin):
    login(client)
    initialized = []
    app.dependency_overrides[get_intent_parser] = lambda: initialized.append(True)
    headers = {"Origin": origin} if origin else {}
    response = client.post("/v1/agent/parse", json={"query": GOLD["query"]}, headers=headers)
    assert response.status_code == 403
    assert initialized == []


def test_cancellation_racing_provider_preflight_prevents_capture(env):
    async def scenario():
        record = await ready(env)
        cid = record.payment.payment_intent_id
        env["sandbox"].on_get = lambda: env["service"].cancel(cid, **ACTOR)
        with pytest.raises(CheckoutBlocked):
            await env["service"].capture(cid, **ACTOR)
        assert env["store"].get_checkout(cid, **ACTOR).payment.state == "FAILED"
        assert env["store"].get_budget("user-1").reserved_minor == 0
        assert not env["sandbox"].capture_posts()
    run(scenario())


def test_lost_capture_response_new_adapter_recovers_original_terms_without_post(env):
    async def scenario():
        record = await ready(env)
        cid = record.payment.payment_intent_id
        env["sandbox"].capture_mode = "timeout_after_capture"
        pending = await env["service"].capture(cid, **ACTOR)
        assert pending.payment.state == "PENDING_PROVIDER"
        async with PayPalSandboxAdapter(
            PayPalSettings(client_id="synthetic", client_secret="synthetic"),
            transport=httpx2.MockTransport(env["sandbox"].handle),
        ) as fresh_adapter:
            service = CheckoutService(env["store"], env["approvals"], fresh_adapter,
                                      clock=lambda: env["now"][0])
            result = await service.capture(cid, **ACTOR)
            assert result.payment.state == "SUCCEEDED"
        assert len(env["sandbox"].capture_posts()) == 1
        assert env["store"].get_budget("user-1").settled_minor == record.payment.amount_minor
    run(scenario())


def test_production_app_has_no_fixture_control_routes(client):
    login(client)
    for path in ("/__test__/new-case", "/__test__/reset", "/__test__/approve/FORGED"):
        assert client.post(path, headers=ORIGIN).status_code == 404
    assert not client.sandbox.calls
>>>>>>> 83d921d (local changes before merging)
