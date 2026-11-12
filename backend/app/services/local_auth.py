"""Operator-provisioned local identities and revocable, hashed persistent sessions."""

import hashlib
import hmac
import re
import secrets
import time
from datetime import datetime, timezone

from app.schemas.policy import BudgetSnapshot, FinancialPolicy
from app.services.checkout_store import CheckoutStore
from app.services.resources import ResourceLimitError, operation_lease
from app.services.session import SESSION_SECONDS, DemoSessions


def password_digest(password: str, salt: str) -> str:
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()


def provision_user(
    store: CheckoutStore, username: str, password: str, *, limit_minor: int, policy: FinancialPolicy
) -> str:
    """Create identity, account and policy atomically; never overwrite another account."""
    username = username.strip().casefold()
    if (
        not re.fullmatch(r"[a-z0-9][a-z0-9_.@+-]{2,127}", username)
        or not 16 <= len(password) <= 1024
    ):
        raise ValueError("Valid username and password of 16–1024 characters required")
    user_id = policy.user_id
    salt = secrets.token_hex(32)
    digest = password_digest(password, salt)
    with store.transaction() as connection:
        connection.execute(
            "INSERT INTO users(user_id,username,password_hash,salt) VALUES (?,?,?,?)",
            (user_id, username, digest, salt),
        )
        store.create_account(
            BudgetSnapshot(
                user_id=user_id,
                currency=policy.currency,
                limit_minor=limit_minor,
                settled_minor=0,
                reserved_minor=0,
            )
        )
        store.put_policy(policy)
        connection.execute(
            "INSERT INTO identity_events(user_id,event,at) VALUES (?,?,?)",
            (user_id, "USER_CREATED", datetime.now(timezone.utc).isoformat()),
        )
    return user_id


def reset_credentials(store: CheckoutStore, username: str, password: str | None = None) -> None:
    """Operator reset/revoke; all sessions invalidated atomically, finances unchanged."""
    if password is not None and not 16 <= len(password) <= 1024:
        raise ValueError("Password must have 16–1024 characters")
    with store.transaction() as connection:
        row = connection.execute(
            "SELECT user_id FROM users WHERE username=?", (username.strip().casefold(),)
        ).fetchone()
        if row is None:
            raise ValueError("Account unavailable")
        if password is not None:
            salt = secrets.token_hex(32)
            connection.execute(
                "UPDATE users SET password_hash=?,salt=?,credential_version="
                "credential_version+1 WHERE user_id=?",
                (password_digest(password, salt), salt, row["user_id"]),
            )
        else:
            connection.execute(
                "UPDATE users SET enabled=0,credential_version=credential_version+1 "
                "WHERE user_id=?",
                (row["user_id"],),
            )
        connection.execute("DELETE FROM sessions WHERE user_id=?", (row["user_id"],))
        connection.execute(
            "INSERT INTO identity_events(user_id,event,at) VALUES (?,?,?)",
            (
                row["user_id"],
                "CREDENTIALS_RESET" if password is not None else "USER_DISABLED",
                datetime.now(timezone.utc).isoformat(),
            ),
        )


class LocalSessions(DemoSessions):
    """No public registration; per-actor policies and ownership remain backend-controlled."""

    def __init__(
        self, store: CheckoutStore, *, origin: str, secure: bool, proxy_secret: str | None = None
    ) -> None:
        super().__init__(
            "unused-local-auth-initializer", origin=origin, secure=secure, proxy_secret=proxy_secret
        )
        self.store = store
        self._dummy_salt = secrets.token_hex(32)
        self._dummy_hash = password_digest(secrets.token_hex(32), self._dummy_salt)

    def login_user(self, username: str, password: str, client: str) -> str | None:
        now = time.time()
        bucket = "login:" + hashlib.sha256(client.encode()).hexdigest()
        with self.store.transaction() as connection:
            connection.execute("DELETE FROM rate_events WHERE at<?", (now - 60,))
            if (
                connection.execute(
                    "SELECT COUNT(*) FROM rate_events WHERE bucket=?", (bucket,)
                ).fetchone()[0]
                >= 5
            ):
                return None
            if connection.execute("SELECT COUNT(*) FROM rate_events").fetchone()[0] >= 5120:
                return None
            connection.execute("INSERT INTO rate_events VALUES (?,?)", (bucket, now))
            row = connection.execute(
                "SELECT * FROM users WHERE username=?", (username.strip().casefold(),)
            ).fetchone()
        try:
            with operation_lease(self.store, bucket, kind="login", global_limit=4, actor_limit=2):
                actual = password_digest(password, row["salt"] if row else self._dummy_salt)
        except ResourceLimitError:
            return None
        expected = row["password_hash"] if row else self._dummy_hash
        if not hmac.compare_digest(actual, expected) or row is None or not row["enabled"]:
            return None
        with self.store.transaction() as connection:
            current = connection.execute(
                "SELECT * FROM users WHERE user_id=?", (row["user_id"],)
            ).fetchone()
            if (
                not current
                or not current["enabled"]
                or (
                    current["credential_version"] != row["credential_version"]
                    or current["password_hash"] != row["password_hash"]
                )
            ):
                return None
            connection.execute("DELETE FROM sessions WHERE expires_at<=?", (now,))
            if (
                connection.execute(
                    "SELECT COUNT(*) FROM sessions WHERE user_id=?", (row["user_id"],)
                ).fetchone()[0]
                >= 8
            ):
                return None
            if connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0] >= 1024:
                return None
            token = secrets.token_urlsafe(32)
            connection.execute(
                "INSERT INTO sessions VALUES (?,?,?,?)",
                (
                    hashlib.sha256(token.encode()).hexdigest(),
                    row["user_id"],
                    row["credential_version"],
                    now + SESSION_SECONDS,
                ),
            )
        return token

    def actor_for(self, token: str | None) -> str | None:
        if not token or len(token) > 128:
            return None
        with self.store.transaction() as connection:
            row = connection.execute(
                "SELECT s.user_id FROM sessions s JOIN users u ON s.user_id=u.user_id "
                "WHERE s.token_hash=? AND s.expires_at>? AND u.enabled=1 "
                "AND s.credential_version=u.credential_version",
                (hashlib.sha256(token.encode()).hexdigest(), time.time()),
            ).fetchone()
            return row["user_id"] if row else None

    def logout(self, token: str | None) -> None:
        if token and len(token) <= 128:
            with self.store.transaction() as connection:
                connection.execute(
                    "DELETE FROM sessions WHERE token_hash=?",
                    (hashlib.sha256(token.encode()).hexdigest(),),
                )

    def allow_model_request(self, actor_user_id: str | None = None) -> bool:
        if not actor_user_id:
            return False
        now = time.time()
        bucket = "model:" + actor_user_id
        with self.store.transaction() as connection:
            connection.execute("DELETE FROM rate_events WHERE at<?", (now - 60,))
            if (
                connection.execute(
                    "SELECT COUNT(*) FROM rate_events WHERE bucket=?", (bucket,)
                ).fetchone()[0]
                >= 10
            ):
                return False
            if connection.execute("SELECT COUNT(*) FROM rate_events").fetchone()[0] >= 5120:
                return False
            connection.execute("INSERT INTO rate_events VALUES (?,?)", (bucket, now))
        return True
