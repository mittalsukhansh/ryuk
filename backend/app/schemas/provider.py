"""Provider-event shape is validated before cryptographic verification; shape is not trust."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RefundReviewState(StrEnum):
    REQUESTED = "REQUESTED"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class RefundState(StrEnum):
    DISPATCHED = "DISPATCHED"
    UNKNOWN = "UNKNOWN"
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ProviderEvent(BaseModel):
    # Preserve the original event's extra fields for PayPal verification.
    model_config = ConfigDict(extra="allow", hide_input_in_errors=True)
    id: str = Field(strict=True, pattern=r"^[A-Za-z0-9_-]{1,127}$")
    event_type: str = Field(strict=True, min_length=1, max_length=128)
    resource: dict[str, Any]
