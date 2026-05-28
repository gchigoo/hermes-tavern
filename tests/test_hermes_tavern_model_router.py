"""Tests for ModelRouter and ModelProfileDescriptor."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.model_router import ModelProfileDescriptor, ModelRouter


def test_resolve_no_session_returns_anthropic_opus():
    d = ModelRouter().resolve()
    assert d.provider == "anthropic"
    assert d.model_id == "claude-opus-4-6"
    assert d.source.startswith("default")


def test_resolve_session_row_without_profile_id_returns_default():
    d = ModelRouter().resolve(session_row={"id": "s1", "card_id": "c1"}, store=None)
    assert d.provider == "anthropic"
    assert d.source.startswith("default")


def test_descriptor_has_no_secret_fields():
    d = ModelRouter().resolve()
    assert not hasattr(d, "api_key")
    assert not hasattr(d, "access_token")
    assert not hasattr(d, "secret")


def test_descriptor_is_frozen():
    d = ModelRouter().resolve()
    with pytest.raises((AttributeError, TypeError)):
        d.provider = "other"  # type: ignore[misc]


def test_descriptor_mode_and_context_window():
    d = ModelRouter().resolve()
    assert d.mode == "chat"
    assert d.context_window > 0
