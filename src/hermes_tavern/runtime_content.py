"""Content-mode commands for Hermes Tavern runtime."""

from __future__ import annotations

from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event


def content_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "mode"
    if subcommand != "mode":
        return "Usage: /rp content mode [safe|adult-fiction]"
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session. Start one before changing content mode."
    if len(command.args) == 1:
        return f"Hermes Tavern content mode: {session.get('content_mode') or 'safe'}"
    requested = command.args[1].lower().replace("_", "-")
    if requested not in {"safe", "adult-fiction"}:
        return "Usage: /rp content mode [safe|adult-fiction]"
    runtime.store.set_session_content_mode(session_key, requested)
    if requested == "adult-fiction":
        return (
            "Hermes Tavern content mode set to adult-fiction for this session. "
            "Only consenting-adult fictional workflows are eligible for adult-fiction preset modules."
        )
    return "Hermes Tavern content mode set to safe for this session."
