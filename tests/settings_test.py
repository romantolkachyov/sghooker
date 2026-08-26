"""Tests for environment-based settings."""

from unittest.mock import patch

from sghooker import settings


def test_env_flag_false_by_default() -> None:
    """Debug webhook logging is disabled without the env var."""
    with patch.dict("os.environ", {}, clear=True):
        assert settings.env_flag("SGHOOKER_DEBUG_WEBHOOK_BODY") is False


def test_env_flag_truthy_values() -> None:
    """Common truthy env values enable the flag."""
    for value in ("1", "true", "TRUE", " yes ", "on"):
        with patch.dict("os.environ", {"SGHOOKER_DEBUG_WEBHOOK_BODY": value}):
            assert settings.env_flag("SGHOOKER_DEBUG_WEBHOOK_BODY") is True


def test_env_flag_falsy_values() -> None:
    """Non-truthy values keep the flag disabled."""
    with patch.dict("os.environ", {"SGHOOKER_DEBUG_WEBHOOK_BODY": "0"}):
        assert settings.env_flag("SGHOOKER_DEBUG_WEBHOOK_BODY") is False
