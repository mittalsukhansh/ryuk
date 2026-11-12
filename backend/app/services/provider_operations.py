"""Audited provider observations and reviewed full refunds; no automatic mutation retries."""

import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.checkout import CheckoutRecord
from app.schemas.provider import RefundReviewState, RefundState
from app.services.checkout import CheckoutBlocked, CheckoutService
from app.services.checkout_store import CheckoutStore
from app.services.durable_approvals import DurableApprovalService
from app.services.paypal import PayPalSandboxAdapter


def refund_binding(record: CheckoutRecord) -> str:
    return hashlib.sha256(
        json.dumps(
            {
                "payment": record.payment.payment_intent_id,
                "owner": record.payment.user_id,
                "digest": record.payment.proposal_digest,
                "capture": record.capture_id,
                "terms": record.terms.model_dump(),
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()


class ProviderOperations:
    def __init__(self, store: CheckoutStore, paypal: PayPalSandboxAdapter) -> None:
        self.store, self.paypal = store, paypal

    async def monitor(self, payment_id: str, actor: str) -> dict:
        """Always verify provider state, including locally terminal attempts."""
        record = self.store.get_checkout(payment_id, actor_user_id=actor)
        if not record.order_id:
            raise CheckoutBlocked(
                "Order creation remains orphaned; operator investigation required"
            )
        result = await self.paypal.get_status(record.order_id, record.terms, capture_attempted=True)
        if record.capture_id and result.capture_id != record.capture_id:
            raise CheckoutBlocked("Provider capture reference mismatch")
        if record.payment.state in {
            "CAPTURE_PENDING",
            "PENDING_PROVIDER",
            "AWAITING_PAYPAL_BUYER",
        } and result.state in {"SUCCEEDED", "FAILED"}:
            coordinator = CheckoutService(
                self.store, DurableApprovalService(self.store), self.paypal
            )
            record = coordinator._finish(payment_id, actor, result)
        status = result.capture_status or result.provider_status
        with self.store.transaction() as connection:
            record = self.store.load(connection, payment_id, actor)
            if record.capture_id and result.capture_id != record.capture_id:
                raise CheckoutBlocked("Provider capture reference mismatch")
            if (
                record.payment.state == "FAILED"
                and result.capture_id
                and (result.state == "SUCCEEDED" or status in {"REFUNDED", "PARTIALLY_REFUNDED"})
            ):
                # A later external capture is financial truth even after local cancellation.
                inserted = connection.execute(
                    "INSERT OR IGNORE INTO financial_adjustments VALUES (?,?,?,?,?,?)",
                    (
                        "external:" + result.capture_id,
                        payment_id,
                        "EXTERNAL_CAPTURE",
                        record.payment.amount_minor,
                        record.payment.currency,
                        datetime.now(timezone.utc).isoformat(),
                    ),
                ).rowcount
                if inserted:
                    connection.execute(
                        "UPDATE accounts SET settled_minor=settled_minor+? WHERE user_id=?",
                        (record.payment.amount_minor, actor),
                    )
                    self.store.audit(
                        connection,
                        payment_id,
                        "EXTERNAL_CAPTURE_ACCOUNTED",
                        datetime.now(timezone.utc),
                    )
            if result.capture_id:
                record.capture_id = result.capture_id
            if not (
                record.provider_observation_status in {"REFUNDED", "REVERSED", "PARTIALLY_REFUNDED"}
                and status not in {"REFUNDED", "REVERSED", "PARTIALLY_REFUNDED"}
            ):
                record.provider_observation_status = status
            self.store.save(connection, record)
            connection.execute(
                "INSERT INTO provider_observations(payment_id,at,capture_status,details) "
                "VALUES (?,?,?,?)",
                (payment_id, datetime.now(timezone.utc).isoformat(), status, "{}"),
            )
            self.store.audit(
                connection,
                payment_id,
                "PROVIDER_OBSERVED",
                datetime.now(timezone.utc),
                {"capture_status": status},
            )
        return {
            "payment_id": payment_id,
            "local_state": record.payment.state,
            "provider_status": record.provider_observation_status,
        }

    def request_refund(self, payment_id: str, actor: str, reason: str) -> dict:
        if not 1 <= len(reason.strip()) <= 200:
            raise ValueError("Bounded refund reason required")
        with self.store.transaction() as connection:
            record = self.store.load(connection, payment_id, actor)
            if record.provider_observation_status in {"REFUNDED", "REVERSED", "PARTIALLY_REFUNDED"}:
                raise CheckoutBlocked("Provider adjustment already recorded")
            if not record.capture_id or not (
                record.payment.state == "SUCCEEDED"
                or record.provider_observation_status == "COMPLETED"
            ):
                raise CheckoutBlocked("Only a confirmed capture may request a refund")
            existing = connection.execute(
                "SELECT request_id,state FROM refund_requests WHERE payment_id=?", (payment_id,)
            ).fetchone()
            if existing:
                return dict(existing)
            request_id = str(uuid4())
            connection.execute(
                "INSERT INTO refund_requests VALUES (?,?,?,?,?,?,?,?,?)",
                (
                    request_id,
                    payment_id,
                    actor,
                    refund_binding(record),
                    RefundReviewState.REQUESTED,
                    reason,
                    None,
                    None,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            self.store.audit(
                connection,
                payment_id,
                "REFUND_REQUESTED",
                datetime.now(timezone.utc),
                {"request_id": request_id},
            )
        return {"request_id": request_id, "state": RefundReviewState.REQUESTED}

    def review_refund(self, request_id: str, *, approve: bool, operator: str, reason: str) -> dict:
        if not all(1 <= len(value.strip()) <= 200 for value in (operator, reason)):
            raise ValueError("Operator and review reason required")
        with self.store.transaction() as connection:
            request = connection.execute(
                "SELECT * FROM refund_requests WHERE request_id=?", (request_id,)
            ).fetchone()
            if not request:
                raise CheckoutBlocked("Refund request unavailable")
            record = self.store.load(connection, request["payment_id"], request["user_id"])
            if refund_binding(record) != request["binding"]:
                raise CheckoutBlocked("Refund terms changed")
            if request["state"] != RefundReviewState.REQUESTED:
                return {"request_id": request_id, "state": request["state"]}
            state = RefundReviewState.APPROVED if approve else RefundReviewState.REJECTED
            connection.execute(
                "UPDATE refund_requests SET state=?,operator=?,operator_reason=? "
                "WHERE request_id=?",
                (state, operator, reason, request_id),
            )
            self.store.audit(
                connection,
                record.payment.payment_intent_id,
                "REFUND_REVIEWED",
                datetime.now(timezone.utc),
                {
                    "request_id": request_id,
                    "decision": state,
                    "operator": operator,
                    "reason": reason,
                },
            )
        return {"request_id": request_id, "state": state}

    async def dispatch_refund(self, request_id: str) -> dict:
        with self.store.transaction() as connection:
            request = connection.execute(
                "SELECT * FROM refund_requests WHERE request_id=?", (request_id,)
            ).fetchone()
            if not request or request["state"] != RefundReviewState.APPROVED:
                raise CheckoutBlocked("Operator approval required")
            record = self.store.load(connection, request["payment_id"], request["user_id"])
            existing = connection.execute(
                "SELECT * FROM refund_attempts WHERE payment_id=?", (request["payment_id"],)
            ).fetchone()
            if existing:
                return {"refund_id": existing["refund_id"], "state": existing["state"]}
        if record.provider_observation_status in {"REFUNDED", "REVERSED", "PARTIALLY_REFUNDED"}:
            raise CheckoutBlocked("Provider adjustment already recorded")
        current = await self.paypal.get_status(
            record.order_id, record.terms, capture_attempted=True
        )
        if current.capture_id != record.capture_id or current.capture_status != "COMPLETED":
            raise CheckoutBlocked(
                "Provider must confirm the original completed capture before refund"
            )
        with self.store.transaction() as connection:
            latest = connection.execute(
                "SELECT * FROM refund_requests WHERE request_id=?", (request_id,)
            ).fetchone()
            record = self.store.load(connection, request["payment_id"], request["user_id"])
            existing = connection.execute(
                "SELECT * FROM refund_attempts WHERE payment_id=?", (request["payment_id"],)
            ).fetchone()
            if existing:
                return {"refund_id": existing["refund_id"], "state": existing["state"]}
            if (
                latest["state"] != RefundReviewState.APPROVED
                or refund_binding(record) != latest["binding"]
                or record.provider_observation_status
                in {"REFUNDED", "REVERSED", "PARTIALLY_REFUNDED"}
            ):
                raise CheckoutBlocked("Refund approval is no longer current")
            refund_id, key = str(uuid4()), str(uuid4())
            connection.execute(
                "INSERT INTO refund_attempts VALUES (?,?,?,?,?,?,?,?,?,?)",
                (
                    refund_id,
                    request["payment_id"],
                    key,
                    RefundState.DISPATCHED,
                    None,
                    record.terms.amount_minor,
                    record.terms.currency,
                    request["operator"],
                    request["operator_reason"],
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            self.store.audit(
                connection,
                request["payment_id"],
                "REFUND_DISPATCH",
                datetime.now(timezone.utc),
                {"refund_id": refund_id},
            )
        try:
            observed = await self.paypal.refund_capture(record.capture_id, record.terms, key=key)
        except Exception:
            with self.store.transaction() as connection:
                connection.execute(
                    "UPDATE refund_attempts SET state='UNKNOWN' WHERE refund_id=?", (refund_id,)
                )
                self.store.audit(
                    connection,
                    request["payment_id"],
                    "REFUND_OUTCOME_UNKNOWN",
                    datetime.now(timezone.utc),
                )
            return {"refund_id": refund_id, "state": RefundState.UNKNOWN}
        return self._record_refund(refund_id, observed)

    def _record_refund(self, refund_id: str, observed: dict) -> dict:
        with self.store.transaction() as connection:
            attempt = connection.execute(
                "SELECT * FROM refund_attempts WHERE refund_id=?", (refund_id,)
            ).fetchone()
            if not attempt:
                raise CheckoutBlocked("Refund attempt unavailable")
            if RefundState(attempt["state"]) == RefundState.COMPLETED:
                return {"refund_id": refund_id, "state": "COMPLETED"}
            connection.execute(
                "UPDATE refund_attempts SET provider_refund_id=?,state=? WHERE refund_id=?",
                (observed["id"], RefundState(observed["status"]), refund_id),
            )
            if observed["status"] == "COMPLETED":
                owner = connection.execute(
                    "SELECT user_id FROM checkouts WHERE payment_id=?", (attempt["payment_id"],)
                ).fetchone()[0]
                record = self.store.load(connection, attempt["payment_id"], owner)
                record.provider_observation_status = "REFUNDED"
                self.store.save(connection, record)
                connection.execute(
                    "INSERT OR IGNORE INTO financial_adjustments VALUES (?,?,?,?,?,?)",
                    (
                        "refund:" + observed["id"],
                        attempt["payment_id"],
                        "REFUND",
                        attempt["amount_minor"],
                        attempt["currency"],
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
            self.store.audit(
                connection,
                attempt["payment_id"],
                "REFUND_OBSERVED",
                datetime.now(timezone.utc),
                {"refund_id": refund_id, "status": observed["status"]},
            )
        return {"refund_id": refund_id, "state": observed["status"]}

    async def reconcile_refund(self, refund_id: str) -> dict:
        with self.store.transaction() as connection:
            attempt = connection.execute(
                "SELECT * FROM refund_attempts WHERE refund_id=?", (refund_id,)
            ).fetchone()
            if not attempt or not attempt["provider_refund_id"]:
                raise CheckoutBlocked(
                    "Refund reference unknown; investigate original request key, never repeat POST"
                )
            owner = connection.execute(
                "SELECT user_id FROM checkouts WHERE payment_id=?", (attempt["payment_id"],)
            ).fetchone()[0]
            record = self.store.load(connection, attempt["payment_id"], owner)
        observed = await self.paypal.get_refund(
            attempt["provider_refund_id"], record.capture_id, record.terms
        )
        return self._record_refund(refund_id, observed)
