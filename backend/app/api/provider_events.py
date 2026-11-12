"""Authenticated PayPal event processing; browser callbacks never reach this authority."""

import os
from datetime import datetime, timezone
from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Request

from app.schemas.provider import ProviderEvent
from app.services.checkout import CheckoutBlocked
from app.services.paypal import PayPalError, _amount_matches, _identifier
from app.services.provider_operations import ProviderOperations

router = APIRouter(prefix="/v1/provider/paypal", tags=["provider"])


@router.post("/webhook")
async def webhook(request: Request) -> dict:
    coordinator = getattr(request.app.state, "checkout_service", None)
    webhook_id = os.environ.get("PAYPAL_WEBHOOK_ID", "")
    if coordinator is None or not webhook_id:
        raise HTTPException(503, "Provider event verification is not configured")
    try:
        event = await request.json()
        ProviderEvent.model_validate(event)
        event_id = _identifier(event["id"])
        event_type = event["event_type"]
        resource = event["resource"]
        resource_id = _identifier(resource["id"])
        if not isinstance(event_type, str) or not 1 <= len(event_type) <= 128:
            raise ValueError
        related = resource.get("supplementary_data", {}).get("related_ids", {})
        related_order = related.get("order_id")
        if related_order is not None:
            related_order = _identifier(related_order)
        links = resource.get("links", [])
        if (
            not isinstance(links, list)
            or len(links) > 20
            or any(
                not isinstance(link, dict) or not isinstance(link.get("href", ""), str)
                for link in links
            )
        ):
            raise ValueError
        for link in links:
            parsed_link = urlsplit(link.get("href", ""))
            _ = parsed_link.port
        headers = dict(request.headers)
        sent = datetime.fromisoformat(headers["paypal-transmission-time"].replace("Z", "+00:00"))
        if sent.tzinfo is None or abs((datetime.now(timezone.utc) - sent).total_seconds()) > 300:
            raise ValueError
    except (KeyError, ValueError, TypeError, AttributeError, PayPalError):
        raise HTTPException(400, "Invalid provider event") from None
    store = coordinator.store
    with store.transaction() as connection:
        now = datetime.now(timezone.utc).timestamp()
        connection.execute("DELETE FROM rate_events WHERE at<?", (now - 60,))
        if (
            connection.execute(
                "SELECT COUNT(*) FROM rate_events WHERE bucket='webhook'"
            ).fetchone()[0]
            >= 30
        ):
            raise HTTPException(429, "Provider event verification allowance reached")
        connection.execute("INSERT INTO rate_events VALUES ('webhook',?)", (now,))
    try:
        if not await coordinator.paypal.verify_webhook(headers, event, webhook_id):
            raise HTTPException(400, "Provider event signature verification failed")
    except PayPalError:
        raise HTTPException(503, "Provider event verification unavailable") from None
    with store.transaction() as connection:
        if connection.execute(
            "SELECT 1 FROM provider_events WHERE event_id=?", (event_id,)
        ).fetchone():
            return {"accepted": True, "duplicate": True}
    if event_type not in {
        "PAYMENT.CAPTURE.COMPLETED",
        "PAYMENT.CAPTURE.PENDING",
        "PAYMENT.CAPTURE.DENIED",
        "PAYMENT.CAPTURE.REFUNDED",
        "PAYMENT.CAPTURE.REVERSED",
    }:
        return {"accepted": True, "matched": False}
    # Signature-verified resource links may identify a capture, but never choose a fetch URL.
    capture_id = resource_id
    if event_type == "PAYMENT.CAPTURE.REFUNDED":
        capture_id = None
        for link in resource.get("links", []):
            if link.get("rel") == "up":
                parsed = urlsplit(link.get("href", ""))
                if (
                    parsed.scheme == "https"
                    and parsed.hostname in {"api-m.sandbox.paypal.com", "api.sandbox.paypal.com"}
                    and parsed.path.startswith("/v2/payments/captures/")
                    and not (parsed.username or parsed.password or parsed.query or parsed.fragment)
                    and parsed.port in {None, 443}
                ):
                    capture_id = parsed.path.rsplit("/", 1)[-1]
    target = None
    from app.schemas.checkout import CheckoutRecord

    with store.transaction() as connection:
        candidate = connection.execute(
            "SELECT body FROM checkouts WHERE json_extract(body,'$.capture_id')=? "
            "OR (json_extract(body,'$.capture_id') IS NULL "
            "AND json_extract(body,'$.order_id')=?) LIMIT 1",
            (capture_id, related_order),
        ).fetchone()
        if candidate:
            target = CheckoutRecord.model_validate_json(candidate["body"])
    if target is None:
        return {"accepted": True, "matched": False}
    operations = ProviderOperations(store, coordinator.paypal)
    try:
        observed = await operations.monitor(
            target.payment.payment_intent_id, target.payment.user_id
        )
        target = store.get_checkout(
            target.payment.payment_intent_id, actor_user_id=target.payment.user_id
        )
        if target.capture_id != capture_id:
            raise ValueError("Verified capture reference differs from event")
        if event_type == "PAYMENT.CAPTURE.REFUNDED":
            refund = await coordinator.paypal.get_refund(
                resource_id, target.capture_id, target.terms
            )
            with store.transaction() as connection:
                attempt = connection.execute(
                    "SELECT refund_id FROM refund_attempts WHERE payment_id=?",
                    (target.payment.payment_intent_id,),
                ).fetchone()
            if attempt:
                operations._record_refund(attempt["refund_id"], refund)
            elif refund["status"] == "COMPLETED":
                with store.transaction() as connection:
                    connection.execute(
                        "INSERT OR IGNORE INTO financial_adjustments VALUES (?,?,?,?,?,?)",
                        (
                            "refund:" + refund["id"],
                            target.payment.payment_intent_id,
                            "REFUND",
                            target.terms.amount_minor,
                            target.terms.currency,
                            datetime.now(timezone.utc).isoformat(),
                        ),
                    )
                    latest = store.load(
                        connection, target.payment.payment_intent_id, target.payment.user_id
                    )
                    latest.provider_observation_status = "REFUNDED"
                    store.save(connection, latest)
    except (PayPalError, ValueError, CheckoutBlocked):
        raise HTTPException(
            503, "Provider observation unavailable; event not acknowledged"
        ) from None
    with store.transaction() as connection:
        inserted = connection.execute(
            "INSERT OR IGNORE INTO provider_events VALUES (?,?,?,?)",
            (event_id, event_type, resource_id, datetime.now(timezone.utc).isoformat()),
        ).rowcount
        if inserted and event_type == "PAYMENT.CAPTURE.REVERSED":
            if not _amount_matches(resource.get("amount"), target.terms):
                raise HTTPException(409, "Reversal amount does not match the recorded capture")
            connection.execute(
                "INSERT OR IGNORE INTO financial_adjustments VALUES (?,?,?,?,?,?)",
                (
                    "reversal:" + target.capture_id,
                    target.payment.payment_intent_id,
                    "REVERSAL",
                    target.terms.amount_minor,
                    target.terms.currency,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            latest = store.load(
                connection, target.payment.payment_intent_id, target.payment.user_id
            )
            latest.provider_observation_status = "REVERSED"
            store.save(connection, latest)
        if inserted:
            store.audit(
                connection,
                target.payment.payment_intent_id,
                "PROVIDER_EVENT_VERIFIED",
                datetime.now(timezone.utc),
                {"event_id": event_id, "event_type": event_type},
            )
    latest = store.get_checkout(
        target.payment.payment_intent_id, actor_user_id=target.payment.user_id
    )
    return {
        "accepted": True,
        "matched": True,
        "provider_status": latest.provider_observation_status or observed["provider_status"],
    }
