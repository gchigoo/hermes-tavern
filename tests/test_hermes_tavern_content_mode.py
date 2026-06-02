"""Runtime tests for Hermes Tavern content mode manager."""

from __future__ import annotations

import json

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import CharacterCard
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


def test_content_mode_controls_adult_fiction_preset_modules(tmp_path):
    preset_file = tmp_path / "adult.json"
    preset_file.write_text(
        json.dumps(
            {
                "name": "adult-style",
                "prompts": [
                    {
                        "name": "adult-tone",
                        "content": "Consenting adult fictional romance with intimate prose.",
                        "enabled": True,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(CharacterCard(id="card-1", name="Alice", description="Character base."))
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1", card_id="card-1")
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(
        RPCommand("preset", ["import", str(preset_file)], "/rp preset import"), Event()
    )
    runtime.handle_command_sync(
        RPCommand("preset", ["use", "adult-style"], "/rp preset use adult-style"), Event()
    )

    safe_debug = runtime.handle_command_sync(
        RPCommand("debug", ["prompt"], "/rp debug prompt"), Event()
    )
    assert "content_mode: safe" in safe_debug
    assert "preset:adult-tone" not in safe_debug

    mode_response = runtime.handle_command_sync(
        RPCommand("content", ["mode", "adult-fiction"], "/rp content mode adult-fiction"),
        Event(),
    )
    adult_debug = runtime.handle_command_sync(
        RPCommand("debug", ["prompt"], "/rp debug prompt"), Event()
    )

    assert "content mode set to adult-fiction" in mode_response
    assert "content_mode: adult-fiction" in adult_debug
    assert "preset:adult-tone" in adult_debug

    runtime.handle_command_sync(
        RPCommand("content", ["mode", "safe"], "/rp content mode safe"), Event()
    )
    safe_again = runtime.handle_command_sync(
        RPCommand("debug", ["prompt"], "/rp debug prompt"), Event()
    )
    assert "content_mode: safe" in safe_again
    assert "preset:adult-tone" not in safe_again


def test_content_mode_blocks_minor_sexualized_st_modules_from_debug_prompt(tmp_path):
    preset_file = tmp_path / "minor-adult.json"
    preset_file.write_text(
        json.dumps(
            {
                "name": "minor-safe-test",
                "prompts": [
                    {
                        "name": "allowed",
                        "content": "Consenting adult fictional romance with subtle emotional intimacy.",
                        "enabled": True,
                    },
                    {
                        "name": "minor-intimate",
                        "content": "A minor is given flirty, intimate roleplay instructions.",
                        "enabled": True,
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(CharacterCard(id="card-1", name="Alice", description="Character base."))
    store.start_session("telegram:chat:chat-1:thread:main:user:user-1", card_id="card-1")
    runtime = TavernRuntime(store)

    runtime.handle_command_sync(
        RPCommand("preset", ["import", str(preset_file)], "/rp preset import"), Event()
    )
    runtime.handle_command_sync(
        RPCommand("preset", ["use", "minor-safe-test"], "/rp preset use minor-safe-test"), Event()
    )
    runtime.handle_command_sync(
        RPCommand("content", ["mode", "adult-fiction"], "/rp content mode adult-fiction"), Event()
    )

    adult_debug = runtime.handle_command_sync(
        RPCommand("debug", ["prompt"], "/rp debug prompt"), Event()
    )

    assert "preset:allowed" in adult_debug
    assert "preset:minor-intimate" not in adult_debug
