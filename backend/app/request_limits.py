"""Bound request bytes/time and in-flight requests before FastAPI parses JSON."""

import asyncio
import time
from weakref import WeakKeyDictionary

from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class RequestLimits:
    def __init__(
        self, app: ASGIApp, *, max_bytes: int = 65536, timeout: float = 10, max_inflight: int = 64
    ) -> None:
        self.app, self.max_bytes, self.timeout = app, max_bytes, timeout
        self.max_inflight = max_inflight
        self._limits = WeakKeyDictionary()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        limiter = self._limits.setdefault(
            asyncio.get_running_loop(), asyncio.Semaphore(self.max_inflight)
        )
        try:
            await asyncio.wait_for(limiter.acquire(), timeout=0.05)
        except TimeoutError:
            await JSONResponse({"detail": "Server busy; retry later"}, status_code=429)(
                scope, receive, send
            )
            return
        try:
            headers = dict(scope.get("headers", []))
            try:
                length = int(headers.get(b"content-length", b"0"))
                if length < 0:
                    raise ValueError
            except ValueError:
                await JSONResponse({"detail": "Invalid request length"}, status_code=400)(
                    scope, receive, send
                )
                return
            if length > self.max_bytes:
                await JSONResponse({"detail": "Request too large"}, status_code=413)(
                    scope, receive, send
                )
                return
            body = bytearray()
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    message = await asyncio.wait_for(
                        receive(), max(0.001, deadline - time.monotonic())
                    )
                except TimeoutError:
                    await JSONResponse({"detail": "Request body timed out"}, status_code=408)(
                        scope, receive, send
                    )
                    return
                if message["type"] == "http.disconnect":
                    return
                chunk = message.get("body", b"")
                if len(body) + len(chunk) > self.max_bytes:
                    await JSONResponse({"detail": "Request too large"}, status_code=413)(
                        scope, receive, send
                    )
                    return
                body.extend(chunk)
                if not message.get("more_body", False):
                    break
            delivered = False

            async def bounded_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            await self.app(scope, bounded_receive, send)
        finally:
            limiter.release()
