"""Local accounts opt in; shared demo remains compatible; ownership tested over HTTP."""

from test_workspace import GOLD, ORIGIN
from test_workspace import client as workspace_client

from app.main import app
from app.schemas.policy import FinancialPolicy
from app.services.local_auth import LocalSessions, provision_user, reset_credentials
from app.services.session import COOKIE_NAME

client = workspace_client
PASSWORD = "synthetic-local-long-password"


def sign_in(client, username):
    client.cookies.clear()
    response = client.post(
        "/v1/session", headers=ORIGIN, json={"username": username, "password": PASSWORD}
    )
    assert response.status_code == 200
    return client.cookies.get(COOKIE_NAME)


def test_http_local_users_cannot_read_or_mutate_another_buyers_records(client):
    store = app.state.workspace.store
    for actor in ["buyer-one", "buyer-two"]:
        provision_user(
            store,
            actor,
            PASSWORD,
            limit_minor=300000,
            policy=FinancialPolicy(
                user_id=actor,
                version="v1",
                currency="USD",
                max_amount_minor=150000,
                approval_threshold_minor=130000,
                allowed_merchant_ids={
                    "synthetic-hotel-merchant-001",
                    "synthetic-hotel-merchant-002",
                },
            ),
        )
    app.state.demo_sessions = LocalSessions(store, origin=ORIGIN["Origin"], secure=False)
    assert client.get("/v1/session").json()["login_mode"] == "local"
    first = sign_in(client, "buyer-one")
    response = client.post("/v1/requests", json={"query": GOLD["query"]}, headers=ORIGIN)
    assert response.status_code == 200, response.text
    proposal = response.json()["candidates"][0]["proposal"]
    pid = proposal["proposal_id"]
    assert len(client.get("/v1/history").json()["items"]) > 0
    sign_in(client, "buyer-two")
    assert client.get("/v1/history").json()["items"] == []
    assert client.get(f"/v1/proposals/{pid}").status_code == 404
    assert client.get(f"/v1/proposals/{pid}/audit").status_code == 404
    assert client.post(f"/v1/proposals/{pid}/approval", json={}, headers=ORIGIN).status_code == 404
    assert (
        client.post("/v1/checkouts", json={"proposal_id": pid}, headers=ORIGIN).status_code == 404
    )
    assert client.get("/v1/workspace").json()["budget"]["settled_minor"] == 0
    reset_credentials(store, "buyer-one")
    client.cookies.clear()
    client.cookies.set(COOKIE_NAME, first)
    assert client.get("/v1/history").status_code == 401
    assert not client.sandbox.orders
