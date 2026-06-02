"""Author's Note command helpers for Hermes Tavern runtime."""

from __future__ import annotations

from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.runtime_utils import mobile_preview as _mobile_preview

_NOTE_USAGE = (
    "Usage: /rp note set <text> | /rp note clear | /rp note inspect | "
    "/rp note position [before_char|after_history|before_user] | "
    "/rp note frequency [always|every_n [n]]"
)


def note_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "inspect"
    if subcommand == "set":
        return note_set(runtime, command, event)
    if subcommand == "clear":
        return note_clear(runtime, event)
    if subcommand == "inspect":
        return note_inspect(runtime, event)
    if subcommand == "position":
        return note_position(runtime, command, event)
    if subcommand == "frequency":
        return note_frequency(runtime, command, event)
    return _NOTE_USAGE


def note_active_session(runtime: Any, event: Any) -> tuple[str, dict[str, Any] | None]:
    session_key = session_key_from_event(event)
    return session_key, runtime.store.get_active_session(session_key)


def note_set(runtime: Any, command: RPCommand, event: Any) -> str:
    text = " ".join(command.args[1:]).strip()
    if not text:
        return "Usage: /rp note set <text>"
    session_key, session = note_active_session(runtime, event)
    if session is None:
        return "No active Hermes Tavern session. Start one with /rp start <card>."
    runtime.store.set_session_note(session_key, text)
    return f"Author note saved ({len(text)} chars).\ninspect: /rp note inspect"


def note_clear(runtime: Any, event: Any) -> str:
    session_key, session = note_active_session(runtime, event)
    if session is None:
        return "No active Hermes Tavern session."
    runtime.store.clear_session_note(session_key)
    return "Author note cleared for this session."


def note_inspect(runtime: Any, event: Any) -> str:
    _session_key, session = note_active_session(runtime, event)
    if session is None:
        return "No active Hermes Tavern session."
    text = (session.get("note_text") or "").strip()
    position = session.get("note_position") or "before_user"
    frequency = format_note_frequency(session)
    if not text:
        return (
            "No Author note set for this session.\n"
            "set: /rp note set <text>"
        )
    return "\n".join(
        [
            "Author note",
            f"position: {position}",
            f"frequency: {frequency}",
            f"chars: {len(text)}",
            "preview:",
            f"  {_mobile_preview(text, 220)}",
        ]
    )


def note_position(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key, session = note_active_session(runtime, event)
    if session is None:
        return "No active Hermes Tavern session."
    if len(command.args) == 1:
        return f"Author note position: {session.get('note_position') or 'before_user'}"
    position = command.args[1].lower()
    if position not in {"before_char", "after_history", "before_user"}:
        return "Usage: /rp note position [before_char|after_history|before_user]"
    runtime.store.set_session_note_position(session_key, position)
    return f"Author note position: {position}"


def note_frequency(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key, session = note_active_session(runtime, event)
    if session is None:
        return "No active Hermes Tavern session."
    if len(command.args) == 1:
        return f"Author note frequency: {format_note_frequency(session)}"
    frequency = command.args[1].lower()
    if frequency == "always":
        runtime.store.set_session_note_frequency(session_key, "always")
        return "Author note frequency: always"
    if frequency == "every_n":
        every_n = 3
        if len(command.args) > 2:
            try:
                every_n = int(command.args[2])
            except ValueError:
                return "Usage: /rp note frequency [always|every_n [n]]"
        every_n = max(2, min(20, every_n))
        runtime.store.set_session_note_frequency(session_key, "every_n", every_n=every_n)
        return f"Author note frequency: every_n {every_n}"
    return "Usage: /rp note frequency [always|every_n [n]]"


def format_note_frequency(session: dict[str, Any]) -> str:
    frequency = session.get("note_frequency") or "always"
    if frequency == "every_n":
        return f"every_n {int(session.get('note_every_n') or 3)}"
    return "always"
