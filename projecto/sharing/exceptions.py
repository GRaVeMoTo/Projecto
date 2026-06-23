"""Sharing-specific exceptions."""

from projecto.exceptions import ConflictError, NotFoundError


class InviteeNotFoundError(NotFoundError):
    """Raised when the invited login does not match any user."""

    message = "The user to invite does not exist."


class AlreadyMemberError(ConflictError):
    """Raised when the invited user is already a project member."""

    message = "User is already a member of this project."
