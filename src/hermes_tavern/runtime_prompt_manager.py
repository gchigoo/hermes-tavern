"""Prompt module controls for the active Tavern preset."""

from __future__ import annotations

import json
from typing import Any

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.identity import session_key_from_event
from plugins.hermes_tavern.runtime_utils import mobile_preview, module_risk_counts_db

_USAGE = (
    "Usage: /rp prompt list | /rp prompt inspect <module> | "
    "/rp prompt enable <module> | /rp prompt disable <module> | /rp prompt debug"
)
_BLOCKED_RISKS = {"jailbreak", "disallowed"}


def prompt_command(runtime: Any, command: RPCommand, event: Any) -> str:
    action = command.args[0].lower() if command.args else "list"
    if action == "list":
        return prompt_list(runtime, event)
    if action == "inspect":
        return prompt_inspect(runtime, command, event)
    if action == "enable":
        return prompt_set_enabled(runtime, command, event, enabled=True)
    if action == "disable":
        return prompt_set_enabled(runtime, command, event, enabled=False)
    if action == "debug":
        return prompt_debug(runtime, event)
    return _USAGE


def _active_preset(runtime: Any, event: Any) -> tuple[str, dict[str, Any] | None, dict[str, Any] | None]:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return session_key, None, None
    preset_id = session.get("preset_id")
    preset = runtime.store.get_preset(preset_id) if preset_id else None
    return session_key, session, preset


def _module_risk(module: dict[str, Any]) -> tuple[str, list[str]]:
    try:
        raw = json.loads(module.get("raw_json") or "{}")
    except Exception:
        raw = {}
    risk = str(raw.get("risk_level") or "safe")
    reasons = raw.get("risk_reasons") or []
    if not isinstance(reasons, list):
        reasons = [str(reasons)]
    return risk, [str(reason) for reason in reasons]


def _module_or_message(runtime: Any, command: RPCommand, event: Any) -> tuple[dict[str, Any] | None, str | None, dict[str, Any] | None]:
    _, session, preset = _active_preset(runtime, event)
    if session is None:
        return None, "No active Hermes Tavern session.", None
    if preset is None:
        return None, "No preset is bound to this session. Use /rp preset use <preset> first.", None
    if len(command.args) < 2:
        return None, "Usage: /rp prompt inspect <module>", preset
    ref = " ".join(command.args[1:]).strip()
    module = runtime.store.get_prompt_module(ref, preset_id=preset["id"])
    if module is None:
        return None, f"Prompt module not found in active preset: {ref}", preset
    return module, None, preset


def prompt_list(runtime: Any, event: Any) -> str:
    _, session, preset = _active_preset(runtime, event)
    if session is None:
        return "No active Hermes Tavern session."
    if preset is None:
        return "No preset is bound to this session. Use /rp preset use <preset> first."
    modules = runtime.store.list_prompt_modules(preset["id"])
    if not modules:
        return f"Active preset has no prompt modules: {preset['name']}"
    counts = module_risk_counts_db(modules)
    lines = [
        f"Hermes Tavern prompt modules for {preset['name']} ({len(modules)}):",
        (
            "counts: "
            f"safe={counts['safe']}, adult_fiction={counts['adult_fiction']}, "
            f"risky_disabled={counts['risky_disabled']}"
        ),
    ]
    for module in modules:
        risk, _ = _module_risk(module)
        status = "on" if module.get("enabled") else "off"
        preview = mobile_preview(module.get("content") or "", 64)
        lines.append(
            f"- {module['name']} [{status}, {risk}, {module.get('position')}, "
            f"{module.get('role')}] {preview}"
        )
    lines.append("inspect: /rp prompt inspect <module>")
    lines.append("toggle: /rp prompt enable <module> | /rp prompt disable <module>")
    return "\n".join(lines)


def prompt_inspect(runtime: Any, command: RPCommand, event: Any) -> str:
    module, message, preset = _module_or_message(runtime, command, event)
    if message:
        return message
    risk, reasons = _module_risk(module)
    lines = [
        f"Prompt module: {module['name']} ({module['id'][:8]})",
        f"preset: {preset['name']}",
        f"status: {'enabled' if module.get('enabled') else 'disabled'}",
        f"risk: {risk}",
        f"role: {module.get('role')}",
        f"position: {module.get('position')}",
        f"insertion_order: {module.get('insertion_order')}",
    ]
    if reasons:
        lines.append("risk_reasons: " + ", ".join(reasons))
    lines.extend(["", module.get("content") or ""])
    return "\n".join(lines).strip()


def prompt_set_enabled(runtime: Any, command: RPCommand, event: Any, *, enabled: bool) -> str:
    module, message, preset = _module_or_message(runtime, command, event)
    if message:
        return message.replace("inspect", "enable" if enabled else "disable")
    risk, reasons = _module_risk(module)
    if enabled and risk in _BLOCKED_RISKS:
        detail = f" ({', '.join(reasons)})" if reasons else ""
        return (
            f"Prompt module remains disabled: {module['name']} is classified as {risk}{detail}. "
            "Edit or re-import a safer preset module instead."
        )
    runtime.store.set_prompt_module_enabled(module["id"], enabled)
    return (
        f"Hermes Tavern prompt module {'enabled' if enabled else 'disabled'}: "
        f"{module['name']} ({preset['name']})"
    )


def prompt_debug(runtime: Any, event: Any) -> str:
    _, session, preset = _active_preset(runtime, event)
    if session is None:
        return "No active Hermes Tavern session."
    if preset is None:
        return "No preset is bound to this session. Use /rp preset use <preset> first."
    modules = runtime._session_preset_modules(session)
    lines = [
        f"Compiled prompt modules from preset: {preset['name']}",
        f"session content_mode: {session.get('content_mode') or 'safe'}",
        f"compiled modules: {len(modules)}",
    ]
    for module in modules:
        preview = mobile_preview(module.content, 80)
        lines.append(f"- {module.name}: {module.position}/{module.role} {preview}")
    return "\n".join(lines)
