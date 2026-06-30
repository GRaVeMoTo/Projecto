import logging
import sys

from projecto.config import settings


def configure_logging() -> None:
    """Configure root logging for the application."""
    level = logging.DEBUG if settings.app_env == "development" else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        stream=sys.stdout,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a named logger instance."""
    return logging.getLogger(name)
