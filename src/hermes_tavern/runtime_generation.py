"""Hermes Tavern generation adapter boundary."""

from __future__ import annotations

from typing import Any

from plugins.hermes_tavern.adapters import HermesChatCompletionAdapter
from plugins.hermes_tavern.provider_bridge import HermesRuntimeProviderResolver


def generate_with_session_adapter(
    runtime: Any,
    session: dict[str, Any],
    messages: list[dict[str, Any]],
    descriptor: Any,
    fake_adapter: Any,
) -> str:
    adapter_mode = session.get("adapter_mode") or "fake"
    if adapter_mode != "hermes":
        return fake_adapter.generate(messages, descriptor)

    if not int(session.get("live_confirmed") or 0):
        return (
            "[Hermes Tavern hermes provider mode is selected, but live generation is off. "
            "Run /rp model live confirm to enable real provider calls for this session.]"
        )

    adapter = runtime.hermes_adapter
    if adapter is None:
        adapter = HermesChatCompletionAdapter(
            HermesRuntimeProviderResolver(descriptor).resolve
        )
        runtime.hermes_adapter = adapter
    try:
        return adapter.generate(messages, descriptor)
    except (ConnectionError, TimeoutError):
        return "[Hermes Tavern: provider unavailable — /rp retry to try again]"
    except NotImplementedError:
        return (
            "[Hermes Tavern hermes provider mode is selected, "
            "but real generation is not wired yet. /rp retry after setup.]"
        )
    except Exception:
        return "[Hermes Tavern: provider error — check /rp model status]"
