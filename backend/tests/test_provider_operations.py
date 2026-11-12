"""Mocked refunds/observations on fresh ledgers; no provider calls escape MockTransport."""

import asyncio
from copy import deepcopy
from datetime import datetime, timezone

import httpx2
import pytest
from fastapi.testclient import TestClient
from test_checkout import ACTOR, ready
from test_checkout import env as checkout_env

from app.main import app
from app.services.checkout import CheckoutBlocked
from app.services.checkout_store import CheckoutAccessError
from app.services.paypal import PayPalError
from app.services.provider_operations import ProviderOperations

env = checkout_env


def run(coro):
    return asyncio.run(coro)


def completed(env):
    async def scenario():
        record = await ready(env)
        return await env["service"].capture(record.payment.payment_intent_id, **ACTOR)

    return run(scenario())


def refund_payload(record, status="COMPLETED"):
    return {
        "id": "REFUND123",
        "status": status,
        "amount": record.terms.provider_amount(),
        "links": [
            {
                "rel": "up",
                "href": "https://api-m.sandbox.paypal.com/v2/payments/captures/"
                + record.capture_id,
            }
        ],
    }


def transport(env, record, *, mode="COMPLETED", verified=True):
    old = env["sandbox"].handle
    calls = []

    def handle(request):
        if request.url.path == "/v1/notifications/verify-webhook-signature":
            calls.append(request)
            return httpx2.Response(
                200, json={"verification_status": "SUCCESS" if verified else "FAILURE"}
            )
        if "/refund" in request.url.path:
            calls.append(request)
            if mode == "timeout":
                raise httpx2.ReadTimeout("private", request=request)
            return httpx2.Response(
                201 if request.method == "POST" else 200, json=refund_payload(record, mode)
            )
        return old(request)

    env["paypal"]._client._transport = httpx2.MockTransport(handle)
    return calls


def approved(env, record):
    ops = ProviderOperations(env["store"], env["paypal"])
    req = ops.request_refund(record.payment.payment_intent_id, "user-1", "Changed my mind")
    ops.review_refund(
        req["request_id"], approve=True, operator="test operator", reason="Verified request"
    )
    return ops, req["request_id"]


def test_buyer_request_is_owner_bound_idempotent_and_never_dispatches(env):
    record = completed(env)
    ops = ProviderOperations(env["store"], env["paypal"])
    with pytest.raises(CheckoutAccessError):
        ops.request_refund(record.payment.payment_intent_id, "other-user", "Please refund")
    a = ops.request_refund(record.payment.payment_intent_id, "user-1", "Please refund")
    b = ops.request_refund(record.payment.payment_intent_id, "user-1", "Please refund again")
    assert a == b and a["state"] == "REQUESTED"
    with pytest.raises(CheckoutBlocked, match="approval"):
        run(ops.dispatch_refund(a["request_id"]))
    ops.review_refund(a["request_id"], approve=False, operator="operator", reason="Denied for test")
    with pytest.raises(CheckoutBlocked):
        run(ops.dispatch_refund(a["request_id"]))
    assert not any("/refund" in str(r.url) for r in env["sandbox"].calls)


def test_refund_exact_terms_claim_and_settlement_duplicate_protection(env):
    record = completed(env)
    calls = transport(env, record)
    ops, reference = approved(env, record)
    first = run(ops.dispatch_refund(reference))
    second = run(ops.dispatch_refund(reference))
    assert first == second and first["state"] == "COMPLETED"
    posts = [r for r in calls if r.method == "POST"]
    assert len(posts) == 1 and posts[0].headers["paypal-request-id"]
    assert env["store"].get_budget("user-1").settled_minor == record.terms.amount_minor
    with env["store"].transaction() as db:
        assert (
            db.execute("SELECT COUNT(*) FROM financial_adjustments WHERE kind='REFUND'").fetchone()[
                0
            ]
            == 1
        )
        assert db.execute("SELECT state FROM refund_attempts").fetchone()[0] == "COMPLETED"
    assert (
        env["store"]
        .get_checkout(record.payment.payment_intent_id, **ACTOR)
        .provider_observation_status
        == "REFUNDED"
    )


def test_ambiguous_refund_never_reposts_even_after_recreation(env):
    record = completed(env)
    calls = transport(env, record, mode="timeout")
    ops, reference = approved(env, record)
    result = run(ops.dispatch_refund(reference))
    assert result["state"] == "UNKNOWN"
    recreated = ProviderOperations(env["store"], env["paypal"])
    assert run(recreated.dispatch_refund(reference)) == result
    with pytest.raises(CheckoutBlocked, match="never repeat POST"):
        run(recreated.reconcile_refund(result["refund_id"]))
    assert len(calls) == 1


def test_pending_refund_get_only_recovery_and_no_downgrade(env):
    record = completed(env)
    transport(env, record, mode="PENDING")
    ops, reference = approved(env, record)
    result = run(ops.dispatch_refund(reference))
    assert result["state"] == "PENDING"
    calls = transport(env, record)
    assert run(ops.reconcile_refund(result["refund_id"]))["state"] == "COMPLETED"
    assert [r.method for r in calls] == ["GET"]
    assert (
        ops._record_refund(result["refund_id"], {"id": "REFUND123", "status": "PENDING"})["state"]
        == "COMPLETED"
    )


@pytest.mark.parametrize(
    "field,value",
    [
        ("amount", {"currency_code": "USD", "value": "0.01"}),
        ("status", "invented"),
        ("id", "../invalid"),
        ("links", [{"rel": "up", "href": "https://evil.test/capture"}]),
    ],
)
def test_refund_adapter_rejects_mismatched_provider_representation(env, field, value):
    record = completed(env)
    payload = refund_payload(record)
    payload[field] = value
    with pytest.raises(PayPalError):
        env["paypal"]._verified_refund(payload, record.capture_id, record.terms)


def test_terminal_monitor_records_refund_without_rewriting_checkout_or_budget(env):
    record = completed(env)
    env["sandbox"].complete(record.order_id, "REFUNDED")
    ops = ProviderOperations(env["store"], env["paypal"])
    observed = run(ops.monitor(record.payment.payment_intent_id, "user-1"))
    assert observed["local_state"] == "SUCCEEDED" and observed["provider_status"] == "REFUNDED"
    env["sandbox"].complete(record.order_id, "COMPLETED")
    assert (
        run(ops.monitor(record.payment.payment_intent_id, "user-1"))["provider_status"]
        == "REFUNDED"
    )
    assert len(env["sandbox"].capture_posts()) == 1
    assert env["store"].get_budget("user-1").settled_minor == record.terms.amount_minor


def event_headers():
    return {
        "paypal-transmission-time": datetime.now(timezone.utc).isoformat(),
        "paypal-auth-algo": "SHA256withRSA",
        "paypal-cert-url": "https://api-m.sandbox.paypal.com/v1/notifications/certs/fake",
        "paypal-transmission-id": "TX123",
        "paypal-transmission-sig": "mocked-signature",
    }


def post_event(env, monkeypatch, payload, *, verified=True):
    record = env["store"].get_checkout(payload.pop("_payment_id"), **ACTOR)
    transport(env, record, verified=verified)
    monkeypatch.setenv("PAYPAL_WEBHOOK_ID", "mock-hook-id")
    # No lifespan startup or real environment provisioning.
    app.state.checkout_service = env["service"]
    try:
        client = TestClient(app)
        return client.post("/v1/provider/paypal/webhook", json=payload, headers=event_headers())
    finally:
        del app.state.checkout_service


def test_verified_reversal_duplicate_event_and_no_budget_recredit(env, monkeypatch):
    record = completed(env)
    payload = {
        "id": "EVENT123",
        "event_type": "PAYMENT.CAPTURE.REVERSED",
        "resource": {"id": record.capture_id, "amount": record.terms.provider_amount()},
        "_payment_id": record.payment.payment_intent_id,
    }
    assert post_event(env, monkeypatch, deepcopy(payload)).json()["provider_status"] == "REVERSED"
    assert post_event(env, monkeypatch, deepcopy(payload)).json()["duplicate"]
    with env["store"].transaction() as db:
        assert (
            db.execute(
                "SELECT COUNT(*) FROM financial_adjustments WHERE kind='REVERSAL'"
            ).fetchone()[0]
            == 1
        )
    assert env["store"].get_budget("user-1").settled_minor == record.terms.amount_minor


def test_unsigned_event_never_changes_financial_records(env, monkeypatch):
    record = completed(env)
    payload = {
        "id": "EVENT123",
        "event_type": "PAYMENT.CAPTURE.REVERSED",
        "resource": {"id": record.capture_id, "amount": record.terms.provider_amount()},
        "_payment_id": record.payment.payment_intent_id,
    }
    assert post_event(env, monkeypatch, payload, verified=False).status_code == 400
    with env["store"].transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM financial_adjustments").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM provider_events").fetchone()[0] == 0


def test_concurrent_refund_dispatch_claim_allows_one_post(env, monkeypatch):
    record = completed(env)
    calls = transport(env, record)
    ops, reference = approved(env, record)
    original = env["paypal"].get_status

    async def delayed(*args, **kwargs):
        await asyncio.sleep(0.01)
        return await original(*args, **kwargs)

    monkeypatch.setattr(env["paypal"], "get_status", delayed)

    async def scenario():
        return await asyncio.gather(ops.dispatch_refund(reference), ops.dispatch_refund(reference))

    results = run(scenario())
    assert all(r["state"] == "COMPLETED" for r in results)
    assert len([r for r in calls if r.method == "POST"]) == 1


@pytest.mark.parametrize(
    "change",
    [
        {"event_type": []},
        {"resource": {"id": "../invalid"}},
        {"resource": {"id": []}},
        {"resource": {"id": "CAP123", "links": [None]}},
        {"resource": {"id": "CAP123", "supplementary_data": []}},
    ],
)
def test_malformed_event_fails_before_provider_verification(env, monkeypatch, change):
    record = completed(env)
    payload = {
        "id": "EVENT123",
        "event_type": "PAYMENT.CAPTURE.REVERSED",
        "resource": {"id": record.capture_id, "amount": record.terms.provider_amount()},
        "_payment_id": record.payment.payment_intent_id,
        **change,
    }
    assert post_event(env, monkeypatch, payload).status_code == 400


def test_external_refund_event_records_one_verified_adjustment(env, monkeypatch):
    record = completed(env)
    payload = {
        "id": "EVENTREFUND123",
        "event_type": "PAYMENT.CAPTURE.REFUNDED",
        "resource": refund_payload(record),
        "_payment_id": record.payment.payment_intent_id,
    }
    assert post_event(env, monkeypatch, deepcopy(payload)).json()["provider_status"] == "REFUNDED"
    assert post_event(env, monkeypatch, deepcopy(payload)).json()["duplicate"]
    with env["store"].transaction() as db:
        assert (
            db.execute("SELECT COUNT(*) FROM financial_adjustments WHERE kind='REFUND'").fetchone()[
                0
            ]
            == 1
        )
        assert db.execute("SELECT COUNT(*) FROM refund_attempts").fetchone()[0] == 0


def test_observed_reversal_blocks_previously_approved_refund(env):
    record = completed(env)
    ops, reference = approved(env, record)
    calls = transport(env, record)
    with env["store"].transaction() as db:
        latest = env["store"].load(db, record.payment.payment_intent_id, "user-1")
        latest.provider_observation_status = "REVERSED"
        env["store"].save(db, latest)
    with pytest.raises(CheckoutBlocked):
        run(ops.dispatch_refund(reference))
    assert not calls


def test_operator_cli_cannot_dispatch_when_refunds_disabled(env, monkeypatch, capsys):
    from app import provider_admin

    record = completed(env)
    _, reference = approved(env, record)
    calls = transport(env, record)
    monkeypatch.setattr(provider_admin, "PayPalSandboxAdapter", lambda _: env["paypal"])
    monkeypatch.setattr(provider_admin.PayPalSettings, "from_env", lambda: env["paypal"]._settings)
    monkeypatch.delenv("RYUK_REFUNDS_ENABLED", raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "provider_admin",
            "dispatch-refund",
            "--reference",
            reference,
            "--database",
            str(env["store"].path),
            "--operator",
            "operator",
            "--reason",
            "test",
        ],
    )
    with pytest.raises(SystemExit) as error:
        provider_admin.main()
    assert error.value.code == 1 and not calls
    with env["store"].transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM refund_attempts").fetchone()[0] == 0
    assert "Do not retry" in capsys.readouterr().err


def test_operator_cli_monitors_terminal_records_get_only_with_audit(env, monkeypatch, capsys):
    from app import provider_admin

    record = completed(env)
    monkeypatch.setattr(provider_admin, "PayPalSandboxAdapter", lambda _: env["paypal"])
    monkeypatch.setattr(provider_admin.PayPalSettings, "from_env", lambda: env["paypal"]._settings)
    monkeypatch.setattr(
        "sys.argv",
        [
            "provider_admin",
            "monitor-batch",
            "--database",
            str(env["store"].path),
            "--operator",
            "operator",
            "--reason",
            "scheduled test",
        ],
    )
    provider_admin.main()
    import json

    response = json.loads(capsys.readouterr().out)
    assert response["next_after"] is None and response["items"][0]["provider_status"] == "COMPLETED"
    assert response["items"][0]["payment_id"] == record.payment.payment_intent_id
    assert len(env["sandbox"].capture_posts()) == 1
    with env["store"].transaction() as db:
        assert (
            db.execute(
                "SELECT COUNT(*) FROM checkout_audit "
                "WHERE event='OPERATOR_PROVIDER_ACTION_REQUESTED'"
            ).fetchone()[0]
            == 1
        )


@pytest.mark.parametrize("status", ["COMPLETED", "REFUNDED"])
def test_late_external_capture_after_local_cancel_accounted_once_without_retry(env, status):
    record = run(ready(env))
    env["service"].cancel(record.payment.payment_intent_id, **ACTOR)
    env["sandbox"].complete(record.order_id, status)
    ops = ProviderOperations(env["store"], env["paypal"])
    first = run(ops.monitor(record.payment.payment_intent_id, "user-1"))
    assert first["local_state"] == "FAILED" and first["provider_status"] == status
    run(ops.monitor(record.payment.payment_intent_id, "user-1"))
    assert env["store"].get_budget("user-1").settled_minor == record.terms.amount_minor
    assert env["store"].get_budget("user-1").reserved_minor == 0
    assert not env["sandbox"].capture_posts()
    with env["store"].transaction() as db:
        assert (
            db.execute(
                "SELECT COUNT(*) FROM financial_adjustments WHERE kind='EXTERNAL_CAPTURE'"
            ).fetchone()[0]
            == 1
        )


def test_reversal_during_refund_preflight_prevents_dispatch(env):
    record = completed(env)
    calls = transport(env, record)
    ops, reference = approved(env, record)

    def reversed_during_get():
        with env["store"].transaction() as db:
            latest = env["store"].load(db, record.payment.payment_intent_id, "user-1")
            latest.provider_observation_status = "REVERSED"
            env["store"].save(db, latest)

    env["sandbox"].on_get = reversed_during_get
    with pytest.raises(CheckoutBlocked):
        run(ops.dispatch_refund(reference))
    assert not calls
    with env["store"].transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM refund_attempts").fetchone()[0] == 0
