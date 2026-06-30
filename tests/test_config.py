"""Tests for application configuration."""

from projecto.config import Settings, get_settings


def test_settings_defaults() -> None:
    """Settings expose sensible defaults."""
    settings = Settings()
    assert settings.app_port == 8000


def test_get_settings_is_cached() -> None:
    """get_settings returns the same cached instance."""
    assert get_settings() is get_settings()
