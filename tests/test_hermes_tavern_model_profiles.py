"""Tests for Hermes Tavern model profile persistence."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.model_router import ModelRouter


def test_save_list_get_model_profile_secret_free(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    profile_id = store.save_model_profile(
        profile_id="opus-default",
        name="Opus 4.6 Default",
        provider="anthropic",
        model_id="claude-opus-4-6",
        raw={"content_mode": "novel"},
    )

    assert profile_id == "opus-default"
    profiles = store.list_model_profiles()
    assert len(profiles) == 1
    assert profiles[0]["provider"] == "anthropic"
    assert store.get_model_profile("Opus 4.6 Default")["id"] == "opus-default"


def test_model_profile_rejects_secret_fields(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    with pytest.raises(ValueError):
        store.save_model_profile(
            name="bad",
            provider="anthropic",
            model_id="claude-opus-4-6",
            raw={"api_key": "should-not-persist"},
        )


def test_model_router_uses_session_bound_profile(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    profile_id = store.save_model_profile(
        profile_id="custom-opus",
        name="Custom Opus",
        provider="openrouter",
        model_id="anthropic/claude-opus-4-6",
    )
    session = store.start_session("telegram:chat:1:thread:main:user:1")
    assert store.set_session_model_profile("telegram:chat:1:thread:main:user:1", profile_id)
    session = store.get_active_session("telegram:chat:1:thread:main:user:1")

    descriptor = ModelRouter().resolve(session_row=session, store=store)

    assert descriptor.source == "db_profile"
    assert descriptor.provider == "openrouter"
    assert descriptor.model_id == "anthropic/claude-opus-4-6"
    assert descriptor.profile_name == "Custom Opus"
