"""Persist pull request / review list API state across backend restarts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

from app.core.data_dir import get_data_dir

FILENAME = "pull_requests_app_state.json"
REPOS_FILENAME = "repositories_app_state.json"


class _DateTimeEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)


def load_pull_request_state() -> Tuple[Dict[int, Any], List[dict]]:
    path = get_data_dir() / FILENAME
    if not path.exists():
        return {}, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}, []
    pr_raw = data.get("pull_requests") or {}
    pr_out: Dict[int, Any] = {}
    for k, v in pr_raw.items():
        ent = dict(v)
        for key in ("created_at", "updated_at"):
            if key in ent and isinstance(ent[key], str):
                ent[key] = datetime.fromisoformat(ent[key].replace("Z", "+00:00"))
        pr_out[int(k)] = ent
    reviews = list(data.get("reviews") or [])
    return pr_out, reviews


def save_pull_request_state(pull_requests: Dict[int, Any], reviews: List[dict]) -> None:
    path = get_data_dir() / FILENAME
    pr_json: Dict[str, Any] = {}
    for k, v in pull_requests.items():
        ent = dict(v)
        for key in ("created_at", "updated_at"):
            if key in ent and isinstance(ent[key], datetime):
                ent[key] = ent[key].isoformat()
        pr_json[str(k)] = ent
    path.write_text(
        json.dumps({"pull_requests": pr_json, "reviews": reviews}, cls=_DateTimeEncoder, indent=2),
        encoding="utf-8",
    )


def load_repository_state() -> Tuple[Dict[int, Any], int]:
    path = get_data_dir() / REPOS_FILENAME
    if not path.exists():
        return {}, 1
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}, 1
    repos_raw = data.get("repositories") or {}
    out: Dict[int, Any] = {}
    for k, v in repos_raw.items():
        out[int(k)] = dict(v)
    next_id = int(data.get("next_id") or (max(out.keys(), default=0) + 1))
    return out, next_id


def save_repository_state(repositories: Dict[int, Any], next_id: int) -> None:
    path = get_data_dir() / REPOS_FILENAME
    payload = {"repositories": {str(k): v for k, v in repositories.items()}, "next_id": next_id}
    path.write_text(json.dumps(payload, cls=_DateTimeEncoder, indent=2), encoding="utf-8")
