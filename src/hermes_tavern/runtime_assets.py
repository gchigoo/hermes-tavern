"""Asset and character-card commands for Hermes Tavern runtime."""

from __future__ import annotations

import json
import math
from types import SimpleNamespace
from typing import Any
from pathlib import Path

from hermes_tavern.commands import RPCommand
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.import_policy import is_gateway_event, resolve_import_path
from hermes_tavern.importers.cards import UnsupportedCardFormat, load_card_file
from hermes_tavern.importers.lorebooks import import_embedded_lorebook_from_card
from hermes_tavern.runtime_utils import mobile_preview


def assets(runtime: Any, event: Any) -> str:
    """Mobile-sized asset dashboard for Telegram/Feishu entry points."""
    cards = runtime.store.list_cards()
    presets = runtime.store.list_presets()
    lorebooks = runtime.store.list_lorebooks()
    session = runtime.store.get_active_session(session_key_from_event(event))

    lines = ["Hermes Tavern assets"]
    lines.append(f"cards: {len(cards)}")
    lines.append(f"presets: {len(presets)}")
    lines.append(f"lorebooks: {len(lorebooks)}")
    if session is None:
        lines.append("active session: none")
    else:
        lines.append(f"active card: {session.get('card_name') or 'none'}")
        preset_name = "none"
        if session.get("preset_id"):
            preset = runtime.store.get_preset(session["preset_id"])
            preset_name = (preset or {}).get("name", session["preset_id"])
        lorebook_name = "none"
        if session.get("lorebook_id"):
            lorebook = runtime.store.get_lorebook(session["lorebook_id"])
            lorebook_name = (lorebook or {}).get("name", session["lorebook_id"])
        lines.append(f"active preset: {preset_name}")
        lines.append(f"active lorebook: {lorebook_name}")
    lines.append("next: /rp cards | /rp preset list | /rp lore list")
    return "\n".join(lines)


def cards(runtime: Any, command: RPCommand) -> str:
    limit = 10
    page = 1
    if command.args:
        try:
            limit = max(1, min(50, int(command.args[0])))
        except ValueError:
            return "Usage: /rp cards [limit] [page]"
        if len(command.args) >= 2:
            try:
                page = max(1, int(command.args[1]))
            except ValueError:
                return "Usage: /rp cards [limit] [page]"
    all_cards = runtime.store.list_cards()
    total = len(all_cards)
    if total == 0:
        return "No Hermes Tavern character cards imported."
    total_pages = max(1, math.ceil(total / limit))
    page = min(page, total_pages)
    slice_start = (page - 1) * limit
    page_cards = all_cards[slice_start : slice_start + limit]
    lines = [f"Hermes Tavern cards (page {page}/{total_pages}, {len(page_cards)} shown):"]
    for row in page_cards:
        data = json.loads(row.get("data_json") or "{}")
        tags = data.get("tags") or []
        tag_text = ", ".join(str(tag) for tag in tags[:4]) or "no tags"
        desc = mobile_preview(data.get("description") or data.get("personality") or "", 56)
        lines.append(f"  [{row['id'][:8]}] {row['name']} — {tag_text}")
        if desc:
            lines.append(f"    {desc}")
        lines.append(f"    start: /rp start {row['name']}")
        lines.append(f"    inspect: /rp card inspect {row['name']}")
    if page > 1:
        lines.append(f"prev: /rp cards {limit} {page - 1}")
    if page < total_pages:
        lines.append(f"next: /rp cards {limit} {page + 1}")
    return "\n".join(lines)


_IMPORTABLE_CARD_SUFFIXES = {".json", ".png"}


def _card_not_found(ref: str) -> str:
    if ref.strip().lower() == "last":
        return "No card has been imported yet. Import a card first: /rp card import <file>"
    return f"Character card not found: {ref}"


def card_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "inspect"
    if subcommand == "import":
        return card_import(runtime, command, event)
    if subcommand == "search":
        return card_search(runtime, command)
    if subcommand == "inspect":
        return runtime._card_inspect(command)
    if subcommand in {"use", "bind"}:
        return runtime._card_use(command, event)
    return "Usage: /rp card import <file> | /rp card search <query> | /rp card inspect <card> | /rp card use <card>"


def card_import(runtime: Any, command: RPCommand, event: Any) -> str:
    explicit_value = " ".join(command.args[1:]) if len(command.args) >= 2 else None
    decision = resolve_import_path(
        event,
        explicit_value,
        label="card",
        suffixes=_IMPORTABLE_CARD_SUFFIXES,
        usage="Usage: /rp card import <file.json|file.png>",
        attach_tip="a .json or .png SillyTavern character card",
        allow_remote_urls=True,
    )
    if decision.error:
        return decision.error
    path = decision.value
    try:
        card = load_card_file(path)
    except UnsupportedCardFormat as exc:
        return str(exc)
    except FileNotFoundError:
        display_path = Path(str(path)).name if is_gateway_event(event) else path
        return f"Card file not found: {display_path}"
    except ValueError as exc:
        return f"Could not import card: {exc}"
    card_id = runtime.store.save_card(card)
    runtime.store.set_last_card(card_id)
    short_id = card_id[:8]
    lines = [
        f"Imported card: {card.name}",
        f"id: {card_id}",
    ]
    embedded_lorebook = import_embedded_lorebook_from_card(card)
    if embedded_lorebook is not None:
        lorebook_id = runtime.store.save_lorebook(embedded_lorebook)
        lines.append(
            f"embedded lorebook: {embedded_lorebook.name} ({lorebook_id[:8]}), {len(embedded_lorebook.entries)} entries"
        )
        lines.append(f"lore: /rp lore inspect {lorebook_id[:8]} | /rp lore use {lorebook_id[:8]}")
    lines.append(f"inspect: /rp card inspect {short_id}")
    lines.append(f"use: /rp card use {short_id}")
    lines.append(f"start: /rp start {short_id}")
    return "\n".join(lines)


def card_search(runtime: Any, command: RPCommand) -> str:
    query = " ".join(command.args[1:]).strip()
    if not query:
        return "Usage: /rp card search <query>"
    terms = [term.lower() for term in query.split() if term.strip()]
    matches: list[tuple[int, dict[str, Any], dict[str, Any]]] = []
    for row in runtime.store.list_cards():
        data = json.loads(row.get("data_json") or "{}")
        haystack_parts = [
            row.get("name") or "",
            data.get("description") or "",
            data.get("personality") or "",
            data.get("scenario") or "",
            " ".join(str(tag) for tag in (data.get("tags") or [])),
        ]
        haystack = "\n".join(haystack_parts).lower()
        if not all(term in haystack for term in terms):
            continue
        name = str(row.get("name") or "").lower()
        tags = " ".join(str(tag).lower() for tag in (data.get("tags") or []))
        score = 0
        if query.lower() == name:
            score += 100
        if any(term in name for term in terms):
            score += 30
        if any(term in tags for term in terms):
            score += 20
        score += min(10, sum(haystack.count(term) for term in terms))
        matches.append((score, row, data))

    if not matches:
        return f"No Hermes Tavern character cards matched: {query}"

    matches.sort(key=lambda item: (-item[0], str(item[1].get("name") or "")))
    shown = matches[:10]
    lines = [f"Hermes Tavern card search: {query} ({len(matches)} matched, {len(shown)} shown)"]
    for _, row, data in shown:
        tags = data.get("tags") or []
        tag_text = ", ".join(str(tag) for tag in tags[:4]) or "no tags"
        desc = mobile_preview(
            data.get("description") or data.get("personality") or data.get("scenario") or "",
            72,
        )
        lines.append(f"  [{row['id'][:8]}] {row['name']} — {tag_text}")
        if desc:
            lines.append(f"    {desc}")
        lines.append(f"    start: /rp start {row['id'][:8]}")
        lines.append(f"    inspect: /rp card inspect {row['id'][:8]}")
    return "\n".join(lines)


def card_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp card inspect <card>"
    card_ref = " ".join(command.args[1:]).strip()
    card = runtime.store.get_card(card_ref)
    if card is None:
        return _card_not_found(card_ref)
    data = json.loads(card.get("data_json") or "{}")
    tags = data.get("tags") or []
    lines = [f"Card: {card['name']} ({card['id'][:8]})"]
    lines.append(f"tags: {', '.join(str(tag) for tag in tags) if tags else 'none'}")
    for key in ("description", "personality", "scenario"):
        value = mobile_preview(data.get(key) or "", 220)
        if value:
            lines.append(f"{key}: {value}")
    lines.append(f"first message: {'yes' if data.get('first_mes') else 'none'}")
    lines.append(f"alternate greetings: {len(data.get('alternate_greetings') or [])}")
    lines.append(f"system prompt override: {'yes' if data.get('system_prompt_override') else 'none'}")
    lines.append(f"post-history instructions: {'yes' if data.get('post_history_instructions') else 'none'}")
    embedded = _embedded_lorebook_from_stored_card(card, data)
    if embedded is not None:
        lorebook_id = runtime.store.save_lorebook(embedded)
        lines.append(f"embedded lorebook: {embedded.name} ({lorebook_id[:8]}), {len(embedded.entries)} entries")
        lines.append(f"lore inspect: /rp lore inspect {lorebook_id[:8]}")
    else:
        lines.append("embedded lorebook: none")
    lines.append(f"start: /rp start {card['name']}")
    lines.append(f"bind active: /rp card use {card['name']}")
    return "\n".join(lines)


def _embedded_lorebook_from_stored_card(card: dict[str, Any], data: dict[str, Any]) -> Any | None:
    raw = data.get("raw") if isinstance(data.get("raw"), dict) else None
    if raw is None:
        return None
    card_obj = SimpleNamespace(id=card.get("id"), name=card.get("name"), raw=raw)
    return import_embedded_lorebook_from_card(card_obj)


def card_use(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp card use <card>"
    card_ref = " ".join(command.args[1:]).strip()
    card = runtime.store.get_card(card_ref)
    if card is None:
        return _card_not_found(card_ref)
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key)
    if session is None:
        return "No active Hermes Tavern session. Start one with /rp start <card>."
    if not runtime.store.set_session_card(session_key, card["id"]):
        return "Could not bind card to active session."
    data = json.loads(card.get("data_json") or "{}")
    greeting = data.get("first_mes") or ""
    if greeting:
        runtime.store.append_message(session["id"], "assistant", greeting)
    lines = [f"Hermes Tavern card bound: {card['name']} ({card['id'][:8]})"]
    if greeting:
        lines.append(greeting)
    lines.append("history preserved; use /rp history to inspect the branch.")
    return "\n".join(lines)
