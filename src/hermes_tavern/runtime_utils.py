"""Shared helpers for Hermes Tavern runtime command modules."""

from __future__ import annotations

import json
from typing import Any

from plugins.hermes_tavern.macros import MacroContext


def mobile_preview(text: str, limit: int = 120) -> str:
    """Single-line preview that stays readable in narrow mobile chat apps."""
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 1)].rstrip() + "…"


def usable_module_counts(modules: list[dict[str, Any]], content_mode: str) -> dict[str, int]:
    counts = {"safe": 0, "adult_fiction": 0, "disabled_risky": 0}
    for module in modules:
        raw = json.loads(module.get("raw_json") or "{}")
        risk = raw.get("risk_level", "safe")
        if risk in {"jailbreak", "disallowed"} or not module.get("enabled"):
            if risk in {"jailbreak", "disallowed"}:
                counts["disabled_risky"] += 1
            continue
        if risk == "safe":
            counts["safe"] += 1
        elif risk == "adult_fiction" and content_mode == "adult-fiction":
            counts["adult_fiction"] += 1
    return counts


def module_risk_counts_db(modules: list[dict[str, Any]]) -> dict[str, int]:
    """Aggregate risk counts from DB module rows (enabled/disabled breakdown)."""
    counts = {"safe": 0, "adult_fiction": 0, "risky_disabled": 0}
    for module in modules:
        raw = json.loads(module.get("raw_json") or "{}")
        risk = raw.get("risk_level", "safe")
        if risk in {"jailbreak", "disallowed"}:
            counts["risky_disabled"] += 1
        elif module.get("enabled"):
            if risk == "safe":
                counts["safe"] += 1
            elif risk == "adult_fiction":
                counts["adult_fiction"] += 1
    return counts


def module_risk_counts(modules: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for module in modules:
        risk = getattr(module, "risk_level", "safe")
        counts[risk] = counts.get(risk, 0) + 1
    return counts


def card_row_to_obj(card_row: dict[str, Any]) -> Any:
    """Reconstruct a minimal CharacterCard-like object from a DB row."""
    from plugins.hermes_tavern.importers.cards import CharacterCard

    data = json.loads(card_row["data_json"])
    return CharacterCard(
        id=card_row["id"],
        name=card_row["name"],
        description=data.get("description", ""),
        personality=data.get("personality", ""),
        scenario=data.get("scenario", ""),
        first_mes=data.get("first_mes", ""),
        mes_example=data.get("mes_example", ""),
        alternate_greetings=data.get("alternate_greetings", []),
        creator_notes=data.get("creator_notes", ""),
        system_prompt_override=data.get("system_prompt_override", ""),
        post_history_instructions=data.get("post_history_instructions", ""),
        tags=data.get("tags", []),
        talkativeness=data.get("talkativeness"),
        extensions=data.get("extensions", {}),
        source_path=data.get("source_path", ""),
        raw=data.get("raw", {}),
    )


def build_macro_context(card: Any, session: dict[str, Any], event: Any = None) -> MacroContext:
    return MacroContext(
        char_name=safe_macro_value(getattr(card, "name", "") or session.get("card_name") or ""),
        user_name=event_user_name(event),
        session_title=safe_macro_value(session.get("title") or ""),
        content_mode=safe_macro_value(session.get("content_mode") or "safe") or "safe",
    )


def event_user_name(event: Any) -> str:
    for attr in ("user_name", "sender_name", "username", "user_id"):
        value = getattr(event, attr, None)
        safe = safe_macro_value(value)
        if safe:
            return safe
    source = getattr(event, "source", None)
    for attr in ("user_name", "sender_name", "username", "user_id"):
        value = getattr(source, attr, None)
        safe = safe_macro_value(value)
        if safe:
            return safe
    return "User"


def safe_macro_value(value: Any, *, limit: int = 120) -> str:
    text = " ".join(str(value or "").split())
    if len(text) > limit:
        return text[:limit].rstrip()
    return text
