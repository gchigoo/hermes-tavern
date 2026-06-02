"""Import helpers for Hermes Tavern."""

from __future__ import annotations

from pathlib import Path

MAX_LOCAL_IMPORT_BYTES = 10 * 1024 * 1024


def _local_import_size_limit_label(limit_bytes: int = MAX_LOCAL_IMPORT_BYTES) -> str:
    if limit_bytes % (1024 * 1024) == 0:
        return f"{limit_bytes // (1024 * 1024)} MB"
    return f"{limit_bytes} bytes"


def assert_local_import_size(
    path: Path,
    *,
    label: str,
    limit_bytes: int = MAX_LOCAL_IMPORT_BYTES,
    error_type: type[Exception] = ValueError,
) -> None:
    """Raise a user-safe bounded-size error before reading the full file."""
    if path.stat().st_size > limit_bytes:
        raise error_type(
            f"{label} is too large to import. "
            f"Maximum supported size is {_local_import_size_limit_label(limit_bytes)}."
        )
