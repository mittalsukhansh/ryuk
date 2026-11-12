"""Database-backed bounded operation leases; never hold a DB transaction across I/O."""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from uuid import uuid4

from app.services.checkout_store import CheckoutStore


class ResourceLimitError(RuntimeError):
    """A safe quota exceeded response; no user input reflected."""


@contextmanager
def operation_lease(
    store: CheckoutStore, actor: str, *, kind: str, global_limit: int, actor_limit: int
) -> Iterator[None]:
    now = time.time()
    lease = str(uuid4())
    with store.transaction() as connection:
        connection.execute("DELETE FROM resource_leases WHERE expires_at<=?", (now,))
        count = connection.execute(
            "SELECT COUNT(*) FROM resource_leases WHERE kind=?", (kind,)
        ).fetchone()[0]
        owned = connection.execute(
            "SELECT COUNT(*) FROM resource_leases WHERE kind=? AND user_id=?", (kind, actor)
        ).fetchone()[0]
        if count >= global_limit or owned >= actor_limit:
            raise ResourceLimitError("Operation concurrency limit reached")
        connection.execute(
            "INSERT INTO resource_leases VALUES (?,?,?,?)", (lease, actor, kind, now + 60)
        )
    try:
        yield
    finally:
        with store.transaction() as connection:
            connection.execute("DELETE FROM resource_leases WHERE lease_id=?", (lease,))


@contextmanager
def model_lease(store: CheckoutStore, actor: str) -> Iterator[None]:
    with operation_lease(store, actor, kind="model", global_limit=8, actor_limit=2):
        yield
