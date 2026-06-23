"""Document-specific exceptions."""

from projecto.exceptions import NotFoundError


class DocumentNotFoundError(NotFoundError):
    """Raised when a document does not exist or is not accessible."""

    message = "Document not found."
