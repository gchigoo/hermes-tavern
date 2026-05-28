"""Gateway hook entry points for Hermes Tavern."""

from __future__ import annotations

import asyncio
import inspect
import logging
from typing import Any

log = logging.getLogger(__name__)

from plugins.hermes_tavern.commands import parse_rp_command
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.runtime import TavernRuntime


def _platform_key(platform: Any) -> Any:
    return getattr(platform, "value", platform)


def _get_adapter(gateway: Any, event: Any) -> Any:
    if gateway is None:
        return None
    adapters = getattr(gateway, "adapters", {}) or {}
    source = getattr(event, "source", None)
    raw_platform = getattr(source, "platform", None)
    platform = _platform_key(raw_platform)
    return adapters.get(platform) or adapters.get(raw_platform)


def _send_if_possible(gateway: Any, event: Any, content: str) -> None:
    adapter = _get_adapter(gateway, event)
    if adapter is None or not hasattr(adapter, "send"):
        return

    chat_id = getattr(getattr(event, "source", None), "chat_id", None)
    if not chat_id:
        return

    send_content = content
    deliver_media = getattr(gateway, "_deliver_media_from_response", None)
    if deliver_media is not None and hasattr(adapter, "extract_media"):
        try:
            media_files, cleaned = adapter.extract_media(content)
            if media_files:
                send_content = cleaned
        except Exception:
            log.debug("hermes-tavern: failed to strip MEDIA tags", exc_info=True)

    result = None
    if send_content.strip():
        result = adapter.send(chat_id, send_content)
    if not inspect.isawaitable(result):
        result = None

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        if result is not None:
            asyncio.run(result)
        _deliver_media_sync(deliver_media, content, event, adapter)
    else:
        if result is not None:
            loop.create_task(result)
        _schedule_media_delivery(loop, deliver_media, content, event, adapter)


def _schedule_media_delivery(
    loop: asyncio.AbstractEventLoop,
    deliver_media: Any,
    content: str,
    event: Any,
    adapter: Any,
) -> None:
    if deliver_media is None or "MEDIA:" not in content:
        return
    try:
        media_result = deliver_media(content, event, adapter)
    except Exception:
        log.debug("hermes-tavern: media delivery failed before scheduling", exc_info=True)
        return
    if inspect.isawaitable(media_result):
        loop.create_task(media_result)


def _deliver_media_sync(deliver_media: Any, content: str, event: Any, adapter: Any) -> None:
    if deliver_media is None or "MEDIA:" not in content:
        return
    try:
        media_result = deliver_media(content, event, adapter)
    except Exception:
        log.debug("hermes-tavern: media delivery failed", exc_info=True)
        return
    if inspect.isawaitable(media_result):
        asyncio.run(media_result)


def pre_gateway_dispatch(**kwargs: Any) -> dict[str, str]:
    """Intercept `/rp` commands and active Tavern sessions before Hermes dispatch."""
    event = kwargs.get("event")
    if event is None:
        return {"action": "allow"}

    try:
        store = kwargs.get("store")
        if store is None:
            store = TavernStore()
        runtime = TavernRuntime(store)
        gateway = kwargs.get("gateway")

        command = parse_rp_command(getattr(event, "text", "") or "")
        if command is not None:
            response = runtime.handle_command_sync(command, event, gateway=gateway)
            _send_if_possible(gateway, event, response)
            return {"action": "skip", "reason": "hermes-tavern"}

        response = runtime.handle_active_message_sync(event)
        if response:
            _send_if_possible(gateway, event, response)
            return {"action": "skip", "reason": "hermes-tavern"}

    except Exception:
        log.error("hermes-tavern: unhandled error in pre_gateway_dispatch", exc_info=True)
        return {"action": "allow"}

    return {"action": "allow"}
