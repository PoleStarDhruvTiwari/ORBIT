"""
Structured HTTP errors + global exception handlers.

Every API response on the error path is a JSON object with a stable shape:

    {
        "error":   "<stable_code>",     # frontend matches against this
        "message": "<human-readable>",
        "field":   "<optional, for validation/conflict errors>",
        "errors":  [<optional list, for 422 only>]
    }

Backwards compatible: existing endpoints raising
`HTTPException(status_code=..., detail="some_code")` still work — the handler
below wraps them in the same envelope.

Use the typed exception classes (NotFoundError / ConflictError / ForbiddenError /
BadRequestError) for new code so the frontend has one less ambiguity to deal
with.
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.core.logger import logger


# ---------------------------------------------------------------------------
# Typed exceptions
# ---------------------------------------------------------------------------

class APIError(HTTPException):
    """Base class for app-level errors that carry a stable `error_code`."""

    error_code: str = "internal_error"

    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: Optional[str] = None,
        field: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=message)
        if error_code:
            self.error_code = error_code
        self.field = field


class NotFoundError(APIError):
    def __init__(self, resource: str, message: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=message or f"{resource}_not_found",
            error_code=f"{resource}_not_found",
        )


class ConflictError(APIError):
    def __init__(
        self,
        message: str,
        error_code: str = "conflict",
        field: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            message=message,
            error_code=error_code,
            field=field,
        )


class ForbiddenError(APIError):
    def __init__(self, message: str = "forbidden", error_code: str = "forbidden"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code=error_code,
        )


class BadRequestError(APIError):
    def __init__(
        self,
        message: str,
        error_code: str = "bad_request",
        field: Optional[str] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            error_code=error_code,
            field=field,
        )


# ---------------------------------------------------------------------------
# Legacy aliases (kept so existing imports keep working)
# ---------------------------------------------------------------------------

class UserNotRegisteredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN, detail="user_not_registered"
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid_credentials"
        )


# ---------------------------------------------------------------------------
# Handler installer
# ---------------------------------------------------------------------------

def _envelope(error: str, message: str, **extra) -> dict:
    body = {"error": error, "message": message}
    body.update({k: v for k, v in extra.items() if v is not None})
    return body


def install_exception_handlers(app: FastAPI) -> None:
    """Register handlers that funnel every error into the standard envelope."""

    @app.exception_handler(APIError)
    async def _api_error(request: Request, exc: APIError):  # noqa: D401
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(exc.error_code, exc.detail, field=getattr(exc, "field", None)),
        )

    @app.exception_handler(HTTPException)
    async def _http(request: Request, exc: HTTPException):
        # detail is usually a stable token like "task_not_found" — surface it
        # as both `error` and `message` so the frontend has something to match.
        detail = exc.detail if isinstance(exc.detail, str) else "http_error"
        return JSONResponse(
            status_code=exc.status_code,
            content=_envelope(detail, detail),
        )

    @app.exception_handler(RequestValidationError)
    async def _validation(request: Request, exc: RequestValidationError):
        # exc.errors() is JSON-serializable but contains pydantic internals
        # like `ctx` that may include non-stringable values; coerce to str.
        clean = []
        for e in exc.errors():
            clean.append(
                {
                    "loc": [str(x) for x in e.get("loc", [])],
                    "msg": e.get("msg", ""),
                    "type": e.get("type", ""),
                }
            )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_envelope(
                "validation_error", "request validation failed", errors=clean
            ),
        )

    @app.exception_handler(IntegrityError)
    async def _integrity(request: Request, exc: IntegrityError):
        msg = str(getattr(exc, "orig", "") or "constraint_violation").splitlines()[0]
        logger.warning(f"IntegrityError on {request.method} {request.url.path}: {msg}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_envelope("integrity_violation", msg),
        )

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception):
        logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_envelope("internal_error", "internal server error"),
        )
