"""Tests for Hermes Tavern ST-style macro expansion."""

from __future__ import annotations

from datetime import datetime

from plugins.hermes_tavern.macros import MacroContext, expand_macros


def _ctx(**kwargs) -> MacroContext:
    defaults = dict(
        char_name="Alice",
        user_name="Steven",
        session_title="Library Run",
        content_mode="safe",
        now=datetime(2026, 5, 20, 9, 8),
    )
    defaults.update(kwargs)
    return MacroContext(**defaults)


def test_expand_basic_macros_deterministically():
    text = (
        "{{char}}/{{user}}/{{time}}/{{date}}/{{datetime}}/"
        "{{weekday}}/{{content_mode}}/{{session_title}}"
    )

    assert expand_macros(text, _ctx()) == (
        "Alice/Steven/09:08/2026-05-20/2026-05-20 09:08/"
        "Wednesday/safe/Library Run"
    )


def test_expand_tolerates_case_and_whitespace():
    assert expand_macros("{{ Char }} + {{USER}} + {{ Content_Mode }}", _ctx()) == (
        "Alice + Steven + safe"
    )


def test_unknown_macros_are_preserved():
    assert expand_macros("{{char}} {{unknown_macro}}", _ctx()) == "Alice {{unknown_macro}}"


def test_expansion_is_one_pass_not_recursive():
    text = "{{char}}"
    context = _ctx(char_name="{{user}}")

    assert expand_macros(text, context) == "{{user}}"


def test_execution_looking_text_is_inert_and_preserved():
    text = "{{__import__('os').system('touch should_not_exist')}} {{char}}"

    assert expand_macros(text, _ctx()) == (
        "{{__import__('os').system('touch should_not_exist')}} Alice"
    )
