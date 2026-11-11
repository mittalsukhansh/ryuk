"""Authenticated frontend seams; existing services retain all financial authority."""

import os
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import Field, SecretStr

from app.api.agent import get_intent_parser, parse_intent, require_model_actor
from app.api.checkout import Actor, _errors
from app.schemas import ApprovalRequest
from app.schemas.domain import DomainModel
from app.schemas.intent_parser import ParseIntentRequest
from app.services.intent_parser import IntentParser
from app.services.session import COOKIE_NAME, SESSION_SECONDS, DemoSessions
from app.services.workspace import WorkspaceService

router = APIRouter(prefix="/v1", tags=["workspace"])


class Login(DomainModel):
    password: SecretStr = Field(min_length=1, max_length=1024)


class Decision(DomainModel):
    decision: Literal["APPROVE", "REJECT"]


class EmptyAction(DomainModel):
    pass


def sessions(request: Request) -> DemoSessions:
    auth = getattr(request.app.state, "demo_sessions", None)
    if not isinstance(auth, DemoSessions):
        raise HTTPException(status_code=503, detail="Private workspace is not configured")
    return auth


def workspace(request: Request) -> WorkspaceService:
    service = getattr(request.app.state, "workspace", None)
    if not isinstance(service, WorkspaceService):
        raise HTTPException(status_code=503, detail="Private workspace is not configured")
    return service


Workspace = Annotated[WorkspaceService, Depends(workspace)]


def check_origin(request: Request, auth: DemoSessions) -> None:
    if request.headers.get("origin") != auth.origin:
        raise HTTPException(status_code=403, detail="Request origin is not allowed")


@router.get("/session")
def session_status(request: Request) -> dict:
    auth = getattr(request.app.state, "demo_sessions", None)
    return {
        "configured": isinstance(auth, DemoSessions),
        "authenticated": bool(auth and auth.actor_for(request.cookies.get(COOKIE_NAME))),
    }


@router.post("/session")
def login(body: Login, request: Request, response: Response) -> dict:
    auth = sessions(request)
    check_origin(request, auth)
    token = auth.login(
        body.password.get_secret_value(), request.client.host if request.client else "local"
    )
    if token is None:
        raise HTTPException(status_code=401, detail="Sign-in failed or temporarily limited")
    response.set_cookie(
        COOKIE_NAME,
        token,
        httponly=True,
        secure=auth.secure,
        samesite="strict",
        max_age=SESSION_SECONDS,
        path="/",
    )
    response.headers["Cache-Control"] = "no-store"
    return {"authenticated": True}


@router.delete("/session")
def logout(request: Request, response: Response) -> dict:
    auth = sessions(request)
    check_origin(request, auth)
    auth.logout(request.cookies.get(COOKIE_NAME))
    response.delete_cookie(
        COOKIE_NAME, path="/", secure=auth.secure, httponly=True, samesite="strict"
    )
    return {"authenticated": False}


@router.get("/workspace")
def get_workspace(request: Request, actor: Actor, service: Workspace) -> dict:
    with _errors(), service.store.transaction() as connection:
        budget = service.store.budget(connection, actor)
        return {
            "budget": (
                budget.model_dump(mode="json") | {"available_minor": budget.remaining_minor}
            ),
            "policy": service.store.policy(connection, actor).model_dump(mode="json"),
            "paypal": {
                "configured": bool(getattr(request.app.state, "checkout_service", None)),
                "client_id": os.environ.get("PAYPAL_CLIENT_ID", ""),
                "environment": "sandbox",
            },
            "synthetic": True,
        }


@router.post("/requests", dependencies=[Depends(require_model_actor)])
async def investigate(
    body: ParseIntentRequest,
    actor: Actor,
    service: Workspace,
    parser: Annotated[IntentParser, Depends(get_intent_parser)],
) -> dict:
    intent = await parse_intent(body, parser)
    if intent.category.strip().casefold() != "hotel":
        raise HTTPException(
            status_code=422, detail="This workspace currently supports hotel requests only"
        )
    with _errors():
        return service.investigate(intent, actor)


@router.get("/proposals/{proposal_id}")
def proposal(proposal_id: str, actor: Actor, service: Workspace) -> dict:
    with _errors():
        return service.describe(proposal_id, actor)


@router.post("/proposals/{proposal_id}/select")
def select(proposal_id: str, body: EmptyAction, actor: Actor, service: Workspace) -> dict:
    with _errors():
        result = service.describe(proposal_id, actor)
        service.event(proposal_id, "OFFER_SELECTED")
        return result


@router.post("/proposals/{proposal_id}/approval", response_model=ApprovalRequest)
def request_approval(
    proposal_id: str, body: EmptyAction, actor: Actor, service: Workspace
) -> ApprovalRequest:
    with _errors():
        return service.request_approval(proposal_id, actor)


@router.post("/approvals/{request_id}/decision", response_model=ApprovalRequest)
def decide(request_id: str, body: Decision, actor: Actor, service: Workspace) -> ApprovalRequest:
    with _errors():
        return service.decide(request_id, actor, body.decision)


@router.get("/proposals/{proposal_id}/audit")
def audit(proposal_id: str, actor: Actor, service: Workspace) -> dict:
    with _errors():
        return {"events": service.timeline(proposal_id, actor)}
