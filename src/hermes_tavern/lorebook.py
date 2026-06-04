"""Lorebook matching and prompt-module conversion for Hermes Tavern."""

from __future__ import annotations

import json
import random
import re
from dataclasses import dataclass, field
from typing import Any

from hermes_tavern.prompt import PromptModule
from hermes_tavern.utils import estimate_tokens


_NESTED_QUANTIFIER_RE = re.compile(
    r"\([^()]*?(?:\{\s*\d+\s*(?:,\s*\d*)?\s*\}|[+*?])\s*\)\s*(?:[+*?]|\{\s*\d+\s*(?:,\s*\d*)?\s*\})"
)
_MAX_REGEX_KEY_LENGTH = 256


@dataclass(frozen=True)
class LoreMatch:
    entry_id: str
    title: str
    matched: bool
    reason: str
    module: PromptModule | None = None


@dataclass(frozen=True)
class LoreMatchResult:
    matches: tuple[LoreMatch, ...]
    excluded: tuple[LoreMatch, ...]
    token_budget: int = 0
    debug: tuple[str, ...] = field(default_factory=tuple)


def match_lorebook_entries(
    entries: list[dict[str, Any]],
    text: str,
    *,
    history_text: str = "",
    token_budget: int = 1200,
    rng: random.Random | None = None,
) -> LoreMatchResult:
    """Match lorebook entries against current message/history.

    This v1 matcher is deterministic by default except entries with probability
    strictly between 0 and 1, where an injectable RNG is used. Bad regex entries
    are excluded with debug reasons instead of raising.
    """
    rng = rng or random.Random(0)
    haystack = f"{history_text}\n{text}".strip()
    haystack_lower = haystack.lower()
    candidates: list[tuple[dict[str, Any], str]] = []
    excluded: list[LoreMatch] = []

    for row in entries:
        entry_id = str(row.get("id") or "")
        title = str(row.get("title") or entry_id or "untitled")
        content = str(row.get("content") or "")
        if not row.get("enabled", True):
            excluded.append(LoreMatch(entry_id, title, False, "disabled"))
            continue
        if not content.strip():
            excluded.append(LoreMatch(entry_id, title, False, "empty content"))
            continue
        probability = _float(row.get("probability"), 1.0)
        if probability <= 0:
            excluded.append(LoreMatch(entry_id, title, False, "probability=0"))
            continue
        if probability < 1 and rng.random() > probability:
            excluded.append(LoreMatch(entry_id, title, False, f"probability miss ({probability:g})"))
            continue
        matched, reason = _entry_matches(row, haystack, haystack_lower)
        if matched:
            candidates.append((row, reason))
        else:
            excluded.append(LoreMatch(entry_id, title, False, reason))

    candidates.sort(
        key=lambda item: (
            -_int(item[0].get("priority"), 0),
            _int(item[0].get("insertion_order"), 0),
            str(item[0].get("title") or ""),
        )
    )

    matches: list[LoreMatch] = []
    used_tokens = 0
    for row, reason in candidates:
        entry_id = str(row.get("id") or "")
        title = str(row.get("title") or entry_id or "untitled")
        content = str(row.get("content") or "")
        cost = estimate_tokens(content)
        if used_tokens + cost > token_budget:
            excluded.append(LoreMatch(entry_id, title, False, "token budget exceeded"))
            continue
        used_tokens += cost
        matches.append(
            LoreMatch(
                entry_id,
                title,
                True,
                reason,
                PromptModule(
                    name=f"lore:{title}",
                    role="system",
                    content=content,
                    position=str(row.get("position") or "before_char"),
                    insertion_order=_int(row.get("insertion_order"), 0),
                    enabled=True,
                ),
            )
        )

    debug = tuple(
        [f"matched {m.title}: {m.reason}" for m in matches]
        + [f"excluded {m.title}: {m.reason}" for m in excluded]
    )
    return LoreMatchResult(tuple(matches), tuple(excluded), used_tokens, debug)


def modules_from_lore_matches(result: LoreMatchResult) -> list[PromptModule]:
    return [match.module for match in result.matches if match.module is not None]


def _entry_matches(row: dict[str, Any], haystack: str, haystack_lower: str) -> tuple[bool, str]:
    if row.get("constant"):
        return True, "constant"
    keys = _keys(row.get("keys_json") or row.get("keys"))
    secondary = _keys(row.get("secondary_keys_json") or row.get("secondary_keys"))
    if not keys:
        return False, "no keys"
    regex = bool(row.get("regex"))
    primary_hit = _any_key_matches(keys, haystack, haystack_lower, regex)
    if primary_hit.startswith(("regex error", "regex rejected")):
        return False, primary_hit
    if not primary_hit:
        return False, "no primary key match"
    if secondary:
        secondary_hit = _any_key_matches(secondary, haystack, haystack_lower, regex)
        if secondary_hit.startswith(("regex error", "regex rejected")):
            return False, secondary_hit
        if not secondary_hit:
            return False, "secondary key filter miss"
    return True, f"key match: {primary_hit}"


def _any_key_matches(keys: tuple[str, ...], haystack: str, haystack_lower: str, regex: bool) -> str:
    for key in keys:
        if regex:
            if len(key) > _MAX_REGEX_KEY_LENGTH:
                return "regex rejected: pattern too long"
            if _NESTED_QUANTIFIER_RE.search(key):
                return "regex rejected: nested quantifier"
            try:
                if re.search(key, haystack, flags=re.IGNORECASE):
                    return key
            except re.error as exc:
                return f"regex error: {exc}"
        elif key.lower() in haystack_lower:
            return key
    return ""


def _keys(value: Any) -> tuple[str, ...]:
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return (value,) if value.strip() else ()
        return _keys(parsed)
    if isinstance(value, list):
        return tuple(str(item) for item in value if str(item).strip())
    if isinstance(value, tuple):
        return tuple(str(item) for item in value if str(item).strip())
    return ()


def _int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
