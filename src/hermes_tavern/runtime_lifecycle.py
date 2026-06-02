"""Lifecycle, status, and export command handlers for Hermes Tavern runtime."""

from __future__ import annotations

import datetime
import json
from typing import Any

from hermes_tavern.hermes_home import get_hermes_home
from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.importers.cards import parse_character_card
from hermes_tavern.importers.lorebooks import import_embedded_lorebook_from_card


def _last_asset_help(asset_type: str) -> str:
    commands = {
        "card": "/rp card import <file>",
        "preset": "/rp preset import <file>",
        "lorebook": "/rp lore import <file>",
        "persona": "/rp persona import <file>",
    }
    return f"No {asset_type} has been imported yet. Import a {asset_type} first: {commands[asset_type]}"


def _asset_not_found(asset_type: str, ref: str) -> str:
    if ref.strip().lower() == "last":
        return _last_asset_help(asset_type)
    labels = {
        "card": "Character card",
        "preset": "Preset",
        "lorebook": "Lorebook",
        "persona": "Persona",
    }
    return f"{labels[asset_type]} not found: {ref}"


def export(runtime: Any, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        paused = runtime.store.get_paused_session(session_key)
        if paused is not None:
            card_name = paused.get("card_name") or paused.get("card_id") or "unknown card"
            return (
                f"Paused Hermes Tavern session with {card_name}. "
                "Use /rp resume to continue or /rp start <card> to begin a fresh session."
            )
        return "No active Hermes Tavern session."

    fmt = "markdown"
    if command.args:
        fmt = command.args[0].lower()
    if fmt not in {"markdown", "st-json"}:
        return "Usage: /rp export [markdown|st-json]"

    # Gather all messages
    messages: list[dict[str, Any]] = []
    page_size = 200
    offset = 0
    while True:
        page = runtime.store.get_messages_page(session["id"], page_size, offset)
        if not page:
            break
        messages.extend(page)
        offset += page_size

    # Gather card / lorebook / preset info
    card_name = session.get("card_name") or "unknown"
    card_data: dict[str, Any] | None = None
    if session.get("card_id"):
        card_row = runtime.store.get_card(session["card_id"])
        if card_row:
            card_data = json.loads(card_row.get("data_json") or "{}")
            card_name = card_row.get("name") or card_name

    lorebook_name = "none"
    if session.get("lorebook_id"):
        lb = runtime.store.get_lorebook(session["lorebook_id"])
        if lb:
            lorebook_name = lb.get("name") or "unknown"

    preset_name = "none"
    if session.get("preset_id"):
        p = runtime.store.get_preset(session["preset_id"])
        if p:
            preset_name = p.get("name") or "unknown"

    content_mode = session.get("content_mode") or "safe"
    session_title = session.get("title") or session.get("id") or "unnamed"

    # Ensure export directory (profile-safe; gateway can deliver MEDIA attachments)
    export_dir = get_hermes_home() / "hermes-agent" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)

    ts = datetime.datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    safe_title = "".join(c if c.isalnum() or c in "._- " else "_" for c in session_title[:40]).strip().replace(" ", "_")
    if fmt == "markdown":
        out = export_dir / f"tavern-{safe_title}-{ts}.md"
        lines = [
            f"# Hermes Tavern Session: {card_name}",
            f"",
            f"- **Session**: {session_title}",
            f"- **Card**: {card_name}",
            f"- **Content mode**: {content_mode}",
            f"- **Preset**: {preset_name}",
            f"- **Lorebook**: {lorebook_name}",
            f"- **Messages**: {len(messages)}",
            f"- **Exported**: {datetime.datetime.utcnow().isoformat()}",
            f"",
            f"---",
            f"",
        ]
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            metadata_json = msg.get("metadata_json")
            lines.append(f"### {role.title()}")
            lines.append(f"")
            lines.append(content)
            lines.append(f"")
            if metadata_json:
                try:
                    meta = json.loads(metadata_json)
                    if meta.get("swipes"):
                        active = meta.get("active_swipe", 0)
                        lines.append(f"> Swipes: {len(meta['swipes'])} candidate(s), active {active}")
                        lines.append(f"")
                except (json.JSONDecodeError, TypeError):
                    pass
        out.write_text("\n".join(lines), encoding="utf-8")
        return f"Session exported as Markdown.\nfile: {out}\nMEDIA:\"{out}\""

    # st-json
    out = export_dir / f"tavern-{safe_title}-{ts}.json"
    chat_history: list[dict[str, Any]] = []
    for msg in messages:
        entry: dict[str, Any] = {
            "role": msg.get("role", "unknown"),
            "content": msg.get("content", ""),
        }
        metadata_json = msg.get("metadata_json")
        if metadata_json:
            try:
                meta = json.loads(metadata_json)
                if meta.get("swipes"):
                    entry["swipes"] = meta["swipes"]
                    entry["active_swipe"] = meta.get("active_swipe", 0)
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
    out.write_text(json.dumps(export_doc, ensure_ascii=False, indent=2), encoding="utf-8")
    return f"Session exported as ST-compatible JSON.\nfile: {out}\nMEDIA:\"{out}\""


def status(runtime: Any, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        paused = runtime.store.get_paused_session(session_key)
        if paused is not None:
            card_name = paused.get("card_name") or paused.get("card_id") or "unknown card"
            return (
                f"Paused Hermes Tavern session with {card_name}. "
                "Use /rp resume to continue or /rp start <card> to begin a fresh session."
            )
        return "No active Hermes Tavern session."
    card_name = session.get("card_name") or session.get("card_id") or "unknown card"
    return (
        f"Active Hermes Tavern session with {card_name} ({session['status']}).\n"
        f"content_mode: {session.get('content_mode') or 'safe'}\n"
        f"preset: {session.get('preset_id') or 'none'}\n"
        f"lorebook: {session.get('lorebook_id') or 'none'}\n"
        f"memory_facts: {len(runtime.store.list_session_memory_facts(session_key))}\n"
        f"memory_summary: {'yes' if runtime.store.get_session_summary(session_key) else 'none'}"
    )


def end(runtime: Any, event: Any) -> str:
    if runtime.store.end_session(session_key_from_event(event)):
        return "Hermes Tavern session ended."
    return "No active Hermes Tavern session to end."


def pause(runtime: Any, event: Any) -> str:
    if runtime.store.pause_session(session_key_from_event(event)):
        return "Hermes Tavern session paused. Ordinary messages will go to normal Hermes until /rp resume."
    return "No active Hermes Tavern session to pause."


def resume(runtime: Any, event: Any) -> str:
    if runtime.store.resume_session(session_key_from_event(event)):
        return "Hermes Tavern session resumed."
    return "No paused Hermes Tavern session to resume."


def start(runtime: Any, command: RPCommand, event: Any) -> str:
    card_ref = " ".join(command.args).strip()
    if not card_ref:
        return "Usage: /rp start <card>"

    card = runtime.store.get_card(card_ref)
    if card is None:
        return _asset_not_found("card", card_ref)

    session = runtime.store.start_session(
        session_key_from_event(event),
        card_id=card["id"],
    )
    data = json.loads(card["data_json"])
    embedded_lorebook = None
    raw_card = data.get("raw")
    if isinstance(raw_card, dict):
        try:
            embedded_lorebook = import_embedded_lorebook_from_card(parse_character_card(raw_card))
        except ValueError:
            embedded_lorebook = None
    greeting = data.get("first_mes") or ""
    lines = [f"Started Hermes Tavern session with {card['name']}."]
    if embedded_lorebook is not None:
        lorebook_id = runtime.store.save_lorebook(embedded_lorebook)
        if runtime.store.set_session_lorebook(session_key_from_event(event), lorebook_id):
            lines.append(
                f"embedded lorebook bound: {embedded_lorebook.name} ({lorebook_id[:8]}), {len(embedded_lorebook.entries)} entries"
            )
    if greeting:
        runtime.store.append_message(session["id"], "assistant", greeting)
        lines.extend(["", greeting])
    return "\n".join(lines)
