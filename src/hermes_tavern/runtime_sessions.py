"""Session browsing and management commands for Hermes Tavern runtime."""

from __future__ import annotations

from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event


def session_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "info"
    if subcommand == "info":
        return runtime._session_info(event)
    return "Usage: /rp session info"


def session_info(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        paused = runtime.store.get_paused_session(session_key)
        if paused is not None:
            card_name = paused.get("card_name") or paused.get("card_id") or "none"
            short_id = (paused.get("id") or "")[:8]
            return (
                f"Hermes Tavern session [{short_id}] is paused ({card_name}). "
                "Use /rp resume to continue."
            )
        return "No active Hermes Tavern session."
    short_id = (session.get("id") or "")[:8]
    title = session.get("title") or "untitled"
    status = session.get("status") or "active"
    card_name = session.get("card_name") or session.get("card_id") or "none"
    preset_id = session.get("preset_id")
    lorebook_id = session.get("lorebook_id")
    content_mode = session.get("content_mode") or "safe"
    adapter_mode = session.get("adapter_mode") or "fake"
    live_confirmed = bool(session.get("live_confirmed"))
    facts = runtime.store.list_session_memory_facts(session_key)
    summary = runtime.store.get_session_summary(session_key)
    recent_msgs = runtime.store.get_recent_messages(session["id"], limit=5)
    lines = [
        f"Session: [{short_id}] {title} ({status})",
        f"card: {card_name}",
        f"preset: {preset_id[:8] if preset_id else 'none'}",
        f"lorebook: {lorebook_id[:8] if lorebook_id else 'none'}",
        f"content_mode: {content_mode}",
        f"adapter: {adapter_mode} ({'live' if live_confirmed else 'not live'})",
        f"memory: {len(facts)} facts, summary: {'yes' if summary else 'none'}",
        f"recent messages: {len(recent_msgs)}",
        "hints: /rp history | /rp debug prompt | /rp status",
    ]
    return "\n".join(lines)


def sessions(runtime: Any, command: RPCommand, event: Any) -> str:
    args = list(command.args)
    include_all = bool(args and args[0].lower() == "all")
    if include_all:
        args = args[1:]
    limit = 10
    page = 1
    if args:
        try:
            limit = max(1, min(25, int(args[0])))
        except ValueError:
            return "Usage: /rp sessions [all] [limit] [page]"
    if len(args) > 1:
        try:
            page = max(1, int(args[1]))
        except ValueError:
            return "Usage: /rp sessions [all] [limit] [page]"
    session_key = session_key_from_event(event)
    total = runtime.store.count_sessions_for_scope(session_key, include_all=include_all)
    total_pages = max(1, -(-total // limit))
    page = min(page, total_pages)
    offset = (page - 1) * limit
    scoped_sessions = runtime.store.list_sessions_for_scope(
        session_key, include_all=include_all, limit=limit, offset=offset
    )
    active = runtime.store.get_active_session(session_key)
    active_id = (active or {}).get("id")
    all_label = "all, " if include_all else ""
    shown = len(scoped_sessions)
    if not scoped_sessions and total == 0:
        label = "Hermes Tavern sessions (all)" if include_all else "Hermes Tavern sessions"
        return f"{label}: none."
    label_prefix = "Hermes Tavern sessions"
    lines = [f"{label_prefix} ({all_label}page {page}/{total_pages}, {shown} shown, {total} total):"]
    for sess in scoped_sessions:
        short_id = (sess.get("id") or "")[:8]
        status = sess.get("status") or "unknown"
        card_name = sess.get("card_name") or sess.get("card_id") or "no card"
        title = sess.get("title") or ""
        marker = " *" if sess.get("id") == active_id else ""
        title_part = f" — {title}" if title else ""
        lines.append(f"  [{short_id}] ({status}){marker} {card_name}{title_part}")
    nav_prefix = f"/rp sessions {'all ' if include_all else ''}{limit}"
    if page > 1:
        lines.append(f"prev: {nav_prefix} {page - 1}")
    if page < total_pages:
        lines.append(f"next: {nav_prefix} {page + 1}")
    return "\n".join(lines)


def switch(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return "Usage: /rp switch <session-id>"
    id_prefix = command.args[0].strip()
    session_key = session_key_from_event(event)
    matches = runtime.store.list_sessions_by_id_prefix_for_scope(session_key, id_prefix, include_all=True, limit=3)
    if not matches:
        return f"Session not found: {id_prefix}"
    if len(matches) > 1:
        choices = ", ".join(f"[{(session.get('id') or '')[:8]}]" for session in matches[:3])
        return f"Multiple sessions match {id_prefix}: {choices}. Use a longer session id."
    target = matches[0]
    if not runtime.store.switch_to_session(session_key, target["id"]):
        return f"Session not found: {id_prefix}"
    short_id = (target.get("id") or "")[:8]
    title = target.get("title") or ""
    title_part = f" — {title}" if title else ""
    card_name = target.get("card_name") or target.get("card_id") or "no card"
    return f"Hermes Tavern switched to session [{short_id}]{title_part} ({card_name})."


def rename(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return "Usage: /rp rename <name>"
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    new_title = " ".join(command.args).strip()
    runtime.store.rename_session(session["id"], new_title)
    return f'Hermes Tavern session renamed to "{new_title}".'


def archive(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    if runtime.store.get_active_session(session_key) is None:
        return "No active Hermes Tavern session to archive."
    runtime.store.archive_active_session(session_key)
    return "Hermes Tavern session archived. No active session remains for this scope."


def clone(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session to clone."
    title = " ".join(command.args).strip() if command.args else None
    cloned = runtime.store.clone_session(session["id"], session_key, title=title or None)
    short_id = (cloned.get("id") or "")[:8]
    card_name = cloned.get("card_name") or cloned.get("card_id") or "no card"
    title_part = f' "{title}"' if title else ""
    return (
        f"Hermes Tavern session cloned{title_part}: [{short_id}] ({card_name}, active). "
        f"Use /rp switch {short_id} to continue in the new branch."
    )
