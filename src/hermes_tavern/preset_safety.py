"""Risk classification for imported Tavern preset/prompt modules.

This module intentionally does not store jailbreak text.  It classifies prompt
modules so importers/runtime can disable risky modules by default while still
preserving useful structure such as writing style controls and prompt ordering.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import re


class PresetRiskLevel(str, Enum):
    SAFE = "safe"
    ADULT_FICTION = "adult_fiction"
    JAILBREAK = "jailbreak"
    DISALLOWED = "disallowed"


@dataclass(frozen=True)
class PresetSafetyReport:
    level: PresetRiskLevel
    reasons: tuple[str, ...] = field(default_factory=tuple)
    enable_by_default: bool = True


_JAILBREAK_PATTERNS: tuple[tuple[str, str], ...] = (
    ("ignore", "ignore/override safety or system instruction language"),
    ("discard conflicting", "context-discarding jailbreak language"),
    ("no disclaimers", "disclaimer suppression"),
    ("no warnings", "warning suppression"),
    ("no content boundaries", "no-boundaries policy override"),
    ("unconditionally", "unconditional compliance framing"),
    ("flagged", "flagged-content override language"),
    ("ethics", "anti-ethics framing"),
    ("jailbreak", "explicit jailbreak marker"),
    ("破限", "explicit Chinese jailbreak marker"),
)

_DISALLOWED_PATTERNS: tuple[tuple[str, str], ...] = (
    ("bestiality", "sexual content involving animals"),
    ("non-con", "sexual non-consent framing"),
    ("rape", "sexual violence framing"),
    ("incest", "incest sexual-content framing"),
    ("celebrities", "sexualized real-person/celebrity framing"),
    ("no content boundaries", "no-boundaries attempt to remove all content boundaries"),
)

_MINOR_TERMS = (
    r"\bminor\b",
    r"\bunder[- ]?age\b",
    r"\bunderage\b",
    r"\bteen(?:ager)?\b",
    r"\bkids?\b",
    r"\bchild(?:ren)?\b",
    r"\byoung[- ]?looking\b",
    r"\bpreteen\b",
)
_MINOR_SEXUAL_MARKERS = (
    " sexual ",
    " sexually ",
    "sexuality",
    "sexualized",
    "sex",
    "erotic",
    "smut",
    "dirty",
    "flirty",
    "intimate",
    "intimacy",
    "kissing",
    "kiss",
    "porn",
    "breast",
    "naked",
    "nude",
    "seduce",
    "seduc",
)

_ADULT_FICTION_PATTERNS: tuple[tuple[str, str], ...] = (
    ("adult", "adult fiction marker"),
    ("erotic", "erotic writing marker"),
    ("smut", "explicit adult-fiction writing marker"),
    ("dirty", "explicit adult-fiction writing marker"),
    ("flirty", "flirty roleplay marker"),
)


def classify_preset_text(text: str) -> PresetSafetyReport:
    """Classify a preset/prompt module and decide whether it should auto-enable.

    The classifier is intentionally conservative.  It is not a content policy
    engine; it is an import/runtime guard that stops ST-style jailbreak modules
    from becoming active system prompts in Hermes Tavern by accident.
    """

    lowered = text.lower()
    reasons: list[str] = []
    minor_term_matches = [pattern for pattern in _MINOR_TERMS if re.search(pattern, lowered)]
    if minor_term_matches and any(marker in lowered for marker in _MINOR_SEXUAL_MARKERS):
        reasons.append("sexualized minor framing")
        return PresetSafetyReport(
            level=PresetRiskLevel.DISALLOWED,
            reasons=tuple(dict.fromkeys(reasons)),
            enable_by_default=False,
        )

    for pattern, reason in _DISALLOWED_PATTERNS:
        if pattern in lowered:
            reasons.append(reason)
    if reasons:
        return PresetSafetyReport(
            level=PresetRiskLevel.DISALLOWED,
            reasons=tuple(dict.fromkeys(reasons)),
            enable_by_default=False,
        )

    for pattern, reason in _JAILBREAK_PATTERNS:
        if pattern in lowered:
            reasons.append(reason)
    if reasons:
        return PresetSafetyReport(
            level=PresetRiskLevel.JAILBREAK,
            reasons=tuple(dict.fromkeys(reasons)),
            enable_by_default=False,
        )

    for pattern, reason in _ADULT_FICTION_PATTERNS:
        if pattern in lowered:
            reasons.append(reason)
    if reasons:
        return PresetSafetyReport(
            level=PresetRiskLevel.ADULT_FICTION,
            reasons=tuple(dict.fromkeys(reasons)),
            enable_by_default=True,
        )

    return PresetSafetyReport(level=PresetRiskLevel.SAFE)


def safe_import_note(report: PresetSafetyReport) -> str:
    if report.level == PresetRiskLevel.SAFE:
        return "Preset module appears safe for default enablement."
    if report.level == PresetRiskLevel.ADULT_FICTION:
        return "Adult-fiction module: allowed for consenting-adult fictional workflows; keep session content mode explicit."
    if report.level == PresetRiskLevel.JAILBREAK:
        return "Jailbreak-like module: imported metadata may be retained, but module must be disabled by default."
    return "Disallowed/no-boundaries module: do not enable as a Tavern system prompt."
