"""
Shared response envelopes & query params used by list endpoints.
"""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Standard paginated list envelope.

    The frontend gets `total` so it can render proper paginator UI without
    hitting `HEAD` or relying on `Content-Range`.
    """

    items: List[T]
    total: int = Field(..., ge=0)
    skip: int = Field(..., ge=0)
    limit: int = Field(..., ge=1, le=500)


class ErrorEnvelope(BaseModel):
    """Documentation-only schema for the error response shape."""

    error: str
    message: str
    field: Optional[str] = None
