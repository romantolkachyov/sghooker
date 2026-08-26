"""Application settings loaded from environment variables."""

import os

_TRUTHY = frozenset({"1", "true", "yes", "on"})


def env_flag(name: str, *, default: bool = False) -> bool:
    """Return True when the environment variable is set to a truthy value."""
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in _TRUTHY


DEBUG_WEBHOOK_BODY = env_flag("SGHOOKER_DEBUG_WEBHOOK_BODY")
