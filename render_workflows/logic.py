"""Use existing deterministic verification with bounded, typed input and canonical offers."""

import json

from app.schemas import PurchaseIntent
from app.schemas.catalog import CatalogSearchRequest
from app.services.catalog import CatalogService
from app.services.verifier import verify_offer


def verify_catalog(intent_data: dict) -> dict:
    """Return advisory evidence only: no policy decision, consent, account or payment access."""
    if len(json.dumps(intent_data).encode()) > 16384:
        raise ValueError("Workflow input too large")
    intent = PurchaseIntent.model_validate(intent_data)
    offers = (
        CatalogService()
        .search(CatalogSearchRequest(currency=intent.currency, limit=8))
        .offers
    )
    return {
        "synthetic": True,
        "advisory_only": True,
        "notice": "Synthetic catalog verification; no spending authorization or booking.",
        "offers": [
            {
                "offer_id": offer.offer_id,
                "verification": verify_offer(intent, offer).model_dump(mode="json"),
            }
            for offer in offers
        ],
    }
