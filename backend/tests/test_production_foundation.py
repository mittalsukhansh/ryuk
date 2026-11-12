"""Fresh-ledger migration, identity and resource-boundary regressions."""

import asyncio
import shutil
import sqlite3

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.request_limits import RequestLimits
from app.schemas.policy import FinancialPolicy
from app.services.checkout_store import CheckoutStore
from app.services.local_auth import LocalSessions, provision_user, reset_credentials
from app.services.migrations import DIRECTORY
from app.services.resources import ResourceLimitError, model_lease

PASSWORD = "synthetic-long-password-for-tests"


def policy(actor="actor-1"):
    return FinancialPolicy(
        user_id=actor,
        version="v1",
        currency="USD",
        max_amount_minor=150000,
        approval_threshold_minor=130000,
        allowed_merchant_ids={"seller"},
    )


def test_legacy_upgrade_preserves_budget_and_versions(tmp_path):
    path = tmp_path / "legacy.sqlite3"
    with sqlite3.connect(path) as db:
        db.executescript((DIRECTORY / "001_core.sql").read_text())
        db.execute("INSERT INTO accounts VALUES ('legacy','USD',150000,12345)")
        db.commit()
    for _ in range(2):
        store = CheckoutStore(path)
        assert store.get_budget("legacy").settled_minor == 12345
        with store.transaction() as db:
            assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 4


def test_newer_or_tampered_migrations_fail_closed(tmp_path):
    store = CheckoutStore(tmp_path / "ledger.sqlite3")
    with store.transaction() as db:
        db.execute("UPDATE schema_migrations SET checksum='changed' WHERE version=1")
    with pytest.raises(ValueError, match="checksum"):
        CheckoutStore(store.path)
    with store.transaction() as db:
        db.execute("INSERT INTO schema_migrations VALUES (999,'future','now')")
    with pytest.raises(ValueError, match="newer"):
        CheckoutStore(store.path)


def test_failed_migration_rolls_back_schema_and_marker(tmp_path, monkeypatch):
    directory = tmp_path / "migrations"
    shutil.copytree(DIRECTORY, directory)
    (directory / "005_broken.sql").write_text(
        "CREATE TABLE transient_test(id TEXT);\nINVALID SQL;\n"
    )
    monkeypatch.setattr("app.services.migrations.DIRECTORY", directory)
    path = tmp_path / "broken.sqlite3"
    with pytest.raises(sqlite3.Error):
        CheckoutStore(path)
    with sqlite3.connect(path) as db:
        assert (
            db.execute("SELECT name FROM sqlite_master WHERE name='transient_test'").fetchone()
            is None
        )
        assert (
            db.execute("SELECT name FROM sqlite_master WHERE name='schema_migrations'").fetchone()
            is None
        )


def test_user_bootstrap_atomic_and_policy_version_immutable(tmp_path):
    store = CheckoutStore(tmp_path / "ledger.sqlite3")
    with pytest.raises(ValueError):
        provision_user(store, "buyer-a", PASSWORD, limit_minor=-1, policy=policy())
    with store.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0
    provision_user(store, "buyer-a", PASSWORD, limit_minor=150000, policy=policy())
    with pytest.raises(ValueError, match="immutable"):
        store.put_policy(policy().model_copy(update={"max_amount_minor": 140000}))


def test_sessions_isolated_hashed_persistent_revocable(tmp_path):
    store = CheckoutStore(tmp_path / "ledger.sqlite3")
    for actor in ["actor-1", "actor-2"]:
        provision_user(store, actor, PASSWORD, limit_minor=150000, policy=policy(actor))
    auth = LocalSessions(store, origin="https://example.test", secure=True)
    a = auth.login_user("actor-1", PASSWORD, "a")
    b = auth.login_user("actor-2", PASSWORD, "b")
    recreated = LocalSessions(CheckoutStore(store.path), origin=auth.origin, secure=True)
    assert recreated.actor_for(a) == "actor-1"
    assert recreated.actor_for(b) == "actor-2"
    with store.transaction() as db:
        assert a not in str([tuple(r) for r in db.execute("SELECT * FROM sessions")])
        assert PASSWORD not in str([tuple(r) for r in db.execute("SELECT * FROM users")])
    reset_credentials(store, "actor-1", PASSWORD + "new")
    assert recreated.actor_for(a) is None
    assert recreated.actor_for(b) == "actor-2"
    reset_credentials(store, "actor-2")
    assert recreated.actor_for(b) is None


def test_limit_shared_across_instances_not_clients(tmp_path):
    store = CheckoutStore(tmp_path / "ledger.sqlite3")
    provision_user(store, "buyer-one", PASSWORD, limit_minor=150000, policy=policy())
    for _ in range(5):
        auth = LocalSessions(store, origin="https://example.test", secure=True)
        assert auth.login_user("buyer-one", "wrong", "attacker") is None
    assert auth.login_user("buyer-one", PASSWORD, "attacker") is None
    assert auth.login_user("buyer-one", PASSWORD, "buyer")


def test_model_leases_shared_and_released(tmp_path):
    store = CheckoutStore(tmp_path / "ledger.sqlite3")
    with model_lease(store, "a"), model_lease(CheckoutStore(store.path), "a"):
        with pytest.raises(ResourceLimitError):
            with model_lease(store, "a"):
                pass
        with model_lease(store, "b"):
            pass
    with store.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM resource_leases").fetchone()[0] == 0


def test_backend_body_limits_before_json_parse():
    with TestClient(RequestLimits(FastAPI())) as client:
        assert client.post("/v1/session", content="x" * 65537).status_code == 413
        assert (
            client.post("/v1/session", content="", headers={"Content-Length": "-1"}).status_code
            == 400
        )


def test_chunked_body_and_timeout():
    async def scenario():
        called = []

        async def downstream(scope, receive, send):
            called.append(True)

        messages = []

        async def send(m):
            messages.append(m)

        chunks = iter(
            [
                {"type": "http.request", "body": b"x" * 33000, "more_body": True},
                {"type": "http.request", "body": b"x" * 33000, "more_body": False},
            ]
        )

        async def receive():
            return next(chunks)

        await RequestLimits(downstream)({"type": "http", "headers": []}, receive, send)
        assert messages[0]["status"] == 413 and not called
        messages.clear()

        async def slow():
            await asyncio.sleep(0.1)

        await RequestLimits(downstream, timeout=0.01)({"type": "http", "headers": []}, slow, send)
        assert messages[0]["status"] == 408 and not called

    asyncio.run(scenario())


def test_demo_provisioning_rolls_back_account_policy_and_all_mappings(tmp_path, monkeypatch):
    from contextlib import AsyncExitStack

    from app.services.catalog import CatalogService
    from app.services.provisioning import provision

    path = tmp_path / "atomic.sqlite3"
    store = CheckoutStore(path)
    store.map_merchant("synthetic-hotel-merchant-002", "EXISTINGSELLER")
    values = {
        "RYUK_AUTH_MODE": "demo",
        "RYUK_DEMO_ENABLED": "true",
        "RYUK_DEMO_PASSWORD": PASSWORD,
        "RYUK_APP_ORIGIN": "http://localhost:3000",
        "RYUK_SECURE_COOKIES": "false",
        "RYUK_CHECKOUT_DB_PATH": str(path),
        "PAYPAL_MERCHANT_ID": "DIFFERENTSELLER",
        "APP_ENV": "development",
    }
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    application = FastAPI()
    application.state.catalog = CatalogService()

    async def scenario():
        async with AsyncExitStack() as stack:
            with pytest.raises(RuntimeError):
                await provision(application, stack)

    asyncio.run(scenario())
    with store.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM accounts").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM policies").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM policy_versions").fetchone()[0] == 0
        assert db.execute("SELECT COUNT(*) FROM merchants").fetchone()[0] == 1
        assert db.execute("SELECT paypal_id FROM merchants").fetchone()[0] == "EXISTINGSELLER"


def test_concurrent_startups_migrate_once(tmp_path):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    for attempt in range(5):
        path = tmp_path / f"concurrent-{attempt}.sqlite3"
        barrier = Barrier(2)

        def open_store(_):
            barrier.wait()
            return CheckoutStore(path)

        with ThreadPoolExecutor(max_workers=2) as pool:
            stores = list(pool.map(open_store, range(2)))
    with stores[0].transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM schema_migrations").fetchone()[0] == 4


def test_model_quota_shared_per_actor_and_credential_expiry(tmp_path, monkeypatch):
    store = CheckoutStore(tmp_path / "ledger.sqlite3")
    provision_user(store, "buyer-one", PASSWORD, limit_minor=150000, policy=policy())
    auth = LocalSessions(store, origin="https://example.test", secure=True)
    token = auth.login_user("buyer-one", PASSWORD, "client")
    for _ in range(10):
        assert LocalSessions(store, origin=auth.origin, secure=True).allow_model_request("actor-1")
    assert not auth.allow_model_request("actor-1")
    assert auth.allow_model_request("actor-2")
    monkeypatch.setattr("app.services.local_auth.time.time", lambda: 10**12)
    assert auth.actor_for(token) is None


def test_inflight_admission_is_bounded_and_released():
    async def scenario():
        entered, release = asyncio.Event(), asyncio.Event()

        async def downstream(scope, receive, send):
            entered.set()
            await release.wait()

        async def receive():
            return {"type": "http.request", "body": b""}

        messages = []

        async def send(message):
            messages.append(message)

        middleware = RequestLimits(downstream, max_inflight=1)
        scope = {"type": "http", "headers": []}
        first = asyncio.create_task(middleware(scope, receive, send))
        await entered.wait()
        await middleware(scope, receive, send)
        assert messages[0]["status"] == 429
        release.set()
        await first
        messages.clear()
        await middleware(scope, receive, send)
        assert not messages

    asyncio.run(scenario())


def test_global_hash_leases_expire_and_bound_independent_clients(tmp_path):
    import time
    from contextlib import ExitStack

    from app.services.resources import operation_lease

    store = CheckoutStore(tmp_path / "ledger.sqlite3")
    with store.transaction() as db:
        db.execute(
            "INSERT INTO resource_leases VALUES (?,?,?,?)",
            ("orphan", "old", "login", time.time() - 1),
        )
    with ExitStack() as stack:
        for number in range(4):
            stack.enter_context(
                operation_lease(store, str(number), kind="login", global_limit=4, actor_limit=2)
            )
        with pytest.raises(ResourceLimitError):
            with operation_lease(
                CheckoutStore(store.path), "fifth", kind="login", global_limit=4, actor_limit=2
            ):
                pass
    with store.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM resource_leases").fetchone()[0] == 0
