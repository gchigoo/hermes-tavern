"""Shared helpers for Hermes Tavern runtime command modules."""

from __future__ import annotations

import json
from typing import Any

from hermes_tavern.macros import MacroContext


USABLE_MODULE_RISKS = frozenset({"safe", "adult_fiction"})
KNOWN_MODULE_RISKS = USABLE_MODULE_RISKS | {"jailbreak", "disallowed"}
INVALID_MODULE_RISK = "invalid"
_INVALID_MODULE_RISK_REASON = "missing or invalid risk metadata"


def mobile_preview(text: str, limit: int = 120) -> str:
    """Single-line preview that stays readable in narrow mobile chat apps."""
    compact = " ".join(str(text or "").split())
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 1)].rstrip() + "…"


def parse_pagination(
    args: list[str],
    *,
    default_limit: int,
    max_limit: int,
) -> tuple[int, int] | None:
    """Parse `[limit] [page]` from command args.

    Returns `(limit, page)` on success and `None` on parse failure.
    Keeps behavior consistent with existing command parsers:
    - `limit` is clamped to `[1, max_limit]`
    - `page` defaults to 1 and clamps to at least 1
    - extra args are ignored
    """
    limit = default_limit
    page = 1
    if args:
        try:
            limit = max(1, min(max_limit, int(args[0])))
        except ValueError:
            return None
    if len(args) > 1:
        try:
            page = max(1, int(args[1]))
        except ValueError:
            return None
    return limit, page


def _module_raw_object(module: dict[str, Any]) -> dict[str, Any] | None:
    raw_json = module.get("raw_json")
    if isinstance(raw_json, dict):
        return raw_json
    if not isinstance(raw_json, str):
        return None
    try:
        parsed = json.loads(raw_json)
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    return parsed if isinstance(parsed, dict) else None


def module_risk_details(module: dict[str, Any]) -> tuple[str, list[str]]:
    """Read validated prompt-module risk metadata, failing closed on corruption."""
    raw = _module_raw_object(module)
    if raw is None:
        return INVALID_MODULE_RISK, [_INVALID_MODULE_RISK_REASON]

    risk = raw.get("risk_level")
    if not isinstance(risk, str) or risk not in KNOWN_MODULE_RISKS:
        return INVALID_MODULE_RISK, [_INVALID_MODULE_RISK_REASON]

    reasons = raw.get("risk_reasons") or []
    if not isinstance(reasons, list):
        reasons = [reasons]
    return risk, [str(reason) for reason in reasons]


def usable_module_counts(modules: list[dict[str, Any]], content_mode: str) -> dict[str, int]:
    counts = {"safe": 0, "adult_fiction": 0, "disabled_risky": 0}
    for module in modules:
        risk, _ = module_risk_details(module)
        if risk not in USABLE_MODULE_RISKS or not module.get("enabled"):
            if risk not in USABLE_MODULE_RISKS:
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
        risk, _ = module_risk_details(module)
        if risk not in USABLE_MODULE_RISKS:
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
    from hermes_tavern.importers.cards import CharacterCard

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
