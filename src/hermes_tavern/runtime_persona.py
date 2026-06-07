"""Persona commands for Hermes Tavern runtime."""

from __future__ import annotations

import math
import json
from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.import_policy import resolve_import_path
from hermes_tavern.importers.personas import import_persona_file, import_raw_persona_text
from hermes_tavern.runtime_utils import mobile_preview, parse_pagination
from hermes_tavern.hermes_home import get_hermes_home

_IMPORTABLE_PERSONA_SUFFIXES = {".json", ".txt"}


def _persona_not_found(ref: str) -> str:
    if ref.strip().lower() == "last":
        return "No persona has been imported yet. Import a persona first: /rp persona import <file>"
    return f"Persona not found: {ref}"


def _coerce_raw_json_object(value: Any) -> dict[str, Any] | None:
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _sanitize_persona_id(persona_id: Any) -> str:
    return str(persona_id).replace("/", "_").replace("..", "_")


def _normalize_persona_payload(persona: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": persona["name"],
        "content": persona.get("content") or "",
        "source_path": persona.get("source_path") or "unknown",
        "created_at": persona.get("created_at", ""),
    }


def _build_persona_export_path(persona_id: Any) -> Any:
    export_dir = get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "personas"
    export_dir.mkdir(parents=True, exist_ok=True)
    sanitized = _sanitize_persona_id(persona_id) or "unknown"
    return export_dir / f"persona_{sanitized}.json"


def persona_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "import":
        return runtime._persona_import(command, event)
    if subcommand == "new":
        return persona_new(runtime, command)
    if subcommand == "list":
        return runtime._persona_list(command)
    if subcommand == "inspect":
        return runtime._persona_inspect(command)
    if subcommand == "use":
        return runtime._persona_use(command, event)
    if subcommand == "temp":
        return persona_temp(runtime, command, event)
    if subcommand == "export":
        return persona_export(runtime, command)
    if subcommand == "clear":
        return runtime._persona_clear(event)
    if subcommand == "debug":
        return runtime._persona_debug(event)
    return "Usage: /rp persona import <file> | /rp persona new <name> <text> | /rp persona list [limit] [page] | /rp persona inspect <persona> | /rp persona use <persona> | /rp persona export <persona> | /rp persona temp <text> | /rp persona clear | /rp persona debug"


def persona_import(runtime: Any, command: RPCommand, event: Any) -> str:
    explicit_value = " ".join(command.args[1:]) if len(command.args) >= 2 else None
    decision = resolve_import_path(
        event,
        explicit_value,
        label="persona",
        suffixes=_IMPORTABLE_PERSONA_SUFFIXES,
        usage="Usage: /rp persona import <file.json|file.txt>",
        attach_tip="a .json or .txt persona",
    )
    if decision.error:
        return decision.error
    path = decision.value
    if not path.exists():
        return f"Persona file not found: {path}"
    persona = import_persona_file(path)
    if not persona.content:
        return "Persona import failed: empty persona content."
    persona_id = runtime.store.save_persona(persona)
    runtime.store.set_last_persona(persona_id)
    return (
        f"Imported Hermes Tavern persona: {persona.name}\n"
        f"id: {persona_id}\n"
        f"chars: {len(persona.content)}\n"
        f"use: /rp persona use {persona_id[:8]}\n"
        f"inspect: /rp persona inspect {persona_id[:8]}"
    )


def persona_new(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 3:
        return "Usage: /rp persona new <name> <text>"
    name = command.args[1].strip()
    content = " ".join(command.args[2:]).strip()
    if not name or not content:
        return "Usage: /rp persona new <name> <text>"
    persona = import_raw_persona_text(
        content,
        name=name,
        source_path="telegram:/rp persona new",
    )
    persona_id = runtime.store.save_persona(persona)
    runtime.store.set_last_persona(persona_id)
    return (
        f"Hermes Tavern persona created: {persona.name}\n"
        f"id: {persona_id}\n"
        f"use: /rp persona use {persona_id[:8]}\n"
        f"inspect: /rp persona inspect {persona_id[:8]}"
    )


def persona_list(runtime: Any, command: RPCommand) -> str:
    args = command.args[1:] if command.args else []
    parsed = parse_pagination(args, default_limit=10, max_limit=25)
    if parsed is None:
        return "Usage: /rp persona list [limit] [page]"
    limit, page = parsed
    total = runtime.store.count_personas()
    total_pages = max(1, math.ceil(total / limit))
    page = min(page, total_pages)
    offset = (page - 1) * limit
    personas = runtime.store.list_personas(limit=limit, offset=offset)
    if total == 0:
        return "No Hermes Tavern personas imported."
    lines = [f"Hermes Tavern personas (page {page}/{total_pages}, {len(personas)} shown, {total} total):"]
    for persona in personas:
        preview = mobile_preview(persona.get("content") or "", 72)
        lines.append(f"  - {persona['name']} ({persona['id'][:8]}): {preview}")
    if page > 1:
        lines.append(f"prev: /rp persona list {limit} {page - 1}")
    if page < total_pages:
        lines.append(f"next: /rp persona list {limit} {page + 1}")
    return "\n".join(lines)


def persona_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp persona inspect <persona>"
    persona_ref = " ".join(command.args[1:]).strip()
    persona = runtime.store.get_persona(persona_ref)
    if persona is None:
        return _persona_not_found(persona_ref)
    source = persona.get("source_path") or "unknown"
    lines = [
        f"Persona: {persona['name']} ({persona['id'][:8]})",
        f"source: {mobile_preview(source, 96)}",
        f"chars: {len(persona.get('content') or '')}",
        "preview:",
        f"  {mobile_preview(persona.get('content') or '', 220)}",
        f"use: /rp persona use {persona['id'][:8]}",
    ]
    return "\n".join(lines)


def persona_use(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp persona use <persona>"
    persona_ref = " ".join(command.args[1:]).strip()
    persona = runtime.store.get_persona(persona_ref)
    if persona is None:
        return _persona_not_found(persona_ref)
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session. Start one with /rp start <card>."
    runtime.store.set_session_persona(session_key, persona["id"])
    return f"Hermes Tavern persona bound: {persona['name']} ({persona['id']})"


def persona_temp(runtime: Any, command: RPCommand, event: Any) -> str:
    content = " ".join(command.args[1:]).strip()
    if not content:
        return "Usage: /rp persona temp <text>"
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session. Start one with /rp start <card>."
    persona = import_raw_persona_text(
        content,
        name="temporary",
        source_path="telegram:/rp persona temp",
    )
    persona_id = runtime.store.save_persona(persona)
    runtime.store.set_last_persona(persona_id)
    runtime.store.set_session_persona(session_key, persona_id)
    return (
        f"Hermes Tavern temporary persona bound ({persona_id[:8]}).\n"
        f"preview: {mobile_preview(content, 160)}"
    )


def persona_export(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp persona export <persona>"

    persona_ref = " ".join(command.args[1:]).strip()
    if not persona_ref:
        return "Usage: /rp persona export <persona>"

    persona = runtime.store.get_persona(persona_ref)
    if persona is None:
        return _persona_not_found(persona_ref)

    payload = _coerce_raw_json_object(persona.get("raw_json"))
    if payload is None:
        payload = _normalize_persona_payload(persona)

    export_path = _build_persona_export_path(persona["id"])
    export_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return f"Persona exported as JSON.\nfile: {export_path}\nMEDIA:\"{export_path}\""


def persona_clear(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session."
    runtime.store.set_session_persona(session_key, None)
    return "Hermes Tavern persona cleared for this session."


def persona_debug(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    modules = runtime._session_persona_modules(session)
    if not modules:
        return "No persona bound to this session."
    module = modules[0]
    persona = runtime.store.get_persona(session.get("persona_id") or "")
    return "\n".join(
        [
            f"Persona: {(persona or {}).get('name', 'unknown')} ({(session.get('persona_id') or '')[:8]})",
            f"module: {module.name}",
            f"chars: {len(module.content)}",
            f"preview: {mobile_preview(module.content, 180)}",
        ]
    )
