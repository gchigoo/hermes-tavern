"""Turn, greeting, voice, and swipe command handlers for Hermes Tavern runtime."""

from __future__ import annotations

import json
from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.runtime_utils import (
    parse_pagination,
    mobile_preview as _mobile_preview,
)


def active_card_data(runtime, event: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return None, None, None
    card = None
    data = None
    if session.get("card_id"):
        card = runtime.store.get_card(session["card_id"])
    if card is not None:
        data = json.loads(card.get("data_json") or "{}")
    return session, card, data


def greeting_options(data: dict[str, Any]) -> list[tuple[int, str, str]]:
    options: list[tuple[int, str, str]] = []
    first_mes = data.get("first_mes") or ""
    if first_mes:
        options.append((0, "first_mes", first_mes))
    alternate = data.get("alternate_greetings") or []
    if isinstance(alternate, list):
        for idx, text in enumerate(alternate, start=1):
            if str(text or "").strip():
                options.append((idx, f"alternate_{idx}", str(text)))
    return options


def greeting(runtime, command: RPCommand, event: Any) -> str:
    session, card, data = active_card_data(runtime, event)
    if session is None:
        return "No active Hermes Tavern session."
    if card is None or data is None:
        return "No character card bound to this session."
    action = command.args[0].lower() if command.args else "list"
    options = greeting_options(data)
    if action == "list":
        if not options:
            return f"No greetings found for {card['name']}."
        lines = [f"Greetings for {card['name']}:"]
        for idx, label, text in options:
            lines.append(f"  [{idx}] {label}: {_mobile_preview(text, 100)}")
        lines.append(f"use: /rp greeting use {options[0][0]}")
        return "\n".join(lines)
    if action == "use":
        if len(command.args) < 2:
            return "Usage: /rp greeting use <0..N>"
        try:
            wanted = int(command.args[1])
        except ValueError:
            return "Usage: /rp greeting use <0..N>"
        for idx, label, text in options:
            if idx == wanted:
                runtime.store.append_message(
                    session["id"],
                    "assistant",
                    text,
                    metadata={"kind": "greeting", "greeting_index": idx, "greeting_label": label},
                )
                return f"Greeting {idx} selected for {card['name']}:\n\n{text}"
        available = ", ".join(str(idx) for idx, _, _ in options) or "none"
        return f"Greeting not found: {wanted}. Available: {available}"
    return "Usage: /rp greeting [list|use <0..N>]"


def say(runtime, command: RPCommand, event: Any) -> str:
    text = " ".join(command.args).strip()
    if not text:
        return "Usage: /rp say <message>"
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session. Start one with /rp start <card>."
    history = runtime.store.get_recent_messages(session["id"], limit=20)
    reply = runtime._run_generation_pipeline(session, text, history, event=event)
    runtime.store.append_message(session["id"], "user", text, metadata={"kind": "rp_say"})
    runtime.store.append_message(session["id"], "assistant", reply)
    return with_auto_speak(runtime, reply, event)


def last_assistant_reply(runtime, session: dict[str, Any]) -> str:
    for msg in reversed(runtime.store.get_recent_messages(session["id"], limit=20)):
        if msg.get("role") == "assistant":
            return (msg.get("content") or "").strip()
    return ""


def _default_tts_renderer(text: str) -> dict[str, Any]:
    from tools.tts_tool import text_to_speech_tool

    raw = text_to_speech_tool(text=text)
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return {"success": False, "error": "TTS renderer returned invalid output"}
    if not isinstance(data, dict):
        return {"success": False, "error": "TTS renderer returned invalid output"}
    return data


def _quoted_media_tag(data: dict[str, Any]) -> str:
    file_path = str(data.get("file_path") or "").strip()
    media_tag = str(data.get("media_tag") or "").strip()
    voice_prefix = "[[audio_as_voice]]\n" if "[[audio_as_voice]]" in media_tag else ""
    if file_path:
        return f'{voice_prefix}MEDIA:"{file_path}"'
    if media_tag.startswith("MEDIA:") or media_tag.startswith("[[audio_as_voice]]"):
        return media_tag
    return ""


def speak(runtime, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    text = last_assistant_reply(runtime, session)
    if not text:
        return "No assistant reply to speak."
    renderer = runtime.tts_renderer or _default_tts_renderer
    try:
        data = renderer(text)
    except Exception:
        return "Hermes Tavern speak: TTS failed. Check Hermes TTS setup."
    if not isinstance(data, dict) or not data.get("success"):
        return "Hermes Tavern speak: TTS unavailable. Check Hermes TTS setup."
    media_tag = _quoted_media_tag(data)
    if not media_tag:
        return "Hermes Tavern speak: TTS produced no deliverable audio."
    provider = str(data.get("provider") or "tts")
    return f"Hermes Tavern speak: audio ready ({provider}).\n{media_tag}"


def voice(runtime, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    if len(command.args) == 0:
        state = "on" if session_key in runtime._voice_enabled_session_keys else "off"
        return f"Hermes Tavern voice: {state}."
    action = command.args[0].lower()
    if action == "on":
        runtime._voice_enabled_session_keys.add(session_key)
        return "Hermes Tavern voice: on."
    if action == "off":
        runtime._voice_enabled_session_keys.discard(session_key)
        return "Hermes Tavern voice: off."
    return "Usage: /rp voice [on|off]"


def with_auto_speak(runtime, reply: str, event: Any) -> str:
    session_key = session_key_from_event(event)
    if session_key not in runtime._voice_enabled_session_keys:
        return reply
    return f"{reply}\n\n{speak(runtime, event)}"


def history(runtime, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    parsed = parse_pagination(command.args, default_limit=10, max_limit=50)
    if parsed is None:
        return "Usage: /rp history [limit] [page]"
    limit, page = parsed
    total = runtime.store.count_messages(session["id"])
    total_pages = max(1, -(-total // limit))  # ceil division
    page = min(page, total_pages)
    offset = (page - 1) * limit
    messages = runtime.store.get_messages_page(session["id"], limit=limit, offset=offset)
    shown = len(messages)
    lines = [f"Hermes Tavern session history (page {page}/{total_pages}, {shown} shown, {total} total):"]
    for msg in messages:
        short_id = (msg.get("id") or "")[:8]
        preview = _mobile_preview(msg.get("content") or "", 80)
        lines.append(f"  [{short_id}] {msg['role']}: {preview}")
    if page > 1:
        lines.append(f"prev: /rp history {limit} {page - 1}")
    if page < total_pages:
        lines.append(f"next: /rp history {limit} {page + 1}")
    return "\n".join(lines)


def last_user_assistant_turn(runtime, session: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]] | None:
    history_rows = runtime.store.get_recent_messages(session["id"], limit=20)
    if len(history_rows) < 2 or history_rows[-1]["role"] != "assistant" or history_rows[-2]["role"] != "user":
        return None
    return history_rows[:-2], history_rows[-2], history_rows[-1]


def assistant_swipe_metadata(assistant_msg: dict[str, Any]) -> dict[str, Any]:
    try:
        metadata = json.loads(assistant_msg.get("metadata_json") or "{}")
    except (TypeError, ValueError):
        metadata = {}
    swipes = metadata.get("swipes")
    if not isinstance(swipes, list) or not swipes:
        swipes = [assistant_msg.get("content") or ""]
    swipes = [str(item) for item in swipes if str(item or "").strip()]
    if not swipes:
        swipes = [assistant_msg.get("content") or ""]
    active = metadata.get("active_swipe", len(swipes) - 1)
    try:
        active = int(active)
    except (TypeError, ValueError):
        active = len(swipes) - 1
    active = max(0, min(active, len(swipes) - 1))
    return {"kind": "assistant_turn", "swipes": swipes, "active_swipe": active}


def debug_swipes(runtime, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    turn = last_user_assistant_turn(runtime, session)
    if turn is None:
        return "No assistant reply with swipes. Send a turn first."
    _prior_history, user_msg, assistant_msg = turn
    metadata = assistant_swipe_metadata(assistant_msg)
    lines = [
        "Hermes Tavern swipe debug",
        f"user: {_mobile_preview(user_msg.get('content') or '', 120)}",
        f"assistant_message: {(assistant_msg.get('id') or '')[:8]}",
        f"candidates: {len(metadata['swipes'])}",
        f"active_swipe: {metadata['active_swipe']}",
        "---",
    ]
    for idx, text in enumerate(metadata["swipes"]):
        marker = "*" if idx == metadata["active_swipe"] else " "
        lines.append(f"{marker} [{idx}] chars={len(text)} preview={_mobile_preview(text, 140)}")
    return "\n".join(lines)


def retry(runtime, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    turn = last_user_assistant_turn(runtime, session)
    if turn is None:
        return "No assistant reply to retry."
    prior_history, user_msg, assistant_msg = turn
    metadata = assistant_swipe_metadata(assistant_msg)
    user_text = user_msg["content"]
    reply = runtime._run_generation_pipeline(session, user_text, prior_history)
    metadata["swipes"].append(reply)
    metadata["active_swipe"] = len(metadata["swipes"]) - 1
    runtime.store.delete_message(assistant_msg["id"])
    runtime.store.append_message(session["id"], "assistant", reply, metadata=metadata)
    body = f"Hermes Tavern retry:\n\n{reply}\n\nretry again: /rp retry"
    return with_auto_speak(runtime, body, event)


def swipe(runtime, command: RPCommand, event: Any) -> str:
    action = command.args[0].lower() if command.args else "list"
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    turn = last_user_assistant_turn(runtime, session)
    if turn is None:
        return "No assistant reply with swipes. Send a turn first."
    prior_history, user_msg, assistant_msg = turn
    metadata = assistant_swipe_metadata(assistant_msg)
    swipes = metadata["swipes"]
    if action == "list":
        lines = [f"Swipes for last turn: {len(swipes)} candidate(s), active {metadata['active_swipe']}."]
        for idx, text in enumerate(swipes):
            marker = "*" if idx == metadata["active_swipe"] else " "
            lines.append(f"{marker} [{idx}] {_mobile_preview(text, 100)}")
        lines.append("add: /rp swipe add")
        lines.append("use: /rp swipe use <n>")
        return "\n".join(lines)
    if action == "add":
        reply = runtime._run_generation_pipeline(session, user_msg["content"], prior_history)
        swipes.append(reply)
        metadata["swipes"] = swipes
        metadata["active_swipe"] = len(swipes) - 1
        runtime.store.update_message(assistant_msg["id"], reply, metadata=metadata)
        body = f"Swipe {metadata['active_swipe']} added and selected:\n\n{reply}"
        return with_auto_speak(runtime, body, event)
    if action == "use":
        if len(command.args) < 2:
            return "Usage: /rp swipe use <n>"
        try:
            idx = int(command.args[1])
        except ValueError:
            return "Usage: /rp swipe use <n>"
        if idx < 0 or idx >= len(swipes):
            return f"Swipe not found: {idx}. Available: 0-{len(swipes) - 1}"
        metadata["active_swipe"] = idx
        runtime.store.update_message(assistant_msg["id"], swipes[idx], metadata=metadata)
        return f"Swipe {idx} selected:\n\n{swipes[idx]}"
    return "Usage: /rp swipe [list|add|use <n>]"


def undo(runtime, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    deleted = runtime.store.delete_last_user_assistant_turn(session["id"])
    if deleted == 0:
        return "No turn to undo."
    noun = "message" if deleted == 1 else "messages"
    return f"Undid last turn (removed {deleted} {noun}).\nundo again: /rp undo"


def edit(runtime, command: RPCommand, event: Any) -> str:
    if not command.args or command.args[0].lower() != "last" or len(command.args) < 2:
        return "Usage: /rp edit last <text>"
    new_text = " ".join(command.args[1:]).strip()
    if not new_text:
        return "Usage: /rp edit last <text>"
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."
    updated = runtime.store.update_last_user_message(session["id"], new_text)
    if updated is None:
        return "No user message to edit."
    runtime.store.delete_assistant_after_last_user_message(session["id"])
    history_rows = runtime.store.get_recent_messages(session["id"], limit=20)
    if not history_rows or history_rows[-1]["role"] != "user":
        return "Could not regenerate after edit."
    user_text = history_rows[-1]["content"]
    prior_history = history_rows[:-1]
    reply = runtime._run_generation_pipeline(session, user_text, prior_history)
    runtime.store.append_message(session["id"], "assistant", reply)
    body = f"Hermes Tavern edit:\n\n{reply}\n\nedit again: /rp edit last <text>"
    return with_auto_speak(runtime, body, event)
