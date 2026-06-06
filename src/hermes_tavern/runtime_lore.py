"""Lorebook commands for Hermes Tavern runtime."""

from __future__ import annotations

import json
import math
from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.hermes_home import get_hermes_home
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.import_policy import resolve_import_path
from hermes_tavern.importers.lorebooks import import_lorebook_file
from hermes_tavern.lorebook import match_lorebook_entries
from hermes_tavern.runtime_utils import mobile_preview


def _parse_ref_limit_page(args: list[str], *, default_limit: int, max_limit: int) -> tuple[str, int, int]:
    """Parse `<ref> [limit] [page]` while allowing spaces in ref names."""
    parts = list(args)
    page = 1
    limit = default_limit
    if len(parts) >= 2 and parts[-1].isdigit() and parts[-2].isdigit():
        page = max(1, int(parts.pop()))
        limit = max(1, min(max_limit, int(parts.pop())))
    elif len(parts) >= 2 and parts[-1].isdigit():
        limit = max(1, min(max_limit, int(parts.pop())))
    return " ".join(parts).strip(), limit, page


def _lorebook_not_found(ref: str) -> str:
    if ref.strip().lower() == "last":
        return "No lorebook has been imported yet. Import a lorebook first: /rp lore import <file>"
    return f"Lorebook not found: {ref}"


def lore_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "import":
        return runtime._lore_import(command, event)
    if subcommand == "list":
        return runtime._lore_list()
    if subcommand == "inspect":
        return runtime._lore_inspect(command)
    if subcommand == "use":
        return runtime._lore_use(command, event)
    if subcommand == "export":
        return lore_export(runtime, command)
    if subcommand == "clear":
        return lore_clear(runtime, event)
    if subcommand == "enable":
        return lore_set_entry_enabled(runtime, command, event, enabled=True)
    if subcommand == "disable":
        return lore_set_entry_enabled(runtime, command, event, enabled=False)
    if subcommand == "test":
        return runtime._lore_test(command, event)
    if subcommand == "debug":
        return runtime._lore_debug(event)
    return (
        "Usage: /rp lore import <file> | /rp lore list | /rp lore inspect <lorebook> | "
        "/rp lore use <lorebook> | /rp lore export <lorebook> | /rp lore clear | "
        "/rp lore enable <entry> | /rp lore disable <entry> | /rp lore test <message> | /rp lore debug"
    )


def _safe_lore_keys(value: Any) -> list[str]:
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except (TypeError, ValueError, json.JSONDecodeError):
            return []
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.lower() in {"1", "true", "yes", "on"}
    return False


def _as_number(value: Any, default: int | float) -> int | float:
    try:
        return int(value) if isinstance(default, int) else float(value)
    except (TypeError, ValueError):
        return default


def _lorebook_export_filename(lorebook_id: Any) -> str:
    safe = "".join(
        char if char.isalnum() or char in {"-", "_", "."} else "_"
        for char in str(lorebook_id)
    ).strip("._-")
    return f"lorebook_{safe or 'unknown'}.json"


def _coerce_lorebook_raw_payload(lorebook: dict[str, Any]) -> dict[str, Any] | None:
    raw_json = lorebook.get("raw_json")
    if isinstance(raw_json, dict):
        return raw_json
    if isinstance(raw_json, str):
        try:
            parsed = json.loads(raw_json)
        except (TypeError, ValueError, json.JSONDecodeError):
            return None
        return parsed if isinstance(parsed, dict) else None
    return None


def _normalize_lorebook_payload(lorebook: dict[str, Any], entries: list[dict[str, Any]]) -> dict[str, Any]:
    normalized_entries = []
    for row in entries:
        normalized_entries.append(
            {
                "title": row.get("title", ""),
                "content": row.get("content", ""),
                "keys": _safe_lore_keys(row.get("keys_json")),
                "secondary_keys": _safe_lore_keys(row.get("secondary_keys_json")),
                "enabled": _as_bool(row.get("enabled")),
                "constant": _as_bool(row.get("constant")),
                "regex": _as_bool(row.get("regex")),
                "position": row.get("position", ""),
                "insertion_order": _as_number(row.get("insertion_order"), 0),
                "priority": _as_number(row.get("priority"), 0),
                "probability": _as_number(row.get("probability"), 1.0),
            }
        )
    return {
        "name": lorebook.get("name", ""),
        "source": lorebook.get("source", ""),
        "entries": normalized_entries,
    }


def lore_export(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp lore export <lorebook>"
    lore_ref = " ".join(command.args[1:]).strip()
    if not lore_ref:
        return "Usage: /rp lore export <lorebook>"

    lorebook = runtime.store.get_lorebook(lore_ref)
    if lorebook is None:
        return _lorebook_not_found(lore_ref)

    payload = _coerce_lorebook_raw_payload(lorebook)
    if payload is None:
        entries = runtime.store.list_lorebook_entries(lorebook["id"])
        payload = _normalize_lorebook_payload(lorebook, entries)

    payload_text = json.dumps(payload, ensure_ascii=False, indent=2)
    export_dir = get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "lorebooks"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / _lorebook_export_filename(lorebook["id"])
    export_path.write_text(payload_text, encoding="utf-8")

    return f"Lorebook exported as JSON.\nfile: {export_path}\nMEDIA:\"{export_path}\""


def lore_import(runtime: Any, command: RPCommand, event: Any) -> str:
    explicit_value = " ".join(command.args[1:]) if len(command.args) >= 2 else None
    decision = resolve_import_path(
        event,
        explicit_value,
        label="lore",
        suffixes={".json"},
        usage="Usage: /rp lore import <file.json>",
        attach_tip="a .json ST lorebook",
    )
    if decision.error:
        return decision.error
    path = decision.value
    if not path.exists():
        return f"Lorebook file not found: {path}"
    lorebook = import_lorebook_file(path)
    lorebook_id = runtime.store.save_lorebook(lorebook)
    runtime.store.set_last_lorebook(lorebook_id)
    return (
        f"Imported ST lorebook: {lorebook.name}\n"
        f"id: {lorebook_id}\n"
        f"entries: {len(lorebook.entries)}\n"
        f"use: /rp lore use {lorebook_id[:8]}\n"
        f"inspect: /rp lore inspect {lorebook_id[:8]}"
    )


def lore_list(runtime: Any) -> str:
    lorebooks = runtime.store.list_lorebooks()
    if not lorebooks:
        return "No Hermes Tavern lorebooks imported."
    lines = ["Hermes Tavern lorebooks:"]
    for lorebook in lorebooks:
        lines.append(
            "  {name} ({id}): {entry_count} entries, {enabled_count} enabled".format(
                name=lorebook["name"],
                id=lorebook["id"],
                entry_count=lorebook.get("entry_count") or 0,
                enabled_count=lorebook.get("enabled_count") or 0,
            )
        )
    return "\n".join(lines)


def lore_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp lore inspect <lorebook> [limit] [page]"
    lore_ref, limit, page = _parse_ref_limit_page(command.args[1:], default_limit=5, max_limit=20)
    if not lore_ref:
        return "Usage: /rp lore inspect <lorebook> [limit] [page]"
    lorebook = runtime.store.get_lorebook(lore_ref)
    if lorebook is None:
        return _lorebook_not_found(lore_ref)
    entries = runtime.store.list_lorebook_entries(lorebook["id"])
    enabled_count = sum(1 for e in entries if e.get("enabled"))
    constant_count = sum(1 for e in entries if e.get("constant"))
    regex_count = sum(1 for e in entries if e.get("regex"))
    total = len(entries)
    total_pages = max(1, math.ceil(total / limit))
    page = min(page, total_pages)
    offset = (page - 1) * limit
    page_entries = entries[offset : offset + limit]
    lines = [
        f"Lorebook: {lorebook['name']} ({lorebook['id'][:8]})",
        f"source: {lorebook.get('source', 'imported')}",
        f"entries: {total} total, {enabled_count} enabled, {constant_count} constant, {regex_count} regex",
        f"showing entries {offset + 1 if total else 0}-{offset + len(page_entries)} of {total} (page {page}/{total_pages})",
    ]
    for entry in page_entries:
        keys = json.loads(entry.get("keys_json") or "[]")
        secondary = json.loads(entry.get("secondary_keys_json") or "[]")
        key_text = ", ".join(str(k) for k in keys[:3]) or "none"
        flags = []
        if entry.get("enabled"):
            flags.append("enabled")
        else:
            flags.append("disabled")
        if entry.get("constant"):
            flags.append("constant")
        if entry.get("regex"):
            flags.append("regex")
        if secondary:
            flags.append(f"secondary={len(secondary)}")
        preview = mobile_preview(entry.get("content") or "", 72)
        lines.append(f"  - {entry['title']} [{', '.join(flags)}]: keys=[{key_text}] — {preview}")
    if page > 1:
        lines.append(f"prev: /rp lore inspect {lorebook['id'][:8]} {limit} {page - 1}")
    if page < total_pages:
        lines.append(f"next: /rp lore inspect {lorebook['id'][:8]} {limit} {page + 1}")
    lines.append(f"use: /rp lore use {lorebook['id'][:8]}")
    lines.append("test: /rp lore test <message>")
    return "\n".join(lines)


def lore_use(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp lore use <lorebook>"
    lore_ref = " ".join(command.args[1:]).strip()
    lorebook = runtime.store.get_lorebook(lore_ref)
    if lorebook is None:
        return _lorebook_not_found(lore_ref)
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session. Start one with /rp start <card>."
    runtime.store.set_session_lorebook(session_key, lorebook["id"])
    entries = runtime.store.list_lorebook_entries(lorebook["id"])
    enabled = sum(1 for entry in entries if entry.get("enabled"))
    return f"Hermes Tavern lorebook bound: {lorebook['name']} ({lorebook['id']})\nenabled entries: {enabled}"


def lore_clear(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session."
    runtime.store.set_session_lorebook(session_key, None)
    return "Hermes Tavern lorebook cleared for this session."


def lore_set_entry_enabled(runtime: Any, command: RPCommand, event: Any, *, enabled: bool) -> str:
    session = runtime.store.get_active_session(session_key_from_event(event))
    if session is None or not session.get("lorebook_id"):
        return "No active lorebook bound. Start a session and run /rp lore use <lorebook>."
    if len(command.args) < 2:
        action = "enable" if enabled else "disable"
        return f"Usage: /rp lore {action} <entry>"
    entry_ref = " ".join(command.args[1:]).strip()
    entry = runtime.store.get_lorebook_entry(entry_ref, lorebook_id=session["lorebook_id"])
    if entry is None:
        return f"Lorebook entry not found in active lorebook: {entry_ref}"
    runtime.store.set_lorebook_entry_enabled(entry["id"], enabled)
    return f"Hermes Tavern lore entry {'enabled' if enabled else 'disabled'}: {entry['title']}"


def lore_test(runtime: Any, command: RPCommand, event: Any) -> str:
    session = runtime.store.get_active_session(session_key_from_event(event))
    if session is None or not session.get("lorebook_id"):
        return "No active lorebook bound. Start a session and run /rp lore use <lorebook>."
    message = " ".join(command.args[1:]).strip()
    if not message:
        return "Usage: /rp lore test <message>"
    entries = runtime.store.list_lorebook_entries(session["lorebook_id"])
    result = match_lorebook_entries(entries, message)
    lines = [
        f"Lorebook test: {len(result.matches)} matched, {len(result.excluded)} excluded, tokens: {result.token_budget}",
    ]
    if result.matches:
        lines.append("matched:")
        for match in result.matches[:8]:
            lines.append(f"  + {match.title}: {match.reason}")
    else:
        lines.append("matched: none")
    if result.excluded:
        lines.append("excluded sample:")
        for match in result.excluded[:8]:
            lines.append(f"  - {match.title}: {match.reason}")
        if len(result.excluded) > 8:
            lines.append(f"  ... {len(result.excluded) - 8} more excluded")
    lines.append("debug: /rp lore debug")
    return "\n".join(lines)


def lore_debug(runtime: Any, event: Any) -> str:
    session = runtime.store.get_active_session(session_key_from_event(event))
    if session is None:
        return "No active Hermes Tavern session."
    lorebook_id = session.get("lorebook_id")
    if not lorebook_id:
        return "No lorebook bound to this session."
    lorebook = runtime.store.get_lorebook(lorebook_id)
    entries = runtime.store.list_lorebook_entries(lorebook_id)
    lines = [f"Lorebook: {(lorebook or {}).get('name', lorebook_id)} ({lorebook_id})", f"entries: {len(entries)}"]
    for entry in entries:
        keys = json.loads(entry.get("keys_json") or "[]")
        state = "enabled" if entry.get("enabled") else "disabled"
        flags = []
        if entry.get("constant"):
            flags.append("constant")
        if entry.get("regex"):
            flags.append("regex")
        flag_text = f" [{', '.join(flags)}]" if flags else ""
        lines.append(f"  - {entry['title']}: {state}{flag_text}, keys={keys}")
    return "\n".join(lines)
