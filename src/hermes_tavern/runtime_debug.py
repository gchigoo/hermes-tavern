"""Debug and prompt-inspection command handlers for Hermes Tavern runtime."""

from __future__ import annotations

import math
from typing import Any

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.identity import session_key_from_event
from plugins.hermes_tavern.prompt import PromptCompiler
from plugins.hermes_tavern.renderers import ChatRenderer
from plugins.hermes_tavern.runtime_utils import (
    build_macro_context as _build_macro_context,
    card_row_to_obj as _card_row_to_obj,
    mobile_preview as _mobile_preview,
)

_compiler = PromptCompiler()
_chat_renderer = ChatRenderer()


def debug_prompt(runtime, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."

    limit = 8
    page = 1
    prompt_args = command.args[1:] if command.args and command.args[0].lower() == "prompt" else command.args
    if prompt_args:
        try:
            limit = max(1, min(30, int(prompt_args[0])))
        except ValueError:
            return "Usage: /rp debug prompt [limit] [page]"
    if len(prompt_args) > 1:
        try:
            page = max(1, int(prompt_args[1]))
        except ValueError:
            return "Usage: /rp debug prompt [limit] [page]"

    history = runtime.store.get_recent_messages(session["id"], limit=20)

    card = None
    if session.get("card_id"):
        card_row = runtime.store.get_card(session["card_id"])
        if card_row:
            card = _card_row_to_obj(card_row)
    if card is None:
        return "No character card bound to this session."

    ctx = _compiler.compile(
        card,
        history,
        "",
        preset_modules=runtime._session_prompt_modules(session, "", history),
        macro_context=_build_macro_context(card, session, event),
    )
    rendered = _chat_renderer.render(ctx)
    macro_context = _build_macro_context(card, session, event)
    debug_rows: list[tuple[str, str, str]] = []
    for i, m in enumerate(ctx.modules):
        debug_rows.append((f"module {i}", f"{m.role}/{m.name}", m.content))
    for i, turn in enumerate(ctx.history):
        debug_rows.append((f"history {i}", turn.get("role", "unknown"), turn.get("content", "")))
    for i, message in enumerate(rendered):
        debug_rows.append((f"rendered {i}", message.get("role", "unknown"), message.get("content", "")))
    total = len(debug_rows)
    total_pages = max(1, math.ceil(total / limit))
    page = min(page, total_pages)
    start = (page - 1) * limit
    shown_rows = debug_rows[start:start + limit]
    lines = [
        "Hermes Tavern prompt debug",
        f"card: {ctx.card_name}",
        f"content_mode: {session.get('content_mode') or 'safe'}",
        "macro_context: "
        f"char={macro_context.char_name}; "
        f"user={macro_context.user_name}; "
        f"session={macro_context.session_title or 'none'}; "
        f"content_mode={macro_context.content_mode}",
        f"preset: {session.get('preset_id') or 'none'}",
        f"lorebook: {session.get('lorebook_id') or 'none'}",
        f"persona: {session.get('persona_id') or 'none'}",
        f"note: {'yes' if (session.get('note_text') or '').strip() else 'none'}",
        f"note_position: {session.get('note_position') or 'before_user'}",
        f"note_frequency: {(session.get('note_frequency') or 'always') if (session.get('note_frequency') or 'always') == 'always' else 'every_n ' + str(session.get('note_every_n') or 3)}",
        f"memory_facts: {len(runtime.store.list_session_memory_facts(session_key))}",
        f"memory_summary: {'yes' if runtime.store.get_session_summary(session_key) else 'none'}",
        f"modules: {len(ctx.modules)}",
        f"history turns: {len(ctx.history)}",
        f"rendered messages: {len(rendered)}",
        f"tokens: {ctx.token_budget}",
        f"showing rows {start + 1 if total else 0}-{start + len(shown_rows)} of {total} (page {page}/{total_pages})",
        "---",
    ]
    for label, role, content in shown_rows:
        lines.append(f"  [{label}] {role}: {_mobile_preview(content, 140)}")
    if page > 1:
        lines.append(f"prev: /rp debug prompt {limit} {page - 1}")
    if page < total_pages:
        lines.append(f"next: /rp debug prompt {limit} {page + 1}")
    return "\n".join(lines)
