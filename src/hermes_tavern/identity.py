"""Session identity helpers for Hermes Tavern gateway events."""

from __future__ import annotations

from typing import Any


def _safe_attr(obj: Any, name: str, default: str = "unknown") -> str:
    try:
        value = getattr(obj, name, None)
    except Exception:
        return default
    if value is None or value == "":
        return default
    if hasattr(value, "value"):
        value = value.value
    return str(value)


def session_key_from_event(event: Any) -> str:
    """Build a deterministic Tavern session key from a gateway event."""
    try:
        source = getattr(event, "source", event)
    except Exception:
        source = event
    platform = _safe_attr(source, "platform")
    chat_id = _safe_attr(source, "chat_id")
    thread_id = (
        _safe_attr(source, "thread_id", "")
        or _safe_attr(source, "topic_id", "")
        or "main"
    )
    user_id = _safe_attr(source, "user_id")
    return f"{platform}:chat:{chat_id}:thread:{thread_id}:user:{user_id}"
