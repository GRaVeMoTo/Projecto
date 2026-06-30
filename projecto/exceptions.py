"""Application-wide exception types and FastAPI exception handlers."""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for all application errors.

    Attributes:
        message: Human-readable error message.
        status_code: HTTP status code to return.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    message: str = "An unexpected error occurred."

    def __init__(self, message: str | None = None) -> None:
        if message is not None:
            self.message = message
        super().__init__(self.message)


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    message = "Resource not found."


class ConflictError(AppError):
    """Raised when a resource conflicts with existing state."""

    status_code = status.HTTP_409_CONFLICT
    message = "Resource conflict."


class UnauthorizedError(AppError):
    """Raised when authentication fails or is missing."""

    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Authentication required."


class ForbiddenError(AppError):
    """Raised when an authenticated user lacks permission."""

    status_code = status.HTTP_403_FORBIDDEN
    message = "You do not have permission to perform this action."


async def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Convert an AppError into a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def register_exception_handlers(app: object) -> None:
    """Register all application exception handlers on the FastAPI app."""
    from fastapi import FastAPI

    assert isinstance(app, FastAPI)
    app.add_exception_handler(AppError, app_error_handler)  # type: ignore[arg-type]
