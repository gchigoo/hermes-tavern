"""Tests for Hermes Tavern prompt renderers."""

from __future__ import annotations

from plugins.hermes_tavern.prompt import CompiledContext, PromptModule
from plugins.hermes_tavern.renderers import ChatRenderer, StoryStringRenderer


def _ctx() -> CompiledContext:
    return CompiledContext(
        modules=[PromptModule("sys", "system", "System prompt.", "before_char")],
        history=[
            {"role": "assistant", "content": "Hello."},
            {"role": "user", "content": "Hi."},
        ],
        user_message="What happens next?",
        card_name="Alice",
        token_budget=12,
    )


def test_chat_renderer_orders_system_history_user_message():
    messages = ChatRenderer().render(_ctx())

    assert messages == [
        {"role": "system", "content": "System prompt."},
        {"role": "assistant", "content": "Hello."},
        {"role": "user", "content": "Hi."},
        {"role": "user", "content": "What happens next?"},
    ]


def test_story_string_renderer_returns_non_empty_string():
    rendered = StoryStringRenderer().render(_ctx())

    assert isinstance(rendered, str)
    assert "[SYSTEM] System prompt." in rendered
    assert "[USER] What happens next?" in rendered
