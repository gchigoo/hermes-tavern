"""Preset commands for Hermes Tavern runtime."""

from __future__ import annotations

import json
from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.import_policy import resolve_import_path
from hermes_tavern.importers.presets import import_preset_file
from hermes_tavern.runtime_utils import (
    mobile_preview,
    module_risk_counts,
    module_risk_counts_db,
    usable_module_counts,
)

_IMPORTABLE_PRESET_SUFFIXES = {".json", ".txt"}


def _preset_not_found(ref: str) -> str:
    if ref.strip().lower() == "last":
        return "No preset has been imported yet. Import a preset first: /rp preset import <file>"
    return f"Preset not found: {ref}"


def preset_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "import":
        return runtime._preset_import(command, event)
    if subcommand == "list":
        return runtime._preset_list()
    if subcommand == "inspect":
        return runtime._preset_inspect(command)
    if subcommand == "use":
        return runtime._preset_use(command, event)
    if subcommand == "clear":
        return preset_clear(runtime, event)
    return "Usage: /rp preset import <file> | /rp preset list | /rp preset inspect <preset> | /rp preset use <preset> | /rp preset clear"


def preset_import(runtime: Any, command: RPCommand, event: Any) -> str:
    explicit_value = " ".join(command.args[1:]) if len(command.args) >= 2 else None
    decision = resolve_import_path(
        event,
        explicit_value,
        label="preset",
        suffixes=_IMPORTABLE_PRESET_SUFFIXES,
        usage="Usage: /rp preset import <file.json|file.txt>",
        attach_tip="a .json or .txt ST preset",
    )
    if decision.error:
        return decision.error
    path = decision.value
    if not path.exists():
        return f"Preset file not found: {path}"
    preset = import_preset_file(path)
    preset_id = runtime.store.save_preset(preset)
    runtime.store.set_last_preset(preset_id)
    counts = module_risk_counts(preset.modules)
    lines = [
        f"Imported ST preset: {preset.name}",
        f"id: {preset_id}",
        "modules:",
    ]
    for key in ("safe", "adult_fiction", "jailbreak", "disallowed"):
        if counts.get(key, 0):
            suffix = " disabled" if key in {"jailbreak", "disallowed"} else ""
            lines.append(f"  {key}: {counts[key]}{suffix}")
    lines.append("Jailbreak/disallowed modules are preserved as disabled imported assets and are not active system prompts.")
    lines.append(f"use: /rp preset use {preset_id[:8]}")
    lines.append(f"inspect: /rp preset inspect {preset_id[:8]}")
    return "\n".join(lines)


def preset_list(runtime: Any) -> str:
    presets = runtime.store.list_presets()
    if not presets:
        return "No Hermes Tavern presets imported."
    lines = ["Hermes Tavern presets:"]
    for preset in presets:
        lines.append(
            "  {name} ({id}): {module_count} modules, {enabled_count} enabled".format(
                name=preset["name"],
                id=preset["id"],
                module_count=preset.get("module_count") or 0,
                enabled_count=preset.get("enabled_count") or 0,
            )
        )
    return "\n".join(lines)


def preset_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp preset inspect <preset>"
    preset_ref = " ".join(command.args[1:]).strip()
    preset = runtime.store.get_preset(preset_ref)
    if preset is None:
        return _preset_not_found(preset_ref)
    modules = runtime.store.list_prompt_modules(preset["id"])
    counts = module_risk_counts_db(modules)
    lines = [
        f"Preset: {preset['name']} ({preset['id'][:8]})",
        f"source: {preset['source']}",
        f"modules: {len(modules)} total",
        f"  safe: {counts['safe']} enabled, adult_fiction: {counts['adult_fiction']} enabled, risky: {counts['risky_disabled']} disabled",
        "module previews:",
    ]
    for module in modules[:5]:
        raw = json.loads(module["raw_json"] or "{}")
        risk = raw.get("risk_level", "safe")
        status = "enabled" if module["enabled"] else "disabled"
        preview = mobile_preview(module["content"], 60)
        lines.append(f"  - {module['name']}: {risk} ({status}) — {preview}")
    lines.append(f"use: /rp preset use {preset['name']}")
    return "\n".join(lines)


def preset_use(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp preset use <preset>"
    preset_ref = " ".join(command.args[1:]).strip()
    preset = runtime.store.get_preset(preset_ref)
    if preset is None:
        return _preset_not_found(preset_ref)
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session. Start one with /rp start <card>."
    if not runtime.store.set_session_preset(session_key, preset["id"]):
        return "Could not bind preset to active session."
    modules = runtime.store.list_prompt_modules(preset["id"])
    usable = usable_module_counts(modules, session.get("content_mode") or "safe")
    return (
        f"Hermes Tavern preset bound: {preset['name']} ({preset['id']})\n"
        f"active safe modules: {usable.get('safe', 0)}\n"
        f"active adult-fiction modules: {usable.get('adult_fiction', 0)}\n"
        f"disabled risky modules: {usable.get('disabled_risky', 0)}"
    )


def preset_clear(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session."
    runtime.store.set_session_preset(session_key, None)
    return "Hermes Tavern preset cleared for this session."
