"""Opt-in single-buyer demo authentication; no identity supplied by browser JSON."""

import hashlib
import hmac
import secrets
from collections import defaultdict, deque
from threading import RLock
from time import monotonic

COOKIE_NAME = "ryuk_session"
SESSION_SECONDS = 1200


class DemoSessions:
    def __init__(
        self, password: str, *, origin: str, secure: bool = True, actor: str = "ryuk-demo-buyer"
    ) -> None:
        if len(password) < 16:
            raise ValueError("Demo password must have at least 16 characters")
        self.origin, self.secure, self.actor = origin, secure, actor
        self._salt = secrets.token_bytes(32)
        self._password = self._hash(password)
        self._sessions: dict[bytes, float] = {}
        self._attempts: dict[str, deque] = defaultdict(deque)
        self._lock = RLock()

    def _hash(self, value: str) -> bytes:
        return hashlib.scrypt(value.encode(), salt=self._salt, n=16384, r=8, p=1)

    def login(self, password: str, client: str) -> str | None:
        with self._lock:
            now = monotonic()
            attempts = self._attempts[client]
            while attempts and attempts[0] < now - 60:
                attempts.popleft()
            if len(attempts) >= 5:
                return None
            attempts.append(now)
            if not hmac.compare_digest(self._hash(password), self._password):
                return None
            self._sessions = {k: expires for k, expires in self._sessions.items() if expires > now}
            token = secrets.token_urlsafe(32)
            self._sessions[hashlib.sha256(token.encode()).digest()] = now + SESSION_SECONDS
            return token

    def actor_for(self, token: str | None) -> str | None:
        if not token or len(token) > 128:
            return None
        with self._lock:
            key = hashlib.sha256(token.encode()).digest()
            if self._sessions.get(key, 0) <= monotonic():
                self._sessions.pop(key, None)
                return None
            return self.actor

    def logout(self, token: str | None) -> None:
        with self._lock:
            if token:
                self._sessions.pop(hashlib.sha256(token.encode()).digest(), None)
