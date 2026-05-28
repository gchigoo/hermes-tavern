"""Prompt renderers for Hermes Tavern."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from plugins.hermes_tavern.prompt import CompiledContext


class ChatRenderer:
    """Render a CompiledContext as an ordered list of role/content message dicts."""

    def render(self, ctx: "CompiledContext") -> list[dict[str, str]]:
        messages: list[dict[str, str]] = []

        for module in ctx.modules:
            messages.append({"role": module.role, "content": module.content})

        for turn in ctx.history:
            messages.append({"role": turn["role"], "content": turn["content"]})

        if ctx.user_message:
            messages.append({"role": "user", "content": ctx.user_message})

        return messages


class StoryStringRenderer:
    """Stub renderer — concatenates all content into a single prose string."""

    def render(self, ctx: "CompiledContext") -> str:
        parts: list[str] = []

        for module in ctx.modules:
            parts.append(f"[{module.role.upper()}] {module.content}")

        for turn in ctx.history:
            parts.append(f"[{turn['role'].upper()}] {turn['content']}")

        if ctx.user_message:
            parts.append(f"[USER] {ctx.user_message}")

        return "\n\n".join(parts)
