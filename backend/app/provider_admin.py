"""Local operator provider review/monitoring. Never execute against live accounts in tests."""

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone

from app.services.checkout_store import CheckoutStore
from app.services.paypal import PayPalSandboxAdapter, PayPalSettings
from app.services.provider_operations import ProviderOperations


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=[
            "list-requests",
            "approve",
            "reject",
            "dispatch-refund",
            "reconcile-refund",
            "monitor",
            "monitor-batch",
        ],
    )
    parser.add_argument("--reference")
    parser.add_argument("--after", type=int, default=0)
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--operator")
    parser.add_argument("--reason")
    parser.add_argument("--database", default=os.environ.get("RYUK_CHECKOUT_DB_PATH"))
    args = parser.parse_args()
    if args.after < 0 or not 1 <= args.limit <= 50:
        parser.error("Use nonnegative --after and --limit 1–50")
    if not args.database:
        parser.error("Existing database path required")
    from pathlib import Path

    if not Path(args.database).is_file():
        parser.error("Existing database required; no new ledger is created")
    store = CheckoutStore(args.database)
    if args.action == "list-requests":
        with store.transaction() as connection:
            result = [
                dict(row)
                for row in connection.execute(
                    "SELECT request_id,payment_id,state,buyer_reason FROM refund_requests "
                    "ORDER BY created_at DESC LIMIT 100"
                )
            ]
        print(json.dumps(result))
        return
    if (
        (not args.reference and args.action != "monitor-batch")
        or not args.operator
        or not args.reason
    ):
        parser.error("Explicit --reference, --operator and --reason required")

    if not all(1 <= len(value.strip()) <= 200 for value in (args.operator, args.reason)):
        parser.error("Operator and reason must have 1–200 characters")

    def audit_request(payment_id: str) -> None:
        with store.transaction() as connection:
            store.audit(
                connection,
                payment_id,
                "OPERATOR_PROVIDER_ACTION_REQUESTED",
                datetime.now(timezone.utc),
                {"action": args.action, "operator": args.operator, "reason": args.reason},
            )

    async def run() -> dict:
        async with PayPalSandboxAdapter(PayPalSettings.from_env()) as paypal:
            operations = ProviderOperations(store, paypal)
            if args.action in {"approve", "reject"}:
                return operations.review_refund(
                    args.reference,
                    approve=args.action == "approve",
                    operator=args.operator,
                    reason=args.reason,
                )
            if (
                os.environ.get("RYUK_REFUNDS_ENABLED") != "true"
                and args.action == "dispatch-refund"
            ):
                raise ValueError("Refund execution must be explicitly enabled")
            if args.action in {"dispatch-refund", "reconcile-refund"}:
                with store.transaction() as connection:
                    if args.action == "dispatch-refund":
                        row = connection.execute(
                            "SELECT payment_id FROM refund_requests WHERE request_id=?",
                            (args.reference,),
                        ).fetchone()
                    else:
                        row = connection.execute(
                            "SELECT payment_id FROM refund_attempts WHERE refund_id=?",
                            (args.reference,),
                        ).fetchone()
                if not row:
                    raise ValueError("Refund reference unavailable")
                audit_request(row["payment_id"])
            if args.action == "dispatch-refund":
                return await operations.dispatch_refund(args.reference)
            if args.action == "reconcile-refund":
                return await operations.reconcile_refund(args.reference)
            if args.action == "monitor-batch":
                with store.transaction() as connection:
                    rows = connection.execute(
                        "SELECT rowid,payment_id,user_id FROM checkouts WHERE rowid>? "
                        "ORDER BY rowid LIMIT ?",
                        (args.after, args.limit + 1),
                    ).fetchall()
                results = []
                for row in rows[: args.limit]:
                    audit_request(row["payment_id"])
                    try:
                        observed = await operations.monitor(row["payment_id"], row["user_id"])
                    except Exception:
                        observed = {
                            "payment_id": row["payment_id"],
                            "error": "Observation unavailable",
                        }
                    results.append(observed)
                return {
                    "items": results,
                    "next_after": rows[args.limit - 1]["rowid"] if len(rows) > args.limit else None,
                }
            with store.transaction() as connection:
                owner = connection.execute(
                    "SELECT user_id FROM checkouts WHERE payment_id=?", (args.reference,)
                ).fetchone()
                if not owner:
                    raise ValueError("Checkout not found")
                store.audit(
                    connection,
                    args.reference,
                    "OPERATOR_PROVIDER_MONITOR_REQUESTED",
                    datetime.now(timezone.utc),
                    {"operator": args.operator, "reason": args.reason},
                )
            return await operations.monitor(args.reference, owner["user_id"])

    try:
        print(json.dumps(asyncio.run(run())))
    except Exception:
        parser.exit(
            1,
            "Provider operation unavailable; inspect original references. "
            "Do not retry a mutation blindly.\n",
        )


if __name__ == "__main__":
    main()
