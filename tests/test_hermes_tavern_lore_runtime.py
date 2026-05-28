import json
from pathlib import Path

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.lorebooks import import_st_lorebook_json
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


@pytest.mark.asyncio
async def test_lore_runtime_import_list_use_test_debug(tmp_path):
    path = tmp_path / "atlas.json"
    path.write_text(json.dumps({
        "name": "Atlas",
        "entries": [{"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"]}],
    }), encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    imported = await runtime.handle_command(RPCommand("lore", ["import", str(path)], "/rp lore import"), Event())
    listed = await runtime.handle_command(RPCommand("lore", ["list"], "/rp lore list"), Event())
    bound = await runtime.handle_command(RPCommand("lore", ["use", "Atlas"], "/rp lore use Atlas"), Event())
    tested = await runtime.handle_command(RPCommand("lore", ["test", "moon"], "/rp lore test moon"), Event())
    debug = await runtime.handle_command(RPCommand("lore", ["debug"], "/rp lore debug"), Event())
    cleared = await runtime.handle_command(RPCommand("lore", ["clear"], "/rp lore clear"), Event())

    assert "Imported ST lorebook" in imported
    assert "Atlas" in listed
    assert "lorebook bound" in bound
    assert "Moon" in tested and "matched:" in tested
    assert "+ Moon: key match: moon" in tested
    assert "debug: /rp lore debug" in tested
    assert "keys=['moon']" in debug
    assert "lorebook cleared" in cleared
    assert store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["lorebook_id"] is None


@pytest.mark.asyncio
async def test_lore_modules_appear_in_debug_prompt(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    lorebook_id = store.save_lorebook(import_st_lorebook_json({
        "name": "Atlas",
        "entries": [{"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"]}],
    }))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    store.set_session_lorebook("telegram:chat:chat-1:thread:main:user:user-1", lorebook_id)
    active = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.append_message(active["id"], "user", "Tell me about the moon")

    prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "lorebook:" in prompt
    assert "lore:Moon" in prompt
    assert "The moon is cracked" in prompt


@pytest.mark.asyncio
async def test_lore_enable_disable_entry_affects_matching(tmp_path):
    path = tmp_path / "atlas.json"
    path.write_text(json.dumps({
        "name": "Atlas",
        "entries": [
            {"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"]},
            {"comment": "Sun", "content": "The sun is blue.", "keys": ["sun"], "disable": True},
        ],
    }), encoding="utf-8")
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime = TavernRuntime(store)

    await runtime.handle_command(RPCommand("lore", ["import", str(path)], "/rp lore import"), Event())
    await runtime.handle_command(RPCommand("lore", ["use", "Atlas"], "/rp lore use Atlas"), Event())

    before = await runtime.handle_command(RPCommand("lore", ["test", "moon", "sun"], "/rp lore test moon sun"), Event())
    disabled = await runtime.handle_command(RPCommand("lore", ["disable", "Moon"], "/rp lore disable Moon"), Event())
    after_disable = await runtime.handle_command(RPCommand("lore", ["test", "moon", "sun"], "/rp lore test moon sun"), Event())
    enabled = await runtime.handle_command(RPCommand("lore", ["enable", "Sun"], "/rp lore enable Sun"), Event())
    after_enable = await runtime.handle_command(RPCommand("lore", ["test", "moon", "sun"], "/rp lore test moon sun"), Event())

    assert "+ Moon: key match: moon" in before
    assert "+ Sun: key match: sun" not in before
    assert "lore entry disabled: Moon" in disabled
    assert "+ Moon: key match: moon" not in after_disable
    assert "lore entry enabled: Sun" in enabled
    assert "+ Sun: key match: sun" in after_enable
