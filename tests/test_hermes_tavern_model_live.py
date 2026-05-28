"""Tests for Hermes Tavern model live routing and adapter caching."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.adapters import FAKE_ADAPTER_REPLY, HermesChatCompletionAdapter
from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.runtime import TavernRuntime
from plugins.hermes_tavern import runtime_model


class FakeSource:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class FakeEvent:
    source = FakeSource()
    text = ""


class _FakeCompletions:
    def __init__(self):
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return {"choices": [{"message": {"content": "live reply from fake client"}}]}


class _FakeChat:
    def __init__(self):
        self.completions = _FakeCompletions()


class _FakeOpenAIClient:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.chat = _FakeChat()


def test_model_live_confirm_caches_hermes_adapter(tmp_path):
    """_model_live confirm sets hermes_adapter on the runtime instance."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), FakeEvent())

    assert runtime.hermes_adapter is None

    response = runtime.handle_command_sync(RPCommand("model", ["live", "confirm"], "/rp model live confirm"), FakeEvent())
    assert "ENABLED" in response

    assert runtime.hermes_adapter is not None
    assert isinstance(runtime.hermes_adapter, HermesChatCompletionAdapter)


def test_model_live_cached_adapter_generates(tmp_path):
    """Cached adapter from live confirm generates replies."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), FakeEvent())

    created = []

    def factory(**kwargs):
        client = _FakeOpenAIClient(**kwargs)
        created.append(client)
        return client

    runtime.handle_command_sync(RPCommand("model", ["live", "confirm"], "/rp model live confirm"), FakeEvent())
    runtime.hermes_adapter._client_factory = factory

    reply = runtime.handle_command_sync(RPCommand("say", ["Hello"], "/rp say Hello"), FakeEvent())
    assert reply == "live reply from fake client"
    assert len(created) == 1


def test_model_live_without_confirm_blocks_real_calls(tmp_path):
    """When mode is hermes but live is not confirmed, returns instruction message."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), FakeEvent())

    reply = runtime.handle_command_sync(RPCommand("say", ["Hello"], "/rp say Hello"), FakeEvent())
    assert "live generation is off" in reply
    assert "/rp model live confirm" in reply


def test_model_live_fake_mode_uses_fake_adapter(tmp_path):
    """Fake mode still uses the deterministic fake adapter regardless of live setting."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    reply = runtime.handle_command_sync(RPCommand("say", ["Hello"], "/rp say Hello"), FakeEvent())

    assert reply == FAKE_ADAPTER_REPLY


def test_model_live_status_reports_state(tmp_path):
    """_model_live status reports enabled/disabled correctly."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), FakeEvent())

    status = runtime.handle_command_sync(RPCommand("model", ["live", "status"], "/rp model live status"), FakeEvent())
    assert "enabled: False" in status.lower() or "false" in status.lower()

    runtime.handle_command_sync(RPCommand("model", ["live", "confirm"], "/rp model live confirm"), FakeEvent())
    status = runtime.handle_command_sync(RPCommand("model", ["live", "status"], "/rp model live status"), FakeEvent())
    assert "true" in status.lower() or "enabled: true" in status.lower()


def test_model_status_sanitizes_debug_descriptor_recursively(tmp_path, monkeypatch):
    class _Descriptor:
        def to_debug_dict(self):
            return {
                "profile_name": "unsafe-debug",
                "provider": "anthropic",
                "model_id": "claude-opus-4-6",
                "mode": "chat",
                "source": "test",
                "API_KEY": "fake-api-key-do-not-persist",
                "nested": {"Access_Token": "fake-access-token-do-not-persist"},
            }

    class _Router:
        def resolve(self, session_row=None, store=None):
            return _Descriptor()

    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    monkeypatch.setattr(runtime_model, "_router", _Router())

    status = runtime.handle_command_sync(RPCommand("model", ["status"], "/rp model status"), FakeEvent())

    assert "provider: anthropic" in status
    assert "model_id: claude-opus-4-6" in status
    assert "fake-" not in status
    assert "API_KEY" not in status
    assert "Access_Token" not in status


def test_model_live_off_disables(tmp_path):
    """_model_live off disables live mode."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), FakeEvent())

    runtime.handle_command_sync(RPCommand("model", ["live", "confirm"], "/rp model live confirm"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["live", "off"], "/rp model live off"), FakeEvent())

    reply = runtime.handle_command_sync(RPCommand("say", ["Hello"], "/rp say Hello"), FakeEvent())
    assert "live generation is off" in reply


# ---------------------------------------------------------------------------
# Live memory summarization
# ---------------------------------------------------------------------------

def test_memory_summarize_live_without_hermes_mode_warns(tmp_path):
    """summarize live with fake adapter mode returns guidance."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())

    response = runtime.handle_command_sync(
        RPCommand("memory", ["summary", "summarize", "live"], "/rp memory summary summarize live"),
        FakeEvent(),
    )
    assert "hermes adapter mode" in response


def test_memory_summarize_live_hermes_no_confirm_warns(tmp_path):
    """summarize live with hermes mode but no confirm returns guidance."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), FakeEvent())

    response = runtime.handle_command_sync(
        RPCommand("memory", ["summary", "summarize", "live"], "/rp memory summary summarize live"),
        FakeEvent(),
    )
    assert "hermes adapter mode" in response


def test_memory_summarize_live_with_cached_adapter(tmp_path):
    """summarize live with hermes + live confirmed + fake client."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())
    runtime.handle_command_sync(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), FakeEvent())

    class _FakeComp:
        def __init__(self):
            self.calls = []
        def create(self, **kwargs):
            self.calls.append(kwargs)
            return {"choices": [{"message": {"content": "Alice greeted the user. They discussed the weather."}}]}

    class _FakeCh:
        def __init__(self):
            self.completions = _FakeComp()

    class _FakeClient:
        def __init__(self, **kwargs):
            self.chat = _FakeCh()

    def factory(**kwargs):
        return _FakeClient(**kwargs)

    runtime.handle_command_sync(RPCommand("model", ["live", "confirm"], "/rp model live confirm"), FakeEvent())
    runtime.hermes_adapter._client_factory = factory

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.append_message(session["id"], "user", "Hi Alice!")
    store.append_message(session["id"], "assistant", "Hello there!")
    store.append_message(session["id"], "user", "What a nice day.")
    store.append_message(session["id"], "assistant", "Indeed! Shall we walk?")

    response = runtime.handle_command_sync(
        RPCommand("memory", ["summary", "summarize", "live"], "/rp memory summary summarize live"),
        FakeEvent(),
    )
    assert "live summary saved" in response
    assert "Alice greeted" in response

    saved = store.get_session_summary("telegram:chat:chat-1:thread:main:user:user-1")
    assert saved is not None
    assert "Alice greeted" in saved["summary"]


def test_memory_summarize_deterministic_without_live(tmp_path):
    """Plain summarize (no live flag) still works deterministically."""
    store = TavernStore(str(tmp_path / "tavern.sqlite3"))
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), FakeEvent())

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.append_message(session["id"], "user", "Hi!")
    store.append_message(session["id"], "assistant", "Hey!")

    response = runtime.handle_command_sync(
        RPCommand("memory", ["summary", "summarize", "5"], "/rp memory summary summarize 5"),
        FakeEvent(),
    )
    assert "deterministic summary saved" in response
    assert "Hi!" in response
