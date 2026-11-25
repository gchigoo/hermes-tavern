"""User persona import helpers for Hermes Tavern."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from uuid import NAMESPACE_URL, uuid5

from hermes_tavern.importers import assert_local_import_size


@dataclass(frozen=True)
class ImportedPersona:
    id: str
    name: str
    content: str
    source_path: str
    raw_json: dict[str, Any] = field(default_factory=dict)


def import_persona_file(path: str | Path) -> ImportedPersona:
    persona_path = Path(path)
    assert_local_import_size(
        persona_path,
        label="Persona file",
    )
    # utf-8-sig 去掉 BOM 后再解析 JSON；解析失败仍走原文回退。
    text = persona_path.read_text(encoding="utf-8-sig")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return import_raw_persona_text(
            text,
            name=persona_path.stem,
            source_path=str(persona_path),
        )
    if not isinstance(parsed, dict):
        return import_raw_persona_text(
            text,
            name=persona_path.stem,
            source_path=str(persona_path),
        )
    return import_persona_json(parsed, default_name=persona_path.stem, source_path=str(persona_path))


def import_raw_persona_text(
    text: str,
    *,
    name: str = "persona",
    source_path: str = "raw",
) -> ImportedPersona:
    content = text.strip()
    raw = {"format": "raw_text", "source_path": source_path}
    return _persona(name=name, content=content, source_path=source_path, raw_json=raw)


def import_persona_json(
    data: dict[str, Any],
    *,
    default_name: str = "persona",
    source_path: str = "json",
) -> ImportedPersona:
    name = persona_json_name(data) or default_name
    return _persona(
        name=name or default_name,
        content=persona_json_content(data),
        source_path=source_path,
        raw_json=_safe_raw(data),
    )


def persona_json_content(data: dict[str, Any]) -> str:
    for key in ("persona", "description", "prompt", "content", "text", "profile"):
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def persona_json_name(data: dict[str, Any]) -> str | None:
    for key in ("name", "persona_name", "user_name"):
        value = data.get(key)
        if isinstance(value, (bool, dict, list)) or not value:
            continue
        name = str(value).strip()
        if name:
            return name
    return None


def _persona(
    *,
    name: str,
    content: str,
    source_path: str,
    raw_json: dict[str, Any],
) -> ImportedPersona:
    clean_name = " ".join(str(name or "persona").split()) or "persona"
    clean_content = str(content or "").strip()
    stable = json.dumps(
        {"name": clean_name, "content": clean_content, "source_path": source_path},
        ensure_ascii=False,
        sort_keys=True,
    )
    persona_id = str(uuid5(NAMESPACE_URL, f"hermes-tavern:persona:{stable}"))
    return ImportedPersona(
        id=persona_id,
        name=clean_name,
        content=clean_content,
        source_path=source_path,
        raw_json=raw_json,
    )


_PERSONA_SECRET_KEYS = {
    "api_key", "apikey", "access_token", "accesstoken", "secret", "token", "password",
}


def _safe_raw(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(k): _safe_raw(v)
            for k, v in value.items()
            if str(k).lower() not in _PERSONA_SECRET_KEYS
        }
    if isinstance(value, list):
        return [_safe_raw(item) for item in value]
    return value
