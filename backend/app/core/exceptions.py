from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str, *, code: str | None = None, details: dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.details = details or {}


class NotFound(AppError):
    status_code, code = 404, "NOT_FOUND"


class Forbidden(AppError):
    status_code, code = 403, "FORBIDDEN"


class Unauthorized(AppError):
    status_code, code = 401, "UNAUTHORIZED"


class Conflict(AppError):
    """Business-rule violations: CAPACITY_EXCEEDED, SHIFT_EXCEEDED, VEHICLE_RESTRICTED, RUN_LOCKED, INVALID_TRANSITION."""
    status_code, code = 409, "CONFLICT"


async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}},
    )
