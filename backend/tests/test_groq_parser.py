"""Groq SDK transport, boundary validation and production dependency tests; no live calls."""

import asyncio
import json
from copy import deepcopy
from typing import Any

import httpx2
import pytest
from fastapi.testclient import TestClient
from openai import AsyncOpenAI
from test_intent_parser import CASES, GOLD

from app.api.checkout import get_checkout_actor
from app.main import app
from app.schemas.intent_parser import LLMIntentExtraction
from app.services.intent_parser import (
    GroqIntentParser,
    IntentClarificationRequired,
    IntentParserUnavailable,
    InvalidParserOutput,
)


@pytest.fixture(autouse=True)
def authenticate_mock_groq_tests():
    app.dependency_overrides[get_checkout_actor] = lambda: "groq-test"
    yield
    app.dependency_overrides.pop(get_checkout_actor, None)


def completion(payload: Any, *, finish: str = "stop", refusal: str | None = None) -> dict:
    return {
        "id": "chatcmpl-test",
        "object": "chat.completion",
        "created": 1,
        "model": "test-model",
        "choices": [
            {
                "index": 0,
                "finish_reason": finish,
                "message": {
                    "role": "assistant",
                    "content": json.dumps(payload),
                    "refusal": refusal,
                },
            }
        ],
    }


async def parse_mock(query: str, response: dict) -> Any:
    def handler(request: httpx2.Request) -> httpx2.Response:
        assert str(request.url) == "https://api.groq.com/openai/v1/chat/completions"
        body = json.loads(request.content)
        assert body["response_format"]["json_schema"] == {
            "name": "purchase_intent_extraction",
            "strict": True,
            "schema": LLMIntentExtraction.model_json_schema(),
        }
        assert "tools" not in body
        assert body["messages"][1] == {"role": "user", "content": query}
        return httpx2.Response(200, json=response)

    async with AsyncOpenAI(
        api_key="test-only",
        base_url="https://api.groq.com/openai/v1",
        max_retries=0,
        http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
    ) as client:
        return await GroqIntentParser(client, "test-model").parse(query)


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_gold_cases(case: dict) -> None:
    if case["expected"] is not None:
        assert (
            asyncio.run(parse_mock(case["query"], completion(case["extraction"]))).model_dump()
            == case["expected"]
        )
    else:
        with pytest.raises(IntentClarificationRequired):
            asyncio.run(parse_mock(case["query"], completion(case["extraction"])))


@pytest.mark.parametrize(
    "kind",
    ["extra", "source", "roles", "truncated", "refused", "json", "empty", "choices", "tools"],
)
def test_invalid_output_fails_closed(kind: str) -> None:
    payload = deepcopy(GOLD["extraction"])
    if kind == "extra":
        payload["capture"] = True
    if kind == "source":
        payload["budget"]["quote"] = "invented budget USD 1"
    if kind == "roles":
        payload["budget"], payload["approval_threshold"] = (
            payload["approval_threshold"],
            payload["budget"],
        )
    response = completion(payload)
    choice = response["choices"][0]
    if kind == "truncated":
        choice["finish_reason"] = "length"
    if kind == "refused":
        choice["message"]["refusal"] = "private refusal"
    if kind in {"json", "empty"}:
        choice["message"]["content"] = "{broken" if kind == "json" else None
    if kind == "choices":
        response["choices"] = []
    if kind == "tools":
        choice["message"]["tool_calls"] = [
            {"id": "x", "type": "function", "function": {"name": "pay", "arguments": "{}"}}
        ]
    with pytest.raises(InvalidParserOutput):
        asyncio.run(parse_mock(GOLD["query"], response))


@pytest.mark.parametrize("failure", [400, 401, 429, 500, "timeout"])
def test_errors_safe_without_retry(failure: int | str) -> None:
    calls = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        if failure == "timeout":
            raise httpx2.ReadTimeout("private-detail", request=request)
        return httpx2.Response(failure, json={"error": {"message": "private-detail"}})

    async def run() -> None:
        async with AsyncOpenAI(
            api_key="test-only",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler)),
        ) as client:
            with pytest.raises(IntentParserUnavailable) as caught:
                await GroqIntentParser(client, "test-model").parse(GOLD["query"])
            assert "private-detail" not in str(caught.value)

    asyncio.run(run())
    assert len(calls) == 1


@pytest.mark.parametrize(
    "provider,missing",
    [("groq", "GROQ_API_KEY"), ("groq", "GROQ_MODEL"), ("unsupported-secret", None), ("", None)],
)
def test_unavailable_configuration(
    monkeypatch: pytest.MonkeyPatch, provider: str, missing: str | None
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", provider)
    monkeypatch.setenv("GROQ_API_KEY", "test-only")
    monkeypatch.setenv("GROQ_MODEL", "test-model")
    if missing:
        monkeypatch.setenv(missing, "   ")
    with TestClient(app) as client:
        response = client.post("/v1/agent/parse", json={"query": GOLD["query"]})
        assert response.status_code == 503
        assert "test-only" not in response.text and "unsupported-secret" not in response.text
        assert client.get("/health").status_code == 200


def test_groq_production_wiring(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("GROQ_API_KEY", "test-only")
    monkeypatch.setenv("GROQ_MODEL", "test-model")
    calls = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        assert request.url.host == "api.groq.com"
        assert request.headers["authorization"] == "Bearer test-only"
        assert "test-only" not in request.content.decode()
        return httpx2.Response(200, json=completion(GOLD["extraction"]))

    def factory(**kwargs: Any) -> AsyncOpenAI:
        assert kwargs["max_retries"] == 0 and kwargs["timeout"] == 20.0
        return AsyncOpenAI(
            **kwargs, http_client=httpx2.AsyncClient(transport=httpx2.MockTransport(handler))
        )

    monkeypatch.setattr("app.api.agent.AsyncOpenAI", factory)
    with TestClient(app) as client:
        response = client.post("/v1/agent/parse", json={"query": GOLD["query"]})
        assert response.status_code == 200
        assert response.json() == GOLD["expected"]
        assert "test-only" not in response.text
    assert len(calls) == 1


@pytest.mark.parametrize("query", ["", "   ", "x" * 4001])
def test_invalid_query_rejected_before_http(query: str) -> None:
    with pytest.raises(IntentClarificationRequired):
        asyncio.run(parse_mock(query, completion(GOLD["extraction"])))
