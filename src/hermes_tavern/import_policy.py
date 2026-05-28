"""Import path trust policy for Hermes Tavern gateway and local commands."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


@dataclass(frozen=True)
class ImportPathDecision:
    value: Path | str | None
    error: str | None = None


def is_local_media_path(value: str) -> bool:
    parsed = urlparse(value)
    return not parsed.scheme and not parsed.netloc


def is_gateway_event(event: Any) -> bool:
    """Return True for events that carry a messaging-platform identity.

    Unit tests and trusted local callers may pass small event-like objects with
    no attachment surface. Those are treated as local/trusted so existing
    CLI-style explicit path imports continue to work. Gateway attachment import
    policy applies when the event exposes ``media_urls``.
    """
    if not hasattr(event, "media_urls"):
        return False
    try:
        source = getattr(event, "source", None)
    except Exception:
        source = None
    if source is not None:
        platform = getattr(source, "platform", None)
        chat_id = getattr(source, "chat_id", None)
        user_id = getattr(source, "user_id", None)
        return any(value not in (None, "") for value in (platform, chat_id, user_id))
    platform = getattr(event, "platform", None)
    chat_id = getattr(event, "chat_id", None)
    user_id = getattr(event, "user_id", None)
    return any(value not in (None, "") for value in (platform, chat_id, user_id))


def _attachment_paths(event: Any, suffixes: set[str]) -> list[str]:
    media_urls = getattr(event, "media_urls", None) or []
    return [
        str(media_url)
        for media_url in media_urls
        if is_local_media_path(str(media_url))
        and Path(str(media_url)).suffix.lower() in suffixes
    ]


def _normalized_local_path(value: str) -> Path | None:
    if not is_local_media_path(value):
        return None
    try:
        return Path(value).expanduser().resolve(strict=False)
    except (OSError, RuntimeError, ValueError):
        return None


def resolve_import_path(
    event: Any,
    explicit_value: str | None,
    *,
    label: str,
    suffixes: set[str],
    usage: str,
    attach_tip: str,
    allow_remote_urls: bool = False,
) -> ImportPathDecision:
    """Resolve an import target under gateway-safe trust rules.

    Gateway events may import exactly one local attachment without an explicit
    path. Explicit gateway paths are accepted only when they normalize to a
    local attachment path from the same event. Trusted local callers keep
    existing explicit path/URL behavior.
    """
    importable = _attachment_paths(event, suffixes)
    if explicit_value is None or not explicit_value.strip():
        if not importable:
            return ImportPathDecision(
                None,
                f"{usage}\nTip: attach {attach_tip} and send /rp {label} import",
            )
        if len(importable) > 1:
            lines = [f"Multiple {label} attachments found:"]
            for idx, path in enumerate(importable[:8], start=1):
                lines.append(f"{idx}. {Path(path).name}")
            if len(importable) > 8:
                lines.append(f"... {len(importable) - 8} more")
            lines.append(f"Specify one explicitly: /rp {label} import <file>")
            return ImportPathDecision(None, "\n".join(lines))
        return ImportPathDecision(Path(importable[0]).expanduser())

    explicit = explicit_value.strip()
    if not is_gateway_event(event):
        if allow_remote_urls and not is_local_media_path(explicit):
            return ImportPathDecision(explicit)
        return ImportPathDecision(Path(explicit).expanduser())

    explicit_path = _normalized_local_path(explicit)
    if explicit_path is None or explicit_path.suffix.lower() not in suffixes:
        return ImportPathDecision(None, f"{label.capitalize()} import rejected: attach the file to this message first.")

    attachment_paths = {
        normalized
        for item in importable
        if (normalized := _normalized_local_path(item)) is not None
    }
    if explicit_path not in attachment_paths:
        return ImportPathDecision(None, f"{label.capitalize()} import rejected: attach the file to this message first.")
    return ImportPathDecision(Path(explicit).expanduser())
