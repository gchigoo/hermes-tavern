"""Template-only SillyTavern macro expansion for Hermes Tavern."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime


_MACRO_PATTERN = re.compile(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}")


@dataclass(frozen=True)
class MacroContext:
    char_name: str = ""
    user_name: str = "User"
    session_title: str = ""
    content_mode: str = "safe"
    now: datetime | None = None


def expand_macros(text: str, context: MacroContext) -> str:
    """Expand a finite allowlist of ST-style template macros.

    This is deliberately one-pass and non-recursive. Unknown macros remain
    byte-for-byte unchanged, and replacement values are treated as inert text.
    """

    if not text:
        return text

    now = context.now or datetime.now()
    replacements = {
        "char": context.char_name,
        "user": context.user_name or "User",
        "time": now.strftime("%H:%M"),
        "date": now.strftime("%Y-%m-%d"),
        "datetime": now.strftime("%Y-%m-%d %H:%M"),
        "weekday": now.strftime("%A"),
        "content_mode": context.content_mode or "safe",
        "session_title": context.session_title,
    }

    def replace(match: re.Match[str]) -> str:
        key = match.group(1).strip().lower()
        if key not in replacements:
            return match.group(0)
        return replacements[key]

    return _MACRO_PATTERN.sub(replace, text)
