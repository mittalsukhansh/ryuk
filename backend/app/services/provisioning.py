"""Opt-in private demo provisioning. Defaults never enable financial access."""

import os
from contextlib import AsyncExitStack

from fastapi import FastAPI

from app.schemas.catalog import CatalogSearchRequest
from app.schemas.policy import BudgetSnapshot, FinancialPolicy
from app.services.approvals import InMemoryApprovalService
from app.services.checkout import CheckoutService
from app.services.checkout_store import CheckoutAccessError, CheckoutStore
from app.services.paypal import PayPalError, PayPalSandboxAdapter, PayPalSettings
from app.services.session import DemoSessions
from app.services.workspace import WorkspaceService


async def provision(application: FastAPI, stack: AsyncExitStack) -> None:
    if os.environ.get("RYUK_DEMO_ENABLED") != "true":
        return
    try:
        origin = os.environ["RYUK_APP_ORIGIN"]
        if not origin.startswith("https://") and not origin.startswith("http://localhost:"):
            raise ValueError
        auth = DemoSessions(
            os.environ["RYUK_DEMO_PASSWORD"],
            origin=origin,
            secure=os.environ.get("RYUK_SECURE_COOKIES", "true") != "false",
        )
        store = CheckoutStore(os.environ["RYUK_CHECKOUT_DB_PATH"])
        try:
            store.get_budget(auth.actor)
        except CheckoutAccessError:
            store.create_account(
                BudgetSnapshot(
                    user_id=auth.actor,
                    currency="USD",
                    limit_minor=int(os.environ.get("RYUK_BUDGET_LIMIT_MINOR", "150000")),
                    settled_minor=0,
                    reserved_minor=0,
                )
            )
            store.put_policy(
                FinancialPolicy(
                    user_id=auth.actor,
                    version="demo-policy-v1",
                    currency="USD",
                    max_amount_minor=150000,
                    approval_threshold_minor=130000,
                    allowed_merchant_ids=frozenset(
                        o.merchant_id
                        for o in application.state.catalog.search(CatalogSearchRequest()).offers
                    ),
                )
            )
        approvals = InMemoryApprovalService()
        application.state.workspace = WorkspaceService(application.state.catalog, store, approvals)
        merchant = os.environ.get("PAYPAL_MERCHANT_ID", "").strip()
        if merchant:
            for offer in application.state.catalog.search(CatalogSearchRequest()).offers:
                store.map_merchant(offer.merchant_id, merchant)
        try:
            settings = PayPalSettings.from_env()
        except PayPalError:
            settings = None
        if settings is not None and merchant:
            paypal = await stack.enter_async_context(PayPalSandboxAdapter(settings))
            application.state.checkout_service = CheckoutService(store, approvals, paypal)
        application.state.demo_sessions = auth
    except (KeyError, ValueError, OSError):
        raise RuntimeError(
            "Invalid private Ryuk demo configuration; check backend settings"
        ) from None
