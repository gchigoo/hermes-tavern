"""Tests for Hermes Tavern gateway dispatch hook."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.gateway_hook import pre_gateway_dispatch
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.runtime import TavernRuntime


class FakeAdapter:
    """Simulates a gateway platform adapter for tests."""

    def __init__(self):
        self.sent: list[tuple[str, str]] = []

    def send(self, chat_id, content):
        self.sent.append((str(chat_id), str(content)))


class FakeSource:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class FakeGateway:
    def __init__(self):
        self.adapters = {"telegram": FakeAdapter()}


class FakeEvent:
    source = FakeSource()
    text = ""


def _make_event(text: str = "") -> FakeEvent:
    event = FakeEvent()
    event.text = text
    return event


def _make_store(path) -> TavernStore:
    store = TavernStore(str(path))
    store.migrate()
    return store


def test_pre_gateway_dispatch_rp_command_skips(tmp_path):
    """pre_gateway_dispatch intercepts /rp commands and returns skip."""
    result = pre_gateway_dispatch(
        event=_make_event("/rp help"),
        gateway=FakeGateway(),
        store=_make_store(tmp_path / "tavern.sqlite3"),
    )
    assert result["action"] == "skip"
    assert result["reason"] == "hermes-tavern"


def test_pre_gateway_dispatch_non_rp_without_active_session_allows(tmp_path):
    """Non-/rp messages without active session fall through to normal Hermes."""
    result = pre_gateway_dispatch(
        event=_make_event("hello"),
        gateway=FakeGateway(),
        store=_make_store(tmp_path / "tavern.sqlite3"),
    )
    assert result["action"] == "allow"


def test_pre_gateway_dispatch_active_session_routes_message(tmp_path):
    """Non-/rp messages in active session route to handle_active_message_sync."""
    store = _make_store(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(
        RPCommand("start", ["Alice"], "/rp start Alice"),
        _make_event(),
    )

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    assert session is not None

    gateway = FakeGateway()
    result = pre_gateway_dispatch(
        event=_make_event("Hi Alice, how are you?"),
        gateway=gateway,
        store=store,
    )

    assert result["action"] == "skip"
    assert result["reason"] == "hermes-tavern"


def test_pre_gateway_dispatch_pause_resume_controls_active_routing(tmp_path):
    store = _make_store(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(
        RPCommand("start", ["Alice"], "/rp start Alice"),
        _make_event(),
    )
    gateway = FakeGateway()

    paused = pre_gateway_dispatch(
        event=_make_event("/rp pause"),
        gateway=gateway,
        store=store,
    )
    assert paused == {"action": "skip", "reason": "hermes-tavern"}
    assert "paused" in gateway.adapters["telegram"].sent[-1][1]

    status = pre_gateway_dispatch(
        event=_make_event("/rp status"),
        gateway=gateway,
        store=store,
    )
    assert status == {"action": "skip", "reason": "hermes-tavern"}
    assert "Use /rp resume" in gateway.adapters["telegram"].sent[-1][1]

    normal = pre_gateway_dispatch(
        event=_make_event("this should be normal Hermes"),
        gateway=gateway,
        store=store,
    )
    assert normal == {"action": "allow"}

    resumed = pre_gateway_dispatch(
        event=_make_event("/rp resume"),
        gateway=gateway,
        store=store,
    )
    assert resumed == {"action": "skip", "reason": "hermes-tavern"}
    assert "resumed" in gateway.adapters["telegram"].sent[-1][1]

    routed = pre_gateway_dispatch(
        event=_make_event("back in roleplay"),
        gateway=gateway,
        store=store,
    )
    assert routed == {"action": "skip", "reason": "hermes-tavern"}


def test_pre_gateway_dispatch_no_event_allows(tmp_path):
    """Missing event falls through."""
    result = pre_gateway_dispatch(gateway=FakeGateway(), store=_make_store(tmp_path / "tavern.sqlite3"))
    assert result["action"] == "allow"


def test_pre_gateway_dispatch_empty_text_with_active_session(tmp_path):
    """Empty-text messages with active session still route (fallback to allow if no reply)."""
    store = _make_store(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(
        RPCommand("start", ["Alice"], "/rp start Alice"),
        _make_event(),
    )

    result = pre_gateway_dispatch(
        event=_make_event(""),
        gateway=FakeGateway(),
        store=store,
    )
    # Empty text still triggers RP turn (runs _run_generation_pipeline with empty user text)
    assert result["action"] == "skip"
    assert result["reason"] == "hermes-tavern"
