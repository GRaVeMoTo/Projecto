"""Project-specific exceptions."""

from projecto.exceptions import ForbiddenError, NotFoundError


class ProjectNotFoundError(NotFoundError):
    """Raised when a project does not exist or is not accessible."""

    message = "Project not found."


class ProjectAccessDeniedError(ForbiddenError):
    """Raised when a user lacks access to a project."""

    message = "You do not have access to this project."


class ProjectOwnerRequiredError(ForbiddenError):
    """Raised when an action requires project ownership."""

    message = "Only the project owner can perform this action."
