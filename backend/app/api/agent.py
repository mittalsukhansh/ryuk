"""Intent extraction endpoint; no policy, approval, or payment side effects."""

import os
from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI

from app.schemas import PurchaseIntent
from app.schemas.intent_parser import ParseIntentRequest
from app.services.intent_parser import (
    IntentClarificationRequired,
    IntentParser,
    IntentParserUnavailable,
    InvalidParserOutput,
    OpenAIIntentParser,
)

PROVIDER_TIMEOUT_SECONDS = 20.0
router = APIRouter(prefix="/v1/agent", tags=["intent"])


async def get_intent_parser() -> AsyncIterator[IntentParser]:
    """Create the real parser lazily so health/catalog startup needs no LLM credentials."""
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    model = os.environ.get("OPENAI_MODEL", "").strip()
    if not api_key or not model:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "PARSER_UNAVAILABLE",
                "message": "Configure backend OPENAI_API_KEY and OPENAI_MODEL to enable parsing.",
            },
        )
    async with AsyncOpenAI(
        api_key=api_key,
        timeout=PROVIDER_TIMEOUT_SECONDS,
        max_retries=0,
    ) as client:
        yield OpenAIIntentParser(client, model)


@router.post("/parse", response_model=PurchaseIntent)
async def parse_intent(
    body: ParseIntentRequest,
    parser: Annotated[IntentParser, Depends(get_intent_parser)],
) -> PurchaseIntent:
    """Return a typed proposal; parsed values never change active financial policy."""
    try:
        return await parser.parse(body.query)
    except IntentClarificationRequired as error:
        raise HTTPException(
            status_code=422,
            detail={
                "code": "INTENT_CLARIFICATION_REQUIRED",
                "message": str(error),
            },
        ) from None
    except InvalidParserOutput:
        raise HTTPException(
            status_code=502,
            detail={
                "code": "INVALID_PARSER_OUTPUT",
                "message": "The model returned an invalid extraction.",
            },
        ) from None
    except IntentParserUnavailable:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "PARSER_UNAVAILABLE",
                "message": "The intent model is unavailable. Try again later.",
            },
        ) from None
