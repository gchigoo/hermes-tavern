"""Low-level utility helpers for the Hermes Tavern SQLite store."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    return dict(row)


_SECRET_FIELD_NAMES = {"apikey", "accesstoken", "secret", "token", "password"}


def _normalized_field_name(key: Any) -> str:
    if not isinstance(key, str):
        return ""
    return "".join(character for character in key.casefold() if character.isalnum())


def assert_no_secret_keys(value: Any, path: str = "raw_json") -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            if _normalized_field_name(key) in _SECRET_FIELD_NAMES:
                raise ValueError(f"model profile must not persist secret field: {path}.{key}")
            assert_no_secret_keys(nested, f"{path}.{key}")
    elif isinstance(value, list):
        for idx, nested in enumerate(value):
            assert_no_secret_keys(nested, f"{path}[{idx}]")
