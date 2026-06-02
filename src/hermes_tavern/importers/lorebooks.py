"""SillyTavern World Info / lorebook import helpers for Hermes Tavern."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import uuid5, NAMESPACE_URL

from hermes_tavern.importers import assert_local_import_size


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
    data = json.loads(lore_path.read_text(encoding="utf-8"))
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
        if isinstance(value, (dict, list)) and _extract_entries(value):
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


def _entry_from_raw(raw: dict[str, Any], idx: int, *, source: str) -> ImportedLorebookEntry | None:
    content = raw.get("content") or raw.get("entry") or raw.get("text") or raw.get("value")
    if not isinstance(content, str) or not content.strip():
        return None
    raw_id = raw.get("uid") or raw.get("id") or raw.get("key") or f"entry_{idx}"
    title = str(raw.get("comment") or raw.get("title") or raw.get("name") or raw_id)
    entry_id = str(raw_id)
    if not entry_id:
        entry_id = str(uuid5(NAMESPACE_URL, f"{source}:{idx}:{title}:{content[:80]}"))
    enabled = not bool(raw.get("disable") or raw.get("disabled"))
    if isinstance(raw.get("enabled"), bool):
        enabled = bool(raw["enabled"])
    return ImportedLorebookEntry(
        id=entry_id,
        title=title,
        content=content,
        keys=_tuple_strings(raw.get("keys") or raw.get("key") or raw.get("primary_keys")),
        secondary_keys=_tuple_strings(raw.get("secondary_keys") or raw.get("keysecondary") or raw.get("filters")),
        enabled=enabled,
        constant=bool(raw.get("constant") or raw.get("always_active")),
        regex=bool(raw.get("regex") or raw.get("use_regex")),
        position=str(raw.get("position") or "before_char"),
        insertion_order=_int(raw.get("insertion_order") or raw.get("order") or raw.get("displayIndex"), idx),
        priority=_int(raw.get("priority"), 0),
        probability=_probability(raw.get("probability") if "probability" in raw else raw.get("chance")),
        raw=_safe_raw(raw),
    )


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
        return int(value)
    except (TypeError, ValueError):
        return default


def _probability(value: Any) -> float:
    if value is None:
        return 1.0
    try:
        p = float(value)
    except (TypeError, ValueError):
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
