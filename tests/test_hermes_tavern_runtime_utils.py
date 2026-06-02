"""Direct unit tests for hermes_tavern.runtime_utils.

Covers all eight public helpers: mobile_preview, safe_macro_value,
event_user_name, usable_module_counts, module_risk_counts_db,
module_risk_counts, build_macro_context, card_row_to_obj.
"""

from __future__ import annotations

import json
import types

import pytest

from hermes_tavern.runtime_utils import (
    build_macro_context,
    card_row_to_obj,
    event_user_name,
    mobile_preview,
    module_risk_counts,
    module_risk_counts_db,
    safe_macro_value,
    usable_module_counts,
)
from hermes_tavern.macros import MacroContext


# ---------------------------------------------------------------------------
# mobile_preview
# ---------------------------------------------------------------------------

class TestMobilePreview:
    def test_empty_string(self):
        assert mobile_preview("") == ""

    def test_short_string_unchanged(self):
        assert mobile_preview("hello world") == "hello world"

    def test_exact_limit_not_truncated(self):
        text = "a" * 120
        assert mobile_preview(text, limit=120) == text

    def test_over_limit_truncated_with_ellipsis(self):
        text = "a" * 130
        result = mobile_preview(text, limit=120)
        assert result.endswith("…")
        assert len(result) == 120

    def test_multiline_collapses_to_single_line(self):
        result = mobile_preview("hello\nworld\nfoo")
        assert "\n" not in result
        assert result == "hello world foo"

    def test_excess_spaces_collapsed(self):
        result = mobile_preview("  hello   world  ")
        assert result == "hello world"

    def test_none_treated_as_empty(self):
        assert mobile_preview(None) == ""  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# safe_macro_value
# ---------------------------------------------------------------------------

class TestSafeMacroValue:
    def test_none_returns_empty(self):
        assert safe_macro_value(None) == ""

    def test_empty_string_returns_empty(self):
        assert safe_macro_value("") == ""

    def test_short_string_unchanged(self):
        assert safe_macro_value("Alice") == "Alice"

    def test_long_string_truncated_at_limit(self):
        text = "x" * 200
        result = safe_macro_value(text, limit=120)
        assert len(result) == 120

    def test_multiline_collapses(self):
        result = safe_macro_value("hello\nworld")
        assert "\n" not in result
        assert result == "hello world"

    def test_trailing_space_removed_at_truncation_boundary(self):
        # Build a string where the 120th char is a space — should not end with space.
        text = "a" * 119 + " " + "b" * 81
        result = safe_macro_value(text, limit=120)
        assert not result.endswith(" ")


# ---------------------------------------------------------------------------
# event_user_name
# ---------------------------------------------------------------------------

class TestEventUserName:
    def test_user_name_attr_returned(self):
        event = types.SimpleNamespace(user_name="Alice")
        assert event_user_name(event) == "Alice"

    def test_sender_name_fallback(self):
        event = types.SimpleNamespace(sender_name="Bob")
        assert event_user_name(event) == "Bob"

    def test_user_name_takes_priority_over_sender_name(self):
        event = types.SimpleNamespace(user_name="Alice", sender_name="Bob")
        assert event_user_name(event) == "Alice"

    def test_source_user_name_fallback(self):
        source = types.SimpleNamespace(user_name="Carol")
        event = types.SimpleNamespace(source=source)
        assert event_user_name(event) == "Carol"

    def test_no_user_attrs_returns_user(self):
        event = types.SimpleNamespace()
        assert event_user_name(event) == "User"

    def test_none_user_name_falls_back_to_next(self):
        event = types.SimpleNamespace(user_name=None, sender_name="Dave")
        assert event_user_name(event) == "Dave"

    def test_empty_user_name_falls_back_to_next(self):
        event = types.SimpleNamespace(user_name="", sender_name="Eve")
        assert event_user_name(event) == "Eve"


# ---------------------------------------------------------------------------
# usable_module_counts
# ---------------------------------------------------------------------------

def _make_db_module(risk: str, enabled: bool = True) -> dict:
    return {"raw_json": json.dumps({"risk_level": risk}), "enabled": enabled}


class TestUsableModuleCounts:
    def test_empty_list_all_zeros(self):
        counts = usable_module_counts([], "safe")
        assert counts == {"safe": 0, "adult_fiction": 0, "disabled_risky": 0}

    def test_safe_enabled_counted(self):
        counts = usable_module_counts([_make_db_module("safe")], "safe")
        assert counts["safe"] == 1

    def test_adult_fiction_in_safe_mode_not_counted(self):
        counts = usable_module_counts([_make_db_module("adult_fiction")], "safe")
        assert counts["adult_fiction"] == 0
        assert counts["safe"] == 0

    def test_adult_fiction_in_adult_fiction_mode_counted(self):
        counts = usable_module_counts([_make_db_module("adult_fiction")], "adult-fiction")
        assert counts["adult_fiction"] == 1

    def test_jailbreak_goes_to_disabled_risky(self):
        counts = usable_module_counts([_make_db_module("jailbreak")], "adult-fiction")
        assert counts["disabled_risky"] == 1
        assert counts["adult_fiction"] == 0

    def test_disallowed_goes_to_disabled_risky(self):
        counts = usable_module_counts([_make_db_module("disallowed")], "safe")
        assert counts["disabled_risky"] == 1

    def test_disabled_safe_module_not_counted(self):
        counts = usable_module_counts([_make_db_module("safe", enabled=False)], "safe")
        assert counts["safe"] == 0
        assert counts["disabled_risky"] == 0


# ---------------------------------------------------------------------------
# module_risk_counts_db
# ---------------------------------------------------------------------------

class TestModuleRiskCountsDb:
    def test_empty_list_all_zeros(self):
        counts = module_risk_counts_db([])
        assert counts == {"safe": 0, "adult_fiction": 0, "risky_disabled": 0}

    def test_safe_enabled_counted(self):
        counts = module_risk_counts_db([_make_db_module("safe")])
        assert counts["safe"] == 1

    def test_adult_fiction_enabled_counted(self):
        counts = module_risk_counts_db([_make_db_module("adult_fiction")])
        assert counts["adult_fiction"] == 1

    def test_jailbreak_goes_to_risky_disabled(self):
        counts = module_risk_counts_db([_make_db_module("jailbreak")])
        assert counts["risky_disabled"] == 1

    def test_adult_fiction_disabled_not_counted(self):
        counts = module_risk_counts_db([_make_db_module("adult_fiction", enabled=False)])
        assert counts["adult_fiction"] == 0
        assert counts["risky_disabled"] == 0


# ---------------------------------------------------------------------------
# module_risk_counts
# ---------------------------------------------------------------------------

def _make_module_obj(risk: str):
    return types.SimpleNamespace(risk_level=risk)


class TestModuleRiskCounts:
    def test_empty_list_returns_empty_dict(self):
        assert module_risk_counts([]) == {}

    def test_single_module_counted(self):
        counts = module_risk_counts([_make_module_obj("safe")])
        assert counts == {"safe": 1}

    def test_mixed_risks_counted_correctly(self):
        modules = [
            _make_module_obj("safe"),
            _make_module_obj("safe"),
            _make_module_obj("adult_fiction"),
        ]
        counts = module_risk_counts(modules)
        assert counts == {"safe": 2, "adult_fiction": 1}

    def test_missing_risk_level_defaults_to_safe(self):
        module = types.SimpleNamespace()  # no risk_level attr
        counts = module_risk_counts([module])
        assert counts == {"safe": 1}


# ---------------------------------------------------------------------------
# build_macro_context
# ---------------------------------------------------------------------------

class TestBuildMacroContext:
    def _make_card(self, name: str = "Aria"):
        return types.SimpleNamespace(name=name)

    def test_returns_macro_context_instance(self):
        ctx = build_macro_context(self._make_card(), {"content_mode": "safe"}, None)
        assert isinstance(ctx, MacroContext)

    def test_char_name_from_card(self):
        ctx = build_macro_context(self._make_card("Luna"), {"content_mode": "safe"}, None)
        assert ctx.char_name == "Luna"

    def test_content_mode_from_session(self):
        ctx = build_macro_context(self._make_card(), {"content_mode": "adult-fiction"}, None)
        assert ctx.content_mode == "adult-fiction"

    def test_user_name_from_event(self):
        event = types.SimpleNamespace(user_name="Alice")
        ctx = build_macro_context(self._make_card(), {"content_mode": "safe"}, event)
        assert ctx.user_name == "Alice"

    def test_user_name_defaults_to_user_without_event(self):
        ctx = build_macro_context(self._make_card(), {"content_mode": "safe"}, None)
        assert ctx.user_name == "User"


# ---------------------------------------------------------------------------
# card_row_to_obj
# ---------------------------------------------------------------------------

def _make_card_row(name: str = "Aria", extra_data: dict | None = None) -> dict:
    data = {
        "description": "A test character",
        "personality": "Curious",
        "scenario": "A tavern",
        "first_mes": "Hello!",
        "mes_example": "",
        "tags": ["fantasy"],
    }
    if extra_data:
        data.update(extra_data)
    return {"id": "test-card-id-001", "name": name, "data_json": json.dumps(data)}


class TestCardRowToObj:
    def test_returns_character_card(self):
        from hermes_tavern.importers.cards import CharacterCard
        card = card_row_to_obj(_make_card_row())
        assert isinstance(card, CharacterCard)

    def test_name_and_id_preserved(self):
        card = card_row_to_obj(_make_card_row("Mira"))
        assert card.name == "Mira"
        assert card.id == "test-card-id-001"

    def test_data_fields_extracted(self):
        card = card_row_to_obj(_make_card_row())
        assert card.description == "A test character"
        assert card.tags == ["fantasy"]
        assert card.first_mes == "Hello!"
