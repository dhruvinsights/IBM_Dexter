"""Filesystem location for local dev persistence (KB, reviews, runtime overrides)."""

from __future__ import annotations

from pathlib import Path

_BACKEND_ROOT = Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """Directory for SQLite/JSON state (gitignored by default)."""
    path = _BACKEND_ROOT / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path
