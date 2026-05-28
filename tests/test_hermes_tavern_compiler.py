"""Tests for PromptCompiler."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.importers.cards import CharacterCard
from plugins.hermes_tavern.macros import MacroContext
from plugins.hermes_tavern.prompt import CompiledContext, PromptCompiler, PromptModule


def _card(**kwargs) -> CharacterCard:
    defaults = dict(id="test-id", name="TestChar")
    defaults.update(kwargs)
    return CharacterCard(**defaults)


def test_compile_system_prompt_override():
    card = _card(system_prompt_override="You are Aria.", description="Fallback desc.")
    ctx = PromptCompiler().compile(card, [], "hi")
    assert isinstance(ctx, CompiledContext)
    assert ctx.modules[0].content == "You are Aria."
    assert ctx.modules[0].role == "system"


def test_compile_falls_back_to_description():
    card = _card(system_prompt_override="", description="A helpful bot.")
    ctx = PromptCompiler().compile(card, [], "hello")
    assert ctx.modules[0].content == "A helpful bot."


def test_compile_no_system_module_when_both_empty():
    card = _card(system_prompt_override="", description="")
    ctx = PromptCompiler().compile(card, [], "hi")
    assert ctx.modules == []


def test_compile_user_message_preserved():
    card = _card()
    ctx = PromptCompiler().compile(card, [], "hi there")
    assert ctx.user_message == "hi there"
    assert ctx.card_name == "TestChar"


def test_compile_token_budget_positive():
    card = _card(description="Some description text.")
    ctx = PromptCompiler().compile(card, [{"role": "user", "content": "hello"}], "world")
    assert ctx.token_budget > 0


def test_compile_preset_modules_appended_in_order():
    card = _card(description="Sys.")
    presets = [
        PromptModule(name="b", role="system", content="B", position="after_char", insertion_order=2),
        PromptModule(name="a", role="system", content="A", position="after_char", insertion_order=1),
    ]
    ctx = PromptCompiler().compile(card, [], "", preset_modules=presets)
    names = [m.name for m in ctx.modules]
    assert names == ["char_system", "a", "b"]


def test_compile_disabled_preset_excluded():
    card = _card(description="Sys.")
    presets = [
        PromptModule(name="on", role="system", content="On", position="after_char", enabled=True),
        PromptModule(name="off", role="system", content="Off", position="after_char", enabled=False),
    ]
    ctx = PromptCompiler().compile(card, [], "", preset_modules=presets)
    assert all(m.name != "off" for m in ctx.modules)


def test_compile_expands_macros_across_all_prompt_surfaces():
    card = _card(description="Card {{char}} sees {{user}}.")
    modules = [
        PromptModule(
            name="preset",
            role="system",
            content="Preset {{content_mode}} {{session_title}}.",
            position="before_char",
            insertion_order=1,
        ),
        PromptModule(
            name="lore",
            role="system",
            content="Lore for {{char}}.",
            position="before_char",
            insertion_order=2,
        ),
        PromptModule(
            name="memory",
            role="system",
            content="Memory about {{user}}.",
            position="before_char",
            insertion_order=3,
        ),
    ]
    history = [{"role": "assistant", "content": "Hello {{user}}."}]
    macro_context = MacroContext(
        char_name="TestChar",
        user_name="Morgan",
        session_title="Chapter One",
        content_mode="adult-fiction",
    )

    ctx = PromptCompiler().compile(
        card,
        history,
        "Current {{char}} to {{user}}.",
        preset_modules=modules,
        macro_context=macro_context,
    )

    assert ctx.modules[0].content == "Card TestChar sees Morgan."
    assert ctx.modules[1].content == "Preset adult-fiction Chapter One."
    assert ctx.modules[2].content == "Lore for TestChar."
    assert ctx.modules[3].content == "Memory about Morgan."
    assert ctx.history[0]["content"] == "Hello Morgan."
    assert ctx.user_message == "Current TestChar to Morgan."


def test_compile_without_macro_context_uses_safe_defaults():
    card = _card(description="Hello {{char}} and {{user}} in {{content_mode}}.")

    ctx = PromptCompiler().compile(card, [], "Ping {{session_title}}.")

    assert ctx.modules[0].content == "Hello TestChar and User in safe."
    assert ctx.user_message == "Ping ."
