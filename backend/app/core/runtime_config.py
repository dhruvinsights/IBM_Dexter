"""Runtime-mutable overrides for sensitive credentials.

Lets the UI update tokens at runtime without restarting the backend or editing
.env. Overrides persist under `backend/data/runtime_overrides.json` for local
development (do not commit; file is gitignored).
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Dict, Optional

from app.core.config import get_settings
from app.core.data_dir import get_data_dir

_settings = get_settings()
_STATE_FILE = "runtime_overrides.json"


def _state_path() -> Path:
    return get_data_dir() / _STATE_FILE


class RuntimeConfig:
    """Thread-safe holder for runtime credential overrides."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._overrides: Dict[str, Optional[str]] = {}
        self._load_disk()

    def _load_disk(self) -> None:
        path = _state_path()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            raw = data.get("overrides") or {}
            with self._lock:
                for k, v in raw.items():
                    if v is not None and str(v).strip() != "":
                        self._overrides[str(k)] = str(v)
        except Exception:
            pass

    def _persist_disk(self) -> None:
        with self._lock:
            snap = {k: v for k, v in self._overrides.items() if v}
        path = _state_path()
        path.write_text(json.dumps({"overrides": snap}, indent=2), encoding="utf-8")

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
        self._persist_disk()

    def has(self, key: str) -> bool:
        with self._lock:
            return key in self._overrides

    def snapshot(self) -> Dict[str, str]:
        """Return masked view of currently-set runtime overrides (for the UI)."""
        with self._lock:
            out: Dict[str, str] = {}
            for key, value in self._overrides.items():
                if not value:
                    continue
                if key in ("ollama_model", "ollama_base_url", "db2_kb_table_prefix", "db2_schema"):
                    out[key] = str(value)
                elif key == "db2_connection_string":
                    out[key] = _mask(value)
                else:
                    out[key] = _mask(value)
            return out

    # ------------------------------------------------------------------ #
    # Convenience accessors that prefer runtime overrides over .env values.
    # ------------------------------------------------------------------ #

    def github_token(self) -> str:
        return self.get("github_token", _settings.github_token or "") or ""

    def gitlab_token(self) -> str:
        return self.get("gitlab_token", _settings.gitlab_token or "") or ""

    def ollama_base_url(self) -> str:
        raw = self.get("ollama_base_url", _settings.ollama_base_url) or ""
        return str(raw).rstrip("/")

    def ollama_model(self) -> str:
        return str(self.get("ollama_model", _settings.ollama_model) or _settings.ollama_model or "")


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
