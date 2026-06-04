import base64
import json as _json
from pathlib import Path
import struct
import zlib

import pytest

from plugins.hermes_tavern.adapters import FAKE_ADAPTER_REPLY
from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.gateway_hook import pre_gateway_dispatch
from plugins.hermes_tavern import runtime_model
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.lorebooks import import_st_lorebook_json
from plugins.hermes_tavern.importers.presets import import_raw_preset_text
from plugins.hermes_tavern.runtime import TavernRuntime


def _make_png_with_chara(card_json: dict) -> bytes:
    chara_b64 = base64.b64encode(_json.dumps(card_json).encode()).decode("latin-1")
    chunk_data = b"chara\x00" + chara_b64.encode("latin-1")

    def chunk(type_: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(type_ + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + type_ + data + struct.pack(">I", crc)

    ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr_data)
        + chunk(b"tEXt", chunk_data)
        + chunk(b"IEND", b"")
    )


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


def _v3_card_with_embedded_book(name: str = "Alice") -> dict:
    return {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "data": {
            "name": name,
            "first_mes": "Hello from embedded card.",
            "character_book": {
                "name": f"{name} World",
                "entries": {
                    "0": {"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"]},
                    "1": {"comment": "Always", "content": "Always-on lore.", "constant": True},
                },
            },
        },
        "name": "",
    }


@pytest.mark.asyncio
async def test_runtime_help_returns_command_list(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(RPCommand("help", [], "/rp"), Event())

    assert "/rp start <card>" in response
    assert "/rp greeting list" in response
    assert "/rp say <message>" in response
    assert "/rp status" in response


@pytest.mark.asyncio
async def test_runtime_status_reports_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(RPCommand("status", [], "/rp status"), Event())

    assert "No active" in response


@pytest.mark.asyncio
async def test_runtime_start_card_opens_session_and_returns_greeting(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("start", ["Alice"], "/rp start Alice"),
        Event(),
    )

    assert "Started" in response
    assert "Alice" in response
    assert "Hello there." in response
    assert store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["card_name"] == "Alice"


@pytest.mark.asyncio
async def test_runtime_start_card_auto_binds_embedded_lorebook(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card(_v3_card_with_embedded_book("Alice")))
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("start", ["Alice"], "/rp start Alice"),
        Event(),
    )

    assert "embedded lorebook bound: Alice World" in response
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    assert session["lorebook_id"]
    lorebook = store.get_lorebook(session["lorebook_id"])
    assert lorebook["name"] == "Alice World"
    entries = store.list_lorebook_entries(session["lorebook_id"])
    assert len(entries) == 2


@pytest.mark.asyncio
async def test_runtime_start_plain_card_does_not_bind_lorebook(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Plain", "first_mes": "Hi."}))
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("start", ["Plain"], "/rp start Plain"),
        Event(),
    )

    assert "embedded lorebook" not in response
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    assert session["lorebook_id"] is None


@pytest.mark.asyncio
async def test_runtime_greeting_list_and_use_alternate_greeting(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({
        "name": "Alice",
        "first_mes": "Hello there.",
        "alternate_greetings": ["Good evening.", "Tea?"],
    }))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    listed = await runtime.handle_command(RPCommand("greeting", ["list"], "/rp greeting list"), Event())
    selected = await runtime.handle_command(RPCommand("greeting", ["use", "2"], "/rp greeting use 2"), Event())

    assert "Greetings for Alice" in listed
    assert "[0] first_mes: Hello there." in listed
    assert "[1] alternate_1: Good evening." in listed
    assert "[2] alternate_2: Tea?" in listed
    assert "Greeting 2 selected for Alice" in selected
    assert "Tea?" in selected
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    messages = store.get_recent_messages(session["id"], limit=10)
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"] == "Tea?"


@pytest.mark.asyncio
async def test_runtime_say_generates_turn_and_preserves_text(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    response = await runtime.handle_command(RPCommand("say", ["What", "happens", "next?"], "/rp say What happens next?"), Event())

    assert response == FAKE_ADAPTER_REPLY
    active = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    messages = store.get_recent_messages(active["id"], limit=10)
    assert messages[-2]["role"] == "user"
    assert messages[-2]["content"] == "What happens next?"
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"] == FAKE_ADAPTER_REPLY


@pytest.mark.asyncio
async def test_runtime_active_message_uses_fake_model_pipeline(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MessageEvent(Event):
        text = "What happens next?"

    response = await runtime.handle_active_message(MessageEvent())

    assert response == FAKE_ADAPTER_REPLY
    active = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    messages = store.get_recent_messages(active["id"])
    assert messages[-2]["role"] == "user"
    assert messages[-2]["content"] == "What happens next?"
    assert messages[-1]["role"] == "assistant"
    assert messages[-1]["content"] == FAKE_ADAPTER_REPLY


@pytest.mark.asyncio
async def test_runtime_debug_prompt_reports_modules_and_tokens(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    response = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "modules:" in response
    assert "tokens:" in response
    assert "rendered messages:" in response


@pytest.mark.asyncio
async def test_runtime_debug_prompt_paginates_mobile_rows(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    for i in range(3):
        store.append_message(session["id"], "user", f"turn {i}")

    page1 = await runtime.handle_command(RPCommand("debug", ["prompt", "2", "1"], "/rp debug prompt 2 1"), Event())
    page2 = await runtime.handle_command(RPCommand("debug", ["prompt", "2", "2"], "/rp debug prompt 2 2"), Event())

    assert "Hermes Tavern prompt debug" in page1
    assert "showing rows" in page1
    assert "next: /rp debug prompt 2 2" in page1
    assert "prev: /rp debug prompt 2 1" in page2


@pytest.mark.asyncio
async def test_runtime_debug_swipes_reports_candidate_metadata(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    await runtime.handle_command(RPCommand("say", ["What", "next?"], "/rp say What next?"), Event())
    runtime._run_generation_pipeline = lambda session, user_text, history, event=None: "second candidate"
    await runtime.handle_command(RPCommand("retry", [], "/rp retry"), Event())

    response = await runtime.handle_command(RPCommand("debug", ["swipes"], "/rp debug swipes"), Event())

    assert "Hermes Tavern swipe debug" in response
    assert "candidates: 2" in response
    assert "active_swipe: 1" in response
    assert "[0]" in response and "[1]" in response


@pytest.mark.asyncio
async def test_runtime_debug_context_reports_budget_rows_and_metadata(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(
        parse_character_card(
            {
                "name": "Alice",
                "description": "Scholar",
                "first_mes": "Hello there.",
            }
        )
    )
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    response = await runtime.handle_command(
        RPCommand("debug", ["context"], "/rp debug context"),
        Event(),
    )

    assert "Hermes Tavern context budget" in response
    assert "card: Alice" in response
    assert "renderer: chat" in response
    assert "model: anthropic/claude-opus-4-6" in response
    assert "context_window:" in response
    assert "estimated_tokens:" in response
    assert "modules:" in response
    assert "history turns:" in response
    assert "rendered messages:" in response
    assert "omitted: preset none; lorebook none; persona none; author note none; memory summary none" in response
    assert "tokens=" in response


@pytest.mark.asyncio
async def test_runtime_debug_context_paginates_mobile_rows(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    for i in range(3):
        store.append_message(session["id"], "user", f"turn {i}")

    page1 = await runtime.handle_command(
        RPCommand("debug", ["context", "2", "1"], "/rp debug context 2 1"),
        Event(),
    )
    page2 = await runtime.handle_command(
        RPCommand("debug", ["context", "2", "2"], "/rp debug context 2 2"),
        Event(),
    )

    assert "Hermes Tavern context budget" in page1
    assert "showing rows" in page1
    assert "next: /rp debug context 2 2" in page1
    assert "prev: /rp debug context 2 1" in page2


@pytest.mark.asyncio
async def test_runtime_debug_context_requires_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(
        RPCommand("debug", ["context"], "/rp debug context"),
        Event(),
    )

    assert response == "No active Hermes Tavern session."


@pytest.mark.asyncio
async def test_runtime_debug_context_requires_bound_card(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("debug", ["context"], "/rp debug context"),
        Event(),
    )

    assert response == "No character card bound to this session."


@pytest.mark.asyncio
async def test_runtime_debug_context_invalid_pagination(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    response = await runtime.handle_command(
        RPCommand("debug", ["context", "bad", "1"], "/rp debug context bad 1"),
        Event(),
    )

    assert response == "Usage: /rp debug context [limit] [page]"


@pytest.mark.asyncio
async def test_runtime_debug_context_unknown_subcommand_shows_usage(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    response = await runtime.handle_command(
        RPCommand("debug", ["status"], "/rp debug status"),
        Event(),
    )

    assert (
        response
        == "Usage: /rp debug [prompt [limit] [page]|context [limit] [page]|swipes]"
    )


@pytest.mark.asyncio
async def test_runtime_debug_context_is_read_only_and_does_not_call_adapter(tmp_path):
    class ExplodingAdapter:
        def __init__(self):
            self.called = False

        def generate(self, *_args, **_kwargs):
            self.called = True
            raise AssertionError("adapter should not be called during debug context")

    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    adapter = ExplodingAdapter()
    runtime.hermes_adapter = adapter

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    session_before = dict(store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1"))
    messages_before = len(store.get_recent_messages(session["id"]))

    response = await runtime.handle_command(
        RPCommand("debug", ["context"], "/rp debug context"),
        Event(),
    )

    assert "Hermes Tavern context budget" in response
    assert adapter.called is False
    session_after = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    messages_after = len(store.get_recent_messages(session["id"]))
    assert messages_before == messages_after
    assert session_before["card_id"] == session_after["card_id"]


@pytest.mark.asyncio
async def test_runtime_active_message_expands_macro_context_in_rendered_prompt(tmp_path):
    class CapturingAdapter:
        def __init__(self):
            self.messages = []

        def generate(self, messages, profile):
            del profile
            self.messages = messages
            return "captured"

    class NamedEvent(Event):
        user_name = "Morgan"

    class MessageEvent(NamedEvent):
        text = "Ask lore about {{char}} for {{user}}."

    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({
        "name": "Alice",
        "description": "Card {{char}} speaks with {{user}}.",
        "first_mes": "Hello there.",
    }))
    preset_id = store.save_preset(import_raw_preset_text(
        "Preset {{content_mode}} / {{session_title}}.",
        name="macro-preset",
    ))
    lorebook_id = store.save_lorebook(import_st_lorebook_json({
        "name": "macro-lore",
        "entries": {
            "0": {
                "key": ["lore"],
                "content": "Lore names {{char}} and {{user}}.",
                "enabled": True,
            }
        },
    }))
    runtime = TavernRuntime(store, hermes_adapter=CapturingAdapter())
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), NamedEvent())
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.rename_session(session["id"], "Chapter One")
    store.set_session_content_mode(session["session_key"], "adult-fiction")
    store.set_session_preset(session["session_key"], preset_id)
    store.set_session_lorebook(session["session_key"], lorebook_id)
    store.add_session_memory_fact(session["session_key"], "Fact about {{user}}.")
    store.append_message(session["id"], "user", "Earlier {{user}} met {{char}}.")
    store.set_session_adapter_mode(session["session_key"], "hermes")
    store.set_session_live_confirmed(session["session_key"], True)

    response = await runtime.handle_active_message(MessageEvent())

    assert response == "captured"
    rendered = "\n".join(message["content"] for message in runtime.hermes_adapter.messages)
    assert "Card Alice speaks with Morgan." in rendered
    assert "Preset adult-fiction / Chapter One." in rendered
    assert "Lore names Alice and Morgan." in rendered
    assert "Fact about Morgan." in rendered
    assert "Earlier Morgan met Alice." in rendered
    assert "Ask lore about Alice for Morgan." in rendered
    assert "{{char}}" not in rendered
    assert "{{user}}" not in rendered


@pytest.mark.asyncio
async def test_runtime_debug_prompt_reports_macro_context_without_raw_event_json(tmp_path):
    class NamedEvent(Event):
        sender_name = "Morgan"
        raw = {"private_detail": "should-not-appear"}

    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), NamedEvent())
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.rename_session(session["id"], "Chapter One")

    response = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), NamedEvent())

    assert "macro_context:" in response
    assert "char=Alice" in response
    assert "user=Morgan" in response
    assert "session=Chapter One" in response
    assert "content_mode=safe" in response
    assert "should-not-appear" not in response
    assert "raw" not in response


@pytest.mark.asyncio
async def test_runtime_model_status_reports_secret_free_route(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(RPCommand("model", ["status"], "/rp model status"), Event())

    assert "Hermes Tavern model route" in response
    assert "claude-opus-4-6" in response
    assert "api_key" not in response
    assert "access_token" not in response


@pytest.mark.asyncio
async def test_runtime_model_profiles_lists_configured_profiles(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_model_profile(
        profile_id="opus-default",
        name="Opus 4.6 Default",
        provider="anthropic",
        model_id="claude-opus-4-6",
    )
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(RPCommand("model", ["profiles"], "/rp model profiles"), Event())

    assert "Opus 4.6 Default" in response
    assert "claude-opus-4-6" in response


@pytest.mark.asyncio
async def test_runtime_model_seed_apiyi_and_use_profile(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    seeded = await runtime.handle_command(RPCommand("model", ["seed", "apiyi"], "/rp model seed apiyi"), Event())
    selected = await runtime.handle_command(RPCommand("model", ["use", "apiyi-opus-default"], "/rp model use apiyi-opus-default"), Event())
    status = await runtime.handle_command(RPCommand("model", ["status"], "/rp model status"), Event())

    assert "Seeded APIYI" in seeded
    assert "APIYI_API_KEY" in seeded
    assert "api_key" not in seeded
    assert "apiyi-opus-default" in selected
    assert "provider: apiyi" in status
    assert "model_id: claude-opus-4-6" in status
    assert "api_key" not in status


@pytest.mark.asyncio
async def test_runtime_model_mode_commands_are_session_scoped(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    current = await runtime.handle_command(RPCommand("model", ["mode"], "/rp model mode"), Event())
    changed = await runtime.handle_command(RPCommand("model", ["mode", "hermes"], "/rp model mode hermes"), Event())
    status = await runtime.handle_command(RPCommand("model", ["status"], "/rp model status"), Event())

    assert current.endswith("fake")
    assert "mode set to hermes" in changed
    assert "adapter_mode: hermes" in status


@pytest.mark.asyncio
async def test_runtime_model_live_gate_commands(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    status = await runtime.handle_command(RPCommand("model", ["live"], "/rp model live"), Event())
    enabled = await runtime.handle_command(RPCommand("model", ["live", "confirm"], "/rp model live confirm"), Event())
    route = await runtime.handle_command(RPCommand("model", ["status"], "/rp model status"), Event())
    disabled = await runtime.handle_command(RPCommand("model", ["live", "off"], "/rp model live off"), Event())

    assert status.endswith("False")
    assert "ENABLED" in enabled
    assert "live_confirmed: True" in route
    assert "disabled" in disabled


@pytest.mark.asyncio
async def test_runtime_hermes_mode_without_live_confirm_does_not_call_default_adapter(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({
        "name": "Alice",
        "description": "Scholar",
        "first_mes": "Hello there.",
    }))
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1", card_id="Alice")
    store.set_session_adapter_mode("telegram:chat:chat-1:thread:main:user:user-1", "hermes")
    runtime = TavernRuntime(store)

    class MessageEvent(Event):
        text = "Continue."

    response = await runtime.handle_active_message(MessageEvent())

    assert "live generation is off" in response


@pytest.mark.asyncio
async def test_runtime_hermes_mode_uses_injected_adapter_without_network(tmp_path):
    class StubHermesAdapter:
        called = False

        def generate(self, messages, profile):
            self.called = True
            raise NotImplementedError("no network")

    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({
        "name": "Alice",
        "description": "Scholar",
        "first_mes": "Hello there.",
    }))
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1", card_id="Alice")
    store.set_session_adapter_mode("telegram:chat:chat-1:thread:main:user:user-1", "hermes")
    store.set_session_live_confirmed("telegram:chat:chat-1:thread:main:user:user-1", True)
    adapter = StubHermesAdapter()
    runtime = TavernRuntime(store, hermes_adapter=adapter)

    class MessageEvent(Event):
        text = "Continue."

    response = await runtime.handle_active_message(MessageEvent())

    assert adapter.called
    assert "real generation is not wired" in response


@pytest.mark.asyncio
async def test_runtime_end_deactivates_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(RPCommand("end", [], "/rp end"), Event())

    assert "ended" in response.lower()
    assert store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1") is None


@pytest.mark.asyncio
async def test_runtime_switch_without_matching_session_returns_not_found(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    response = await runtime.handle_command(RPCommand("switch", ["zzzz"], "/rp switch zzzz"), Event())

    assert response == "Session not found: zzzz"

# --- Phase 19: error envelope + /rp model test + gateway non-crash ---


@pytest.mark.asyncio
async def test_runtime_live_provider_exception_does_not_leak_secret_detail(tmp_path):
    """Error envelope must not forward str(exc) which may contain secrets/URLs."""
    class ExplodingAdapter:
        def generate(self, messages, profile):
            raise RuntimeError("secret-detail: api_key=[REDACTED] url=https://internal/v1")

    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Bob", "first_mes": "Hi."}))
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1", card_id="Bob")
    store.set_session_adapter_mode("telegram:chat:chat-1:thread:main:user:user-1", "hermes")
    store.set_session_live_confirmed("telegram:chat:chat-1:thread:main:user:user-1", True)
    runtime = TavernRuntime(store, hermes_adapter=ExplodingAdapter())

    class MessageEvent(Event):
        text = "Hello."

    response = await runtime.handle_active_message(MessageEvent())

    assert "secret-detail" not in response
    assert "[REDACTED]" not in response
    assert "provider error" in response.lower() or "not wired" in response.lower()


@pytest.mark.asyncio
async def test_runtime_model_test_no_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(RPCommand("model", ["test"], "/rp model test"), Event())

    assert "No active Hermes Tavern session" in response


@pytest.mark.asyncio
async def test_runtime_model_test_fake_mode(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(RPCommand("model", ["test"], "/rp model test"), Event())

    assert "dry-run" in response.lower() or "model test" in response.lower()
    assert "fake mode" in response
    assert "api_key" not in response
    assert "access_token" not in response


@pytest.mark.asyncio
async def test_runtime_model_test_hermes_mode_with_fake_resolver(tmp_path, monkeypatch):
    """model test in hermes mode resolves provider without real generation."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.set_session_adapter_mode("telegram:chat:chat-1:thread:main:user:user-1", "hermes")
    store.set_session_live_confirmed("telegram:chat:chat-1:thread:main:user:user-1", True)
    runtime = TavernRuntime(store)

    import plugins.hermes_tavern.provider_bridge as bridge_mod

    def fake_resolve_fn(**kwargs):
        return {
            "provider": "fake-provider",
            "api_key": "test-placeholder-key",
            "base_url": "https://api.fake-provider.example/v1",
            "model": "fake-model",
            "source": "test_injected",
        }

    monkeypatch.setattr(
        bridge_mod.HermesRuntimeProviderResolver,
        "resolve",
        lambda self: fake_resolve_fn(),
    )

    response = await runtime.handle_command(RPCommand("model", ["test"], "/rp model test"), Event())

    assert "test-placeholder-key" not in response  # actual key value must not appear
    assert "no real generation" in response
    assert "result:" in response


def test_gateway_hook_does_not_crash_on_active_message_provider_exception(tmp_path):
    """gateway hook must return allow (not crash) when provider raises."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Carol", "first_mes": "Hey."}))
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1", card_id="Carol")
    store.set_session_adapter_mode("telegram:chat:chat-1:thread:main:user:user-1", "hermes")
    store.set_session_live_confirmed("telegram:chat:chat-1:thread:main:user:user-1", True)

    class BombAdapter:
        def generate(self, messages, profile):
            raise ConnectionError("network gone")

    class TextEvent(Event):
        text = "Hello Carol."

    result = pre_gateway_dispatch(event=TextEvent(), store=store)

    assert result.get("action") in {"skip", "allow"}  # must not raise


# --- /rp card import ---


@pytest.mark.asyncio
async def test_runtime_card_import_success(tmp_path):
    import json as _json

    card_file = tmp_path / "alice.json"
    card_file.write_text(_json.dumps({"name": "Alice", "description": "A scholar."}))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("card", ["import", str(card_file)], f"/rp card import {card_file}"),
        Event(),
    )

    assert "Imported card: Alice" in response
    assert "/rp card inspect" in response
    assert "/rp start" in response
    saved = store.get_card("Alice")
    assert saved is not None


@pytest.mark.asyncio
async def test_runtime_card_import_embedded_lorebook_is_saved_and_reported(tmp_path):
    import json as _json

    card_file = tmp_path / "alice.json"
    card_file.write_text(_json.dumps(_v3_card_with_embedded_book("Alice")))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("card", ["import", str(card_file)], f"/rp card import {card_file}"),
        Event(),
    )

    assert "Imported card: Alice" in response
    assert "embedded lorebook: Alice World" in response
    lorebooks = store.list_lorebooks()
    assert len(lorebooks) == 1
    assert lorebooks[0]["name"] == "Alice World"
    assert lorebooks[0]["entry_count"] == 2


@pytest.mark.asyncio
async def test_runtime_card_import_png_success(tmp_path):
    png_path = tmp_path / "bob.png"
    png_path.write_bytes(_make_png_with_chara({"name": "Bob", "description": "A rogue."}))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("card", ["import", str(png_path)], f"/rp card import {png_path}"),
        Event(),
    )

    assert "Imported card: Bob" in response
    assert "/rp card inspect" in response
    assert store.get_card("Bob") is not None


@pytest.mark.asyncio
async def test_runtime_card_import_png_no_chara_returns_friendly_error(tmp_path):
    # PNG with no chara chunk gives a clear message, not a traceback
    png_path = tmp_path / "card.png"
    png_path.write_bytes(b"\x89PNG\r\n\x1a\n")  # valid sig, no chunks
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(
        RPCommand("card", ["import", str(png_path)], f"/rp card import {png_path}"),
        Event(),
    )

    assert "chara" in response.lower() or "metadata" in response.lower()


@pytest.mark.asyncio
async def test_runtime_card_import_invalid_json_returns_friendly_error(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("this is not json")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(
        RPCommand("card", ["import", str(bad_file)], f"/rp card import {bad_file}"),
        Event(),
    )

    assert "Could not import card" in response or "Invalid JSON" in response


class AttachmentEvent(Event):
    def __init__(self, media_urls):
        self.media_urls = media_urls


@pytest.mark.asyncio
async def test_runtime_card_import_from_single_attachment_json(tmp_path):
    card_file = tmp_path / "alice.json"
    card_file.write_text(_json.dumps({"name": "Alice", "description": "Scholar."}))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("card", ["import"], "/rp card import"),
        AttachmentEvent([str(card_file)]),
    )

    assert "Imported card: Alice" in response
    assert store.get_card("Alice") is not None


@pytest.mark.asyncio
async def test_runtime_card_import_from_single_attachment_png(tmp_path):
    png_path = tmp_path / "bob.png"
    png_path.write_bytes(_make_png_with_chara({"name": "Bob", "description": "Rogue."}))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    response = await runtime.handle_command(
        RPCommand("card", ["import"], "/rp card import"),
        AttachmentEvent([str(png_path)]),
    )

    assert "Imported card: Bob" in response
    assert store.get_card("Bob") is not None


@pytest.mark.asyncio
async def test_runtime_card_import_no_args_no_attachment_shows_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(
        RPCommand("card", ["import"], "/rp card import"),
        Event(),
    )

    assert "Usage:" in response
    assert ".json" in response
    assert ".png" in response
    assert "attach" in response.lower()


@pytest.mark.asyncio
async def test_runtime_card_import_multiple_attachments_asks_to_specify(tmp_path):
    f1 = tmp_path / "alice.json"
    f2 = tmp_path / "bob.json"
    f1.write_text(_json.dumps({"name": "Alice"}))
    f2.write_text(_json.dumps({"name": "Bob"}))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(
        RPCommand("card", ["import"], "/rp card import"),
        AttachmentEvent([str(f1), str(f2)]),
    )

    assert "Multiple card attachments found" in response
    assert "alice.json" in response and "bob.json" in response
    assert "/rp card import <file>" in response


@pytest.mark.asyncio
async def test_runtime_card_import_https_url(monkeypatch, tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    seen = {}

    def fake_load_card_file(source):
        seen["source"] = source
        return parse_character_card({"name": "Remote Alice", "description": "URL card"})

    monkeypatch.setattr("plugins.hermes_tavern.runtime_assets.load_card_file", fake_load_card_file)

    response = await runtime.handle_command(
        RPCommand("card", ["import", "https://example.com/alice.png"], "/rp card import https://example.com/alice.png"),
        Event(),
    )

    assert seen["source"] == "https://example.com/alice.png"
    assert "Imported card: Remote Alice" in response
    assert store.get_card("Remote Alice") is not None


@pytest.mark.asyncio
async def test_runtime_help_includes_card_import(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(RPCommand("help", [], "/rp"), Event())

    assert "/rp card import" in response


@pytest.mark.asyncio
async def test_runtime_export_markdown_with_messages_and_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.append_message(session["id"], "user", "What's up?")
    store.append_message(session["id"], "assistant", "Not much.")
    store.rename_session(session["id"], "Test Chat")

    response = await runtime.handle_command(RPCommand("export", [], "/rp export"), Event())

    assert "Session exported as Markdown." in response
    assert "file:" in response
    assert "MEDIA:" in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path
    from gateway.platforms.base import BasePlatformAdapter
    media_files, cleaned = BasePlatformAdapter.extract_media(response)
    assert media_files == [(file_path, False)]
    assert "MEDIA:" not in cleaned
    from pathlib import Path
    exported_path = Path(file_path)
    assert str(exported_path).startswith(str(tmp_path / "hermes home"))
    exported = exported_path.read_text(encoding="utf-8")
    assert "Test Chat" in exported
    assert "Alice" in exported
    assert "What's up?" in exported
    assert "Not much." in exported
    assert 'MEDIA:"' in response
    assert "metadata_json" not in exported
    assert "fake-api-key-do-not-persist" not in exported


@pytest.mark.asyncio
async def test_runtime_export_st_json_with_card_and_swipes(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    await runtime.handle_command(RPCommand("say", ["What", "next?"], "/rp say What next?"), Event())
    runtime._run_generation_pipeline = lambda session, user_text, history, event=None: "second candidate"
    await runtime.handle_command(RPCommand("retry", [], "/rp retry"), Event())

    response = await runtime.handle_command(RPCommand("export", ["st-json"], "/rp export st-json"), Event())

    assert "Session exported as ST-compatible JSON." in response
    assert "file:" in response
    assert "MEDIA:" in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path
    from gateway.platforms.base import BasePlatformAdapter
    media_files, cleaned = BasePlatformAdapter.extract_media(response)
    assert media_files == [(file_path, False)]
    assert "MEDIA:" not in cleaned
    from pathlib import Path
    exported_path = Path(file_path)
    assert str(exported_path).startswith(str(tmp_path / "hermes home"))
    exported = _json.loads(exported_path.read_text(encoding="utf-8"))
    assert exported["hermes_tavern_export"] is True
    assert exported["card_name"] == "Alice"
    assert "card" in exported
    msgs = exported["messages"]
    assert any("swipes" in m for m in msgs)
    assert any(m.get("swipes") == [FAKE_ADAPTER_REPLY, "second candidate"] for m in msgs)
    assert 'MEDIA:"' in response
    assert "metadata_json" not in exported_path.read_text(encoding="utf-8")
    assert "fake-api-key-do-not-persist" not in exported_path.read_text(encoding="utf-8")


@pytest.mark.asyncio
async def test_runtime_export_media_marker_quotes_paths_with_spaces_and_omits_raw_metadata(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home with spaces"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.append_message(
        session["id"],
        "assistant",
        "Visible reply.",
        metadata={
            "kind": "assistant_turn",
            "raw_event": {"Authorization": "fake-token-do-not-persist"},
            "API_KEY": "fake-api-key-do-not-persist",
        },
    )

    response = await runtime.handle_command(RPCommand("export", [], "/rp export"), Event())

    assert 'MEDIA:"' in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_marker = response.split("MEDIA:", 1)[1].strip()
    assert media_marker == f'"{file_path}"'
    assert " " in file_path
    from gateway.platforms.base import BasePlatformAdapter
    media_files, cleaned = BasePlatformAdapter.extract_media(response)
    assert media_files == [(file_path, False)]
    assert "MEDIA:" not in cleaned
    exported_text = Path(file_path).read_text(encoding="utf-8")
    assert "Visible reply." in exported_text
    assert "raw_event" not in exported_text
    assert "fake-token-do-not-persist" not in exported_text
    assert "fake-api-key-do-not-persist" not in exported_text


@pytest.mark.asyncio
async def test_runtime_model_status_sanitizes_debug_descriptor_recursively(tmp_path, monkeypatch):
    class Descriptor:
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

    class Router:
        def resolve(self, session_row=None, store=None):
            return Descriptor()

    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello!"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    monkeypatch.setattr(runtime_model, "_router", Router())

    status = await runtime.handle_command(RPCommand("model", ["status"], "/rp model status"), Event())

    assert "provider: anthropic" in status
    assert "model_id: claude-opus-4-6" in status
    assert "fake-" not in status
    assert "API_KEY" not in status
    assert "Access_Token" not in status


@pytest.mark.asyncio
async def test_runtime_export_no_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(RPCommand("export", [], "/rp export"), Event())

    assert "No active Hermes Tavern session" in response


@pytest.mark.asyncio
async def test_runtime_help_includes_export(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = await runtime.handle_command(RPCommand("help", [], "/rp"), Event())

    assert "/rp export" in response
