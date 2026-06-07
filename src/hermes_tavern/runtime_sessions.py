"""Session browsing and management commands for Hermes Tavern runtime."""

from __future__ import annotations

import datetime
import json
from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.hermes_home import get_hermes_home
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.runtime_utils import parse_pagination


def session_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "info"
    if subcommand == "info":
        return runtime._session_info(event)
    if subcommand == "export":
        return session_export(runtime, command, event)
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
    novel_context = runtime.store.get_novel_context_for_session(session["id"])
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
    if novel_context is not None:
        lines.extend(
            [
                f"Project: {novel_context['project_title']}",
                f"Chapter: {novel_context['chapter_title']}",
                f"Scene: {novel_context['scene_title']}",
            ]
        )
    return "\n".join(lines)


def _session_export_filename(session_id: str) -> str:
    safe_id = "".join(char for char in str(session_id) if char.isalnum())[:16]
    if not safe_id:
        safe_id = "session"
    return f"session_{safe_id}.json"


def session_export(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp session export <id>"
    id_prefix = " ".join(command.args[1:]).strip()
    if not id_prefix:
        return "Usage: /rp session export <id>"

    session_key = session_key_from_event(event)
    matches = runtime.store.list_sessions_by_id_prefix_for_scope(
        session_key,
        id_prefix,
        include_all=True,
        limit=3,
    )
    if not matches:
        return f"Session not found: {id_prefix}"
    if len(matches) > 1:
        choices = ", ".join(f"[{(session.get('id') or '')[:8]}]" for session in matches[:3])
        return f"Multiple sessions match {id_prefix}: {choices}. Use a longer session id."

    session = matches[0]

    messages: list[dict[str, Any]] = []
    page_size = 200
    offset = 0
    while True:
        page = runtime.store.get_messages_page(session["id"], page_size, offset)
        if not page:
            break
        messages.extend(page)
        offset += page_size

    card_name = session.get("card_name") or "unknown"
    card_data: dict[str, Any] | None = None
    if session.get("card_id"):
        card = runtime.store.get_card(session["card_id"])
        if card:
            card_data = json.loads(card.get("data_json") or "{}")
            card_name = card.get("name") or card_name

    preset_name = "none"
    if session.get("preset_id"):
        preset = runtime.store.get_preset(session["preset_id"])
        if preset:
            preset_name = preset.get("name") or "unknown"

    lorebook_name = "none"
    if session.get("lorebook_id"):
        lorebook = runtime.store.get_lorebook(session["lorebook_id"])
        if lorebook:
            lorebook_name = lorebook.get("name") or "unknown"

    content_mode = session.get("content_mode") or "safe"
    session_title = session.get("title") or session.get("id") or "unnamed"

    chat_history: list[dict[str, Any]] = []
    for msg in messages:
        entry: dict[str, Any] = {
            "role": msg.get("role", "unknown"),
            "content": msg.get("content", ""),
        }
        metadata_json = msg.get("metadata_json")
        if metadata_json:
            try:
                metadata = json.loads(metadata_json)
                if metadata.get("swipes"):
                    entry["swipes"] = metadata["swipes"]
                    entry["active_swipe"] = metadata.get("active_swipe", 0)
            except (json.JSONDecodeError, TypeError):
                pass
        chat_history.append(entry)

    export_doc: dict[str, Any] = {
        "hermes_tavern_export": True,
        "exported_at": datetime.datetime.utcnow().isoformat(),
        "session_title": session_title,
        "card_name": card_name,
        "content_mode": content_mode,
        "preset_name": preset_name,
        "lorebook_name": lorebook_name,
        "message_count": len(messages),
        "messages": chat_history,
    }
    if card_data:
        export_doc["card"] = card_data

    export_dir = get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "sessions"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = export_dir / _session_export_filename(session["id"])
    export_path.write_text(
        json.dumps(export_doc, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return f"Session exported as JSON.\nfile: {export_path}\nMEDIA:\"{export_path}\""


def sessions(runtime: Any, command: RPCommand, event: Any) -> str:
    args = list(command.args)
    include_all = bool(args and args[0].lower() == "all")
    if include_all:
        args = args[1:]
    parsed = parse_pagination(args, default_limit=10, max_limit=25)
    if parsed is None:
        return "Usage: /rp sessions [all] [limit] [page]"
    limit, page = parsed
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
