"""Debug and prompt-inspection command handlers for Hermes Tavern runtime."""

from __future__ import annotations

import math
from os import PathLike
from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.model_router import ModelRouter
from hermes_tavern.prompt import PromptCompiler
from hermes_tavern.renderers import ChatRenderer
from hermes_tavern.utils import estimate_tokens
from hermes_tavern.runtime_utils import (
    parse_pagination,
    build_macro_context as _build_macro_context,
    card_row_to_obj as _card_row_to_obj,
    mobile_preview as _mobile_preview,
)

_compiler = PromptCompiler()
_chat_renderer = ChatRenderer()
_router = ModelRouter()

_ERROR = object()


def debug_prompt(runtime, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."

    prompt_args = command.args[1:] if command.args and command.args[0].lower() == "prompt" else command.args
    parsed = parse_pagination(prompt_args, default_limit=8, max_limit=30)
    if parsed is None:
        return "Usage: /rp debug prompt [limit] [page]"
    limit, page = parsed

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


def debug_context(runtime, command: RPCommand, event: Any) -> str:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session."

    context_args = (
        command.args[1:] if command.args and command.args[0].lower() == "context" else command.args
    )
    parsed = parse_pagination(context_args, default_limit=8, max_limit=30)
    if parsed is None:
        return "Usage: /rp debug context [limit] [page]"
    limit, page = parsed

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
    model = _router.resolve(session_row=session, store=runtime.store)
    model_window = model.context_window

    rows: list[tuple[str, str, str, int]] = []
    for i, module in enumerate(ctx.modules):
        row_content = module.content
        rows.append(
            (
                f"module {i}",
                f"{module.role}/{module.name}",
                row_content,
                estimate_tokens(row_content),
            )
        )
    for i, turn in enumerate(ctx.history):
        row_content = turn.get("content", "")
        rows.append(
            (
                f"history {i}",
                turn.get("role", "unknown"),
                row_content,
                estimate_tokens(row_content),
            )
        )
    for i, message in enumerate(rendered):
        row_content = message.get("content", "")
        rows.append(
            (
                f"rendered {i}",
                message.get("role", "unknown"),
                row_content,
                estimate_tokens(row_content),
            )
        )

    total = len(rows)
    total_pages = max(1, math.ceil(total / limit))
    page = min(page, total_pages)
    start = (page - 1) * limit
    shown_rows = rows[start:start + limit]

    omitted = [
        "preset none" if not session.get("preset_id") else None,
        "lorebook none" if not session.get("lorebook_id") else None,
        "persona none" if not session.get("persona_id") else None,
        "author note none" if not (session.get("note_text") or "").strip() else None,
        "memory summary none" if not runtime.store.get_session_summary(session_key) else None,
    ]
    omitted_parts = [item for item in omitted if item is not None]
    omitted_summary = "omitted: none" if not omitted_parts else "omitted: " + "; ".join(omitted_parts)

    lines = [
        "Hermes Tavern context budget",
        f"card: {ctx.card_name}",
        "renderer: chat",
        f"model: {model.provider}/{model.model_id}",
        f"context_window: {model_window}",
        f"estimated_tokens: {ctx.token_budget}",
        f"modules: {len(ctx.modules)}",
        f"history turns: {len(ctx.history)}",
        f"rendered messages: {len(rendered)}",
        omitted_summary,
        f"showing rows {start + 1 if total else 0}-{start + len(shown_rows)} of {total} (page {page}/{total_pages})",
        "---",
    ]
    for label, role, content, tokens in shown_rows:
        lines.append(f"  [{label}] {role} tokens={tokens}: {_mobile_preview(content, 140)}")
    if page > 1:
        lines.append(f"prev: /rp debug context {limit} {page - 1}")
    if page < total_pages:
        lines.append(f"next: /rp debug context {limit} {page + 1}")
    return "\n".join(lines)


def doctor(runtime: Any, event: Any) -> str:
    """Return a concise offline diagnostic report for the current Tavern scope."""
    store = _safe_attr(runtime, "store", default=None)
    session_key = _safe_session_key(event)
    db_path = _safe_db_path(store)

    active = _safe_store_call(store, "get_active_session", session_key)
    session: dict[str, Any] | None = None
    if active is _ERROR:
        session_status = "error"
    elif isinstance(active, dict) and active:
        session_status = "active"
        session = active
    else:
        paused = _safe_store_call(store, "get_paused_session", session_key)
        if paused is _ERROR:
            session_status = "error"
        elif isinstance(paused, dict) and paused:
            session_status = "paused"
            session = paused
        else:
            session_status = "none"

    cards_count = _safe_list_count(store, "list_cards")
    presets_count = _safe_list_count(store, "list_presets")
    lorebooks_count = _safe_list_count(store, "list_lorebooks")
    personas_count = _safe_count(store, "count_personas")

    lines = [
        "Hermes Tavern doctor",
        f"db path: {db_path}",
        f"scope key: {_clean_text(session_key)}",
        f"session status: {session_status}",
        f"session id: {_short_session_id(session)}",
        f"session card: {_session_card_name(session)}",
        f"cards: {cards_count}",
        f"presets: {presets_count}",
        f"lorebooks: {lorebooks_count}",
        f"personas: {personas_count}",
        f"model mode: {_model_mode(session_status, session)}",
        f"image provider: {_image_provider_label(runtime)}",
        f"tts configured: {_tts_configured(runtime)}",
        f"next: {_next_hint(session_status, cards_count)}",
    ]
    return "\n".join(lines)


def _safe_attr(obj: Any, name: str, *, default: Any = "unknown") -> Any:
    try:
        value = getattr(obj, name, default)
    except Exception:
        return default
    return default if value is None else value


def _safe_session_key(event: Any) -> str:
    try:
        key = session_key_from_event(event)
    except Exception:
        return "unknown:chat:unknown:thread:main:user:unknown"
    return _clean_text(key, default="unknown")


def _safe_db_path(store: Any) -> str:
    if store is None:
        return "unknown"
    return _clean_text(
        _safe_attr(store, "db_path", default="unknown"),
        default="unknown",
        limit=240,
    )


def _safe_store_call(store: Any, method_name: str, *args: Any) -> Any:
    if store is None:
        return _ERROR
    method = _safe_attr(store, method_name, default=None)
    if method is None:
        return _ERROR
    try:
        return method(*args)
    except Exception:
        return _ERROR


def _safe_list_count(store: Any, method_name: str) -> str:
    result = _safe_store_call(store, method_name)
    if result is _ERROR:
        return "error"
    try:
        return str(len(result))
    except Exception:
        return "error"


def _safe_count(store: Any, method_name: str) -> str:
    result = _safe_store_call(store, method_name)
    if result is _ERROR:
        return "error"
    try:
        return str(int(result))
    except Exception:
        return "error"


def _clean_text(value: Any, *, default: str = "unknown", limit: int = 160) -> str:
    if value is None:
        return default
    if isinstance(value, PathLike):
        value = value.__fspath__()
    if not isinstance(value, (str, int, float, bool)):
        return default
    text = (
        str(value)
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("\t", " ")
        .strip()
    )
    while "  " in text:
        text = text.replace("  ", " ")
    if not text:
        return default
    if len(text) > limit:
        return text[: max(0, limit - 3)] + "..."
    return text


def _short_session_id(session: dict[str, Any] | None) -> str:
    if not session:
        return "none"
    session_id = _clean_text(session.get("id"), default="")
    return session_id[:8] if session_id else "none"


def _session_card_name(session: dict[str, Any] | None) -> str:
    if not session:
        return "none"
    return _clean_text(session.get("card_name"), default="none")


def _model_mode(session_status: str, session: dict[str, Any] | None) -> str:
    if session_status == "error":
        return "error"
    if session:
        return _clean_text(session.get("adapter_mode") or "fake", default="fake")
    return "fake (default)"


def _image_provider_label(runtime: Any) -> str:
    provider = _safe_attr(runtime, "image_provider", default=None)
    if provider is None:
        return "none"
    class_name = _clean_text(type(provider).__name__, default="unknown")
    name = _static_provider_name(provider)
    return f"{class_name}/{name}"


def _static_provider_name(provider: Any) -> str:
    value: Any = None
    try:
        value = vars(provider).get("name")
    except Exception:
        value = None
    if value is None:
        try:
            value = vars(type(provider)).get("name")
        except Exception:
            value = None
    return _clean_text(value, default="unknown")


def _tts_configured(runtime: Any) -> str:
    configured = _safe_attr(runtime, "tts_renderer", default=None) is not None
    return "yes" if configured else "no"


def _next_hint(session_status: str, cards_count: str) -> str:
    if session_status == "active":
        return "send a message, or pause with /rp pause before normal Hermes chat"
    if session_status == "paused":
        return "resume with /rp resume"
    if session_status == "error":
        return "check the Tavern DB path and run /rp help"
    if _count_is_zero(cards_count):
        return "import a card with /rp card import <file>"
    return (
        "start a session with /rp start <card> "
        "(import cards with /rp card import <file>)"
    )


def _count_is_zero(value: str) -> bool:
    try:
        return int(value) == 0
    except Exception:
        return False
