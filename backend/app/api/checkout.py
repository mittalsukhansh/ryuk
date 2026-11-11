"""Identifier-only checkout API. Authentication and backend authority are required.

Deployment must install a trusted authentication dependency and provision the
service. Neither browser user IDs nor unsigned identity headers are accepted.
"""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request

from app.schemas.checkout import CheckoutRecord, OrderCreationState
from app.schemas.domain import Currency, DomainModel, MinorUnits, NonEmptyString, PaymentState
from app.services.approvals import ApprovalAccessError, ApprovalPolicyError, ApprovalStateError
from app.services.checkout import CheckoutBlocked, CheckoutService, CheckoutUnavailable
from app.services.checkout_store import CheckoutAccessError

router = APIRouter(prefix="/v1/checkouts", tags=["checkout"])


class CreateCheckout(DomainModel):
    proposal_id: NonEmptyString


class CheckoutAction(DomainModel):
    """Empty JSON action: client amount/merchant/user/status/approval are forbidden."""


class CheckoutView(DomainModel):
    checkout_id: str
    state: PaymentState
    order_creation: OrderCreationState
    paypal_order_id: str | None
    amount_minor: MinorUnits
    currency: Currency
    merchant_id: str


def get_checkout_actor() -> str:
    """Fail closed until a real server-side session/token verifier is configured."""
    raise HTTPException(status_code=503, detail="Checkout authentication is not configured")


def get_checkout_service(request: Request) -> CheckoutService:
    service = getattr(request.app.state, "checkout_service", None)
    if not isinstance(service, CheckoutService):
        raise HTTPException(status_code=503, detail="Checkout service is not configured")
    return service


Actor = Annotated[str, Depends(get_checkout_actor)]
Service = Annotated[CheckoutService, Depends(get_checkout_service)]


def _view(record: CheckoutRecord) -> CheckoutView:
    return CheckoutView(
        checkout_id=record.payment.payment_intent_id,
        state=record.payment.state,
        order_creation=record.order_creation,
        paypal_order_id=record.order_id,
        amount_minor=record.payment.amount_minor,
        currency=record.payment.currency,
        merchant_id=record.payment.merchant_id,
    )


@contextmanager
def _errors() -> Iterator[None]:
    try:
        yield
    except (ApprovalAccessError, CheckoutAccessError):
        raise HTTPException(status_code=404, detail="Checkout or proposal not available") from None
    except ApprovalPolicyError as error:
        raise HTTPException(
            status_code=409,
            detail={
                "decision": error.decision.decision,
                "reason_codes": error.decision.reason_codes,
            },
        ) from None
    except (CheckoutBlocked, ApprovalStateError):
        raise HTTPException(
            status_code=409, detail="Current checkout conditions block this action"
        ) from None
    except (CheckoutUnavailable, sqlite3.Error, ValueError):
        raise HTTPException(
            status_code=503, detail="Checkout unavailable; inspect persisted state"
        ) from None


@router.post("", response_model=CheckoutView)
async def create_checkout(body: CreateCheckout, actor: Actor, service: Service) -> CheckoutView:
    with _errors():
        return _view(await service.create_checkout(body.proposal_id, actor_user_id=actor))


@router.get("/{checkout_id}", response_model=CheckoutView)
def get_checkout(checkout_id: str, actor: Actor, service: Service) -> CheckoutView:
    with _errors():
        return _view(service.store.get_checkout(checkout_id, actor_user_id=actor))


@router.post("/{checkout_id}/capture", response_model=CheckoutView)
async def capture(
    checkout_id: str, body: CheckoutAction, actor: Actor, service: Service
) -> CheckoutView:
    with _errors():
        return _view(await service.capture(checkout_id, actor_user_id=actor))


@router.post("/{checkout_id}/reconcile", response_model=CheckoutView)
async def reconcile(
    checkout_id: str, body: CheckoutAction, actor: Actor, service: Service
) -> CheckoutView:
    with _errors():
        return _view(await service.reconcile(checkout_id, actor_user_id=actor))


@router.post("/{checkout_id}/cancel", response_model=CheckoutView)
def cancel(checkout_id: str, body: CheckoutAction, actor: Actor, service: Service) -> CheckoutView:
    with _errors():
        return _view(service.cancel(checkout_id, actor_user_id=actor))
