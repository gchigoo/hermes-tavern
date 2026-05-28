"""End-to-end generation pipeline test for Hermes Tavern.

Covers: active session + card + preset + lorebook + memory
  → prompt compile → renderer → injected fake adapter
  → assistant message persisted → user-safe reply.

No real network calls; no credentials.
"""

from __future__ import annotations

import json

import pytest

from plugins.hermes_tavern.adapters import FAKE_ADAPTER_REPLY, FakeModelAdapter
from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-e2e"
    thread_id = None
    user_id = "user-e2e"


class Event:
    source = Source()
    text = ""


SESSION_KEY = "telegram:chat:chat-e2e:thread:main:user:user-e2e"


def _make_preset_file(tmp_path, name: str, content: str) -> object:
    """Write a minimal ST-style plain-text preset file."""
    p = tmp_path / f"{name}.txt"
    p.write_text(content, encoding="utf-8")
    return p


def _make_lorebook_file(tmp_path, name: str, keyword: str, lore_content: str) -> object:
    """Write a minimal SillyTavern JSON lorebook file."""
    p = tmp_path / f"{name}.json"
    data = {
        "entries": {
            "0": {
                "key": [keyword],
                "content": lore_content,
                "enabled": True,
                "constant": False,
                "regex": False,
            }
        }
    }
    p.write_text(json.dumps(data), encoding="utf-8")
    return p


@pytest.mark.asyncio
async def test_e2e_full_pipeline_with_fake_adapter(tmp_path):
    """Full pipeline: session+card+preset+lore+memory → compile → fake adapter → persisted reply."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    # 1. Import card
    store.save_card(parse_character_card({
        "name": "Elara",
        "description": "A wise elven scholar.",
        "personality": "Thoughtful and calm.",
        "scenario": "A grand library.",
        "first_mes": "Welcome, traveler.",
        "mes_example": "",
    }))

    # 2. Import preset
    preset_path = _make_preset_file(tmp_path, "scholar", "You are a knowledgeable guide.")
    await runtime.handle_command(
        RPCommand("preset", ["import", str(preset_path)], f"/rp preset import {preset_path}"),
        Event(),
    )

    # 3. Import lorebook
    lore_path = _make_lorebook_file(tmp_path, "elven_lore", "elven", "Elves live for millennia.")
    await runtime.handle_command(
        RPCommand("lore", ["import", str(lore_path)], f"/rp lore import {lore_path}"),
        Event(),
    )

    # 4. Start session with card
    start_resp = await runtime.handle_command(
        RPCommand("start", ["Elara"], "/rp start Elara"),
        Event(),
    )
    assert "Started" in start_resp
    assert "Elara" in start_resp

    session = store.get_active_session(SESSION_KEY)
    assert session is not None

    # 5. Bind preset
    preset_resp = await runtime.handle_command(
        RPCommand("preset", ["use", "scholar"], "/rp preset use scholar"),
        Event(),
    )
    assert "bound" in preset_resp.lower()

    # 6. Bind lorebook
    lore_resp = await runtime.handle_command(
        RPCommand("lore", ["use", "elven_lore"], "/rp lore use elven_lore"),
        Event(),
    )
    assert "bound" in lore_resp.lower()

    # 7. Add memory fact
    mem_resp = await runtime.handle_command(
        RPCommand("memory", ["add", "The user seeks ancient knowledge."], "/rp memory add The user seeks ancient knowledge."),
        Event(),
    )
    assert "saved" in mem_resp.lower()

    # 8. Send an active message — triggers full pipeline
    class MessageEvent(Event):
        text = "Tell me about elven history."

    reply = await runtime.handle_active_message(MessageEvent())

    # 9. Verify reply is the fake adapter reply (no network)
    assert reply == FAKE_ADAPTER_REPLY

    # 10. Verify both messages persisted in DB
    session = store.get_active_session(SESSION_KEY)
    messages = store.get_recent_messages(session["id"], limit=10)
    roles = [m["role"] for m in messages]
    assert "user" in roles
    assert "assistant" in roles

    user_msgs = [m for m in messages if m["role"] == "user"]
    assistant_msgs = [m for m in messages if m["role"] == "assistant"]
    assert any("elven history" in m["content"] for m in user_msgs)
    assert any(m["content"] == FAKE_ADAPTER_REPLY for m in assistant_msgs)


@pytest.mark.asyncio
async def test_e2e_no_card_returns_placeholder(tmp_path):
    """Session with no card bound should not crash — returns placeholder."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    store.start_session(SESSION_KEY)  # no card

    class MessageEvent(Event):
        text = "Hello?"

    reply = await runtime.handle_active_message(MessageEvent())

    # Should return placeholder, not crash
    assert isinstance(reply, str)
    assert len(reply) > 0


@pytest.mark.asyncio
async def test_e2e_model_test_in_fake_mode_does_not_generate(tmp_path):
    """model test command performs no generation even with full session setup."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    store.save_card(parse_character_card({"name": "Ryn", "first_mes": "Hi."}))
    await runtime.handle_command(RPCommand("start", ["Ryn"], "/rp start Ryn"), Event())

    response = await runtime.handle_command(
        RPCommand("model", ["test"], "/rp model test"),
        Event(),
    )

    assert "no real generation" in response
    assert "api_key" not in response
    assert "access_token" not in response

    session = store.get_active_session(SESSION_KEY)
    messages = store.get_recent_messages(session["id"], limit=20)
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert len(user_msgs) == 0  # model test must not write any user/assistant turn
