"""SillyTavern preset import helpers for Hermes Tavern.

Supports JSON presets and raw text prompts.  Risky modules are preserved as
imported assets but disabled by default; import does not imply active prompt use.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from hermes_tavern.importers import assert_local_import_size
from hermes_tavern.preset_safety import PresetRiskLevel, classify_preset_text


@dataclass(frozen=True)
class ImportedPresetModule:
    name: str
    role: str
    content: str
    enabled: bool
    position: str = "before_char"
    insertion_order: int = 0
    risk_level: str = PresetRiskLevel.SAFE.value
    risk_reasons: tuple[str, ...] = field(default_factory=tuple)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ImportedPreset:
    name: str
    source: str
    raw: dict[str, Any]
    modules: tuple[ImportedPresetModule, ...]


def import_preset_file(path: str | Path) -> ImportedPreset:
    preset_path = Path(path)
    assert_local_import_size(
        preset_path,
        label="Preset file",
    )
    text = preset_path.read_text(encoding="utf-8")
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return import_raw_preset_text(text, name=preset_path.stem, source=str(preset_path))
    if not isinstance(parsed, dict):
        return import_raw_preset_text(text, name=preset_path.stem, source=str(preset_path))
    return import_st_preset_json(parsed, default_name=preset_path.stem, source=str(preset_path))


def import_raw_preset_text(text: str, *, name: str = "raw-preset", source: str = "raw") -> ImportedPreset:
    report = classify_preset_text(text)
    module = ImportedPresetModule(
        name="raw_text",
        role="system",
        content=text,
        enabled=report.enable_by_default,
        position="before_char",
        insertion_order=0,
        risk_level=report.level.value,
        risk_reasons=report.reasons,
        raw={"source": source, "import_kind": "raw_text"},
    )
    return ImportedPreset(
        name=name,
        source=source,
        raw={"source": source, "format": "raw_text"},
        modules=(module,),
    )


def import_st_preset_json(data: dict[str, Any], *, default_name: str = "st-preset", source: str = "json") -> ImportedPreset:
    name = str(data.get("name") or data.get("preset_name") or default_name)
    prompt_entries = _extract_prompt_entries(data)
    modules: list[ImportedPresetModule] = []
    for idx, entry in enumerate(prompt_entries):
        module = _module_from_entry(entry, idx)
        if module is not None:
            modules.append(module)
    if not modules:
        text = json.dumps(data, ensure_ascii=False, sort_keys=True)
        return import_raw_preset_text(text, name=name, source=source)
    return ImportedPreset(name=name, source=source, raw=_safe_raw(data), modules=tuple(modules))


def _extract_prompt_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("prompts", "prompt_order", "modules"):
        value = data.get(key)
        if isinstance(value, list):
            return [entry for entry in value if isinstance(entry, dict)]
    return []


def _module_from_entry(entry: dict[str, Any], idx: int) -> ImportedPresetModule | None:
    content = entry.get("content") or entry.get("prompt") or entry.get("text") or entry.get("value")
    if not isinstance(content, str) or not content.strip():
        return None
    name = str(entry.get("name") or entry.get("identifier") or entry.get("id") or f"module_{idx}")
    role = str(entry.get("role") or "system")
    position = str(entry.get("position") or "before_char")
    report = classify_preset_text(content)
    explicit_enabled = entry.get("enabled")
    if isinstance(explicit_enabled, bool):
        enabled = explicit_enabled and report.enable_by_default
    else:
        enabled = report.enable_by_default
    return ImportedPresetModule(
        name=name,
        role=role,
        content=content,
        enabled=enabled,
        position=position,
        insertion_order=int(entry.get("insertion_order") or entry.get("order") or idx),
        risk_level=report.level.value,
        risk_reasons=report.reasons,
        raw={"st_entry": _safe_raw(entry)},
    )


def _safe_raw(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _safe_raw(v) for k, v in value.items() if str(k).lower() not in {"api_key", "access_token", "secret", "token", "password"}}
    if isinstance(value, list):
        return [_safe_raw(item) for item in value]
    return value
