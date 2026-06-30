"""Auth-specific exceptions."""

from projecto.exceptions import ConflictError, UnauthorizedError


class UserAlreadyExistsError(ConflictError):
    """Raised when registering a login that already exists."""

    message = "A user with this login already exists."


class InvalidCredentialsError(UnauthorizedError):
    """Raised when login credentials are incorrect."""

    message = "Invalid login or password."
