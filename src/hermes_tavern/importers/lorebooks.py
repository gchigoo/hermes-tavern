"""SillyTavern World Info / lorebook import helpers for Hermes Tavern."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid5, NAMESPACE_URL

from hermes_tavern.importers import assert_local_import_size
from hermes_tavern.importers.presets import coerce_legacy_enabled


@dataclass(frozen=True)
class ImportedLorebookEntry:
    id: str
    title: str
    content: str
    keys: tuple[str, ...] = field(default_factory=tuple)
    secondary_keys: tuple[str, ...] = field(default_factory=tuple)
    enabled: bool = True
    constant: bool = False
    regex: bool = False
    position: str = "before_char"
    insertion_order: int = 0
    priority: int = 0
    probability: float = 1.0
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ImportedLorebook:
    name: str
    source: str
    raw: dict[str, Any]
    entries: tuple[ImportedLorebookEntry, ...]
    id: str = ""


def import_lorebook_file(path: str | Path) -> ImportedLorebook:
    lore_path = Path(path)
    assert_local_import_size(
        lore_path,
        label="Lorebook file",
    )
    data = json.loads(lore_path.read_text(encoding="utf-8-sig"))
    return import_st_lorebook_json(data, default_name=lore_path.stem, source=str(lore_path))


def import_st_lorebook_json(
    data: dict[str, Any] | list[Any],
    *,
    default_name: str = "lorebook",
    source: str = "json",
) -> ImportedLorebook:
    entries_data = _extract_entries(data)
    name = default_name
    if isinstance(data, dict):
        name = str(data.get("name") or data.get("world_info_name") or default_name)
    entries = tuple(
        entry for idx, raw in enumerate(entries_data)
        if (entry := _entry_from_raw(raw, idx, source=source)) is not None
    )
    raw = _safe_raw(data)
    if not isinstance(raw, dict):
        raw = {"entries": raw}
    return ImportedLorebook(name=name, source=source, raw=raw, entries=entries)


def import_embedded_lorebook_from_card(card: Any) -> ImportedLorebook | None:
    """Extract a SillyTavern character_book/world_info embedded in a character card.

    SillyTavern v3 character cards commonly store a nested ``data.character_book``
    object. Some legacy/community exports use top-level ``character_book`` or
    ``world_info``. Return ``None`` when the card has no importable embedded book.
    """
    raw = getattr(card, "raw", None)
    if not isinstance(raw, dict):
        return None

    book, source_key = _find_embedded_book(raw)
    if book is None:
        return None

    card_name = str(getattr(card, "name", "") or "character").strip() or "character"
    source = f"embedded:{getattr(card, 'id', card_name)}:{source_key}"
    lorebook = import_st_lorebook_json(
        book,
        default_name=f"{card_name} embedded lorebook",
        source=source,
    )
    if not lorebook.entries:
        return None
    stable = json.dumps(_safe_raw(book), ensure_ascii=False, sort_keys=True, default=str)
    lorebook_id = str(uuid5(NAMESPACE_URL, f"hermes-tavern:{getattr(card, 'id', card_name)}:{source_key}:{stable}"))
    return ImportedLorebook(
        id=lorebook_id,
        name=lorebook.name,
        source=lorebook.source,
        raw=lorebook.raw,
        entries=lorebook.entries,
    )


def _find_embedded_book(raw: dict[str, Any]) -> tuple[dict[str, Any] | list[Any] | None, str]:
    candidates: list[tuple[str, Any]] = []
    data = raw.get("data")
    if isinstance(data, dict):
        candidates.extend([
            ("data.character_book", data.get("character_book")),
            ("data.world_info", data.get("world_info")),
        ])
    candidates.extend([
        ("character_book", raw.get("character_book")),
        ("world_info", raw.get("world_info")),
    ])
    for key, value in candidates:
        if isinstance(value, (dict, list)) and any(
            _entry_from_raw(entry, idx, source=key) is not None
            for idx, entry in enumerate(_extract_entries(value))
        ):
            return value, key
    return None, ""


def _extract_entries(data: dict[str, Any] | list[Any]) -> list[dict[str, Any]]:
    if isinstance(data, list):
        return [item for item in data if isinstance(item, dict)]
    if not isinstance(data, dict):
        return []
    entries = data.get("entries") or data.get("world_info") or data.get("items")
    if isinstance(entries, dict):
        result = []
        for uid, entry in entries.items():
            if isinstance(entry, dict):
                merged = {"uid": uid, **entry}
                result.append(merged)
        return result
    if isinstance(entries, list):
        return [item for item in entries if isinstance(item, dict)]
    return []


def _entry_enabled(raw: dict[str, Any]) -> bool:
    """Normalize native and legacy lorebook enabled flags.

    A recognized ``enabled`` value is authoritative.  Otherwise the historical
    negative aliases keep their default-enabled behavior, except recognized
    textual/numeric false values no longer disable entries.  Unrecognized
    nonempty negative values retain the conservative legacy fallback.
    """
    explicit_enabled = coerce_legacy_enabled(raw.get("enabled"))
    if explicit_enabled is not None:
        return explicit_enabled
    for field in ("disable", "disabled"):
        value = raw.get(field)
        disabled = coerce_legacy_enabled(value)
        if disabled is True or (disabled is None and bool(value)):
            return False
    return True


def _legacy_or(raw: dict[str, Any], *fields: str) -> bool:
    """OR legacy aliases, normalizing recognized serialized boolean values."""
    for field in fields:
        value = raw.get(field)
        normalized = coerce_legacy_enabled(value)
        if normalized is True or (normalized is None and bool(value)):
            return True
    return False


def _entry_from_raw(raw: dict[str, Any], idx: int, *, source: str) -> ImportedLorebookEntry | None:
    content = None
    for field in ("content", "entry", "text", "value"):
        candidate = raw.get(field)
        if isinstance(candidate, str) and candidate.strip():
            content = candidate
            break
    if content is None:
        return None
    raw_id = _entry_id_from_raw(raw, idx)
    title = str(raw.get("comment") or raw.get("title") or raw.get("name") or raw_id)
    entry_id = str(raw_id)
    if not entry_id:
        entry_id = str(uuid5(NAMESPACE_URL, f"{source}:{idx}:{title}:{content[:80]}"))
    enabled = _entry_enabled(raw)
    raw_order = raw.get("displayIndex")
    for field in ("insertion_order", "order"):
        value = raw.get(field)
        if value or (type(value) is int and value == 0):
            raw_order = value
            break
    return ImportedLorebookEntry(
        id=entry_id,
        title=title,
        content=content,
        keys=_tuple_strings(raw.get("keys") or raw.get("key") or raw.get("primary_keys")),
        secondary_keys=_tuple_strings(raw.get("secondary_keys") or raw.get("keysecondary") or raw.get("filters")),
        enabled=enabled,
        constant=_legacy_or(raw, "constant", "always_active"),
        regex=_legacy_or(raw, "regex", "use_regex"),
        position=str(raw.get("position") or "before_char"),
        insertion_order=_int(raw_order, idx),
        priority=_int(raw.get("priority"), 0),
        probability=_probability(raw.get("probability") if "probability" in raw else raw.get("chance")),
        raw=_safe_raw(raw),
    )


def _entry_id_from_raw(raw: dict[str, Any], idx: int) -> Any:
    """Select an entry id: uid, then id, then key, then ``entry_{idx}``.

    Integer 0 is a valid SillyTavern uid. Boolean False and other falsy
    values are skipped so they fall through to the next candidate.
    """
    for field in ("uid", "id", "key"):
        value = raw.get(field)
        if _is_usable_entry_id(value):
            return value
    return f"entry_{idx}"


def _is_usable_entry_id(value: Any) -> bool:
    """Return whether ``value`` can be kept as an entry id."""
    # bool 是 int 的子类，False == 0；必须先排除 False，再保留整数 0。
    if isinstance(value, bool):
        return value
    if isinstance(value, int):
        return True
    return bool(value)


def _tuple_strings(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,) if value.strip() else ()
    if isinstance(value, list):
        return tuple(str(item) for item in value if str(item).strip())
    return (str(value),) if str(value).strip() else ()


def _int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    # SQLite INTEGER columns store signed 64-bit values.
    return parsed if -(2**63) <= parsed <= 2**63 - 1 else default


def _probability(value: Any) -> float:
    if value is None:
        return 1.0
    try:
        p = float(value)
    except (TypeError, ValueError, OverflowError):
        return 1.0
    if not math.isfinite(p):
        return 1.0
    if p > 1:
        p = p / 100.0
    return max(0.0, min(1.0, p))


def _safe_raw(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _safe_raw(v) for k, v in value.items() if str(k).lower() not in {"api_key", "access_token", "secret", "token", "password"}}
    if isinstance(value, list):
        return [_safe_raw(item) for item in value]
    return value
