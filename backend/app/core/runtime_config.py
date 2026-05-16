"""Runtime-mutable overrides for sensitive credentials.

Lets the UI update tokens at runtime without restarting the backend or editing
.env. Overrides are kept in-process only (not persisted) which is intentional
for the demo / local-dev experience.
"""

from __future__ import annotations

import threading
from typing import Dict, Optional

from app.core.config import get_settings

_settings = get_settings()


class RuntimeConfig:
    """Thread-safe holder for runtime credential overrides."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._overrides: Dict[str, Optional[str]] = {}

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with self._lock:
            if key in self._overrides:
                return self._overrides[key]
        return default

    def set(self, key: str, value: Optional[str]) -> None:
        with self._lock:
            if value is None or value == "":
                self._overrides.pop(key, None)
            else:
                self._overrides[key] = value

    def has(self, key: str) -> bool:
        with self._lock:
            return key in self._overrides

    def snapshot(self) -> Dict[str, str]:
        """Return masked view of currently-set runtime overrides (for the UI)."""
        with self._lock:
            return {key: _mask(value) for key, value in self._overrides.items() if value}

    # ------------------------------------------------------------------ #
    # Convenience accessors that prefer runtime overrides over .env values.
    # ------------------------------------------------------------------ #

    def github_token(self) -> str:
        return self.get("github_token", _settings.github_token or "") or ""

    def gitlab_token(self) -> str:
        return self.get("gitlab_token", _settings.gitlab_token or "") or ""


def _mask(value: Optional[str]) -> str:
    if not value:
        return ""
    if len(value) <= 8:
        return "•" * len(value)
    return f"{value[:4]}…{value[-4:]}"


_runtime_config: Optional[RuntimeConfig] = None


def get_runtime_config() -> RuntimeConfig:
    """Return the singleton runtime config."""
    global _runtime_config
    if _runtime_config is None:
        _runtime_config = RuntimeConfig()
    return _runtime_config


# Made with Bob
