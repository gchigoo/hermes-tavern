import json

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""

    def __init__(self, media_urls=None):
        self.media_urls = list(media_urls or [])


def test_preset_import_uses_single_json_or_txt_attachment(tmp_path):
    preset_file = tmp_path / "mobile-preset.txt"
    preset_file.write_text("Keep replies concise.", encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    imported = runtime.handle_command_sync(
        RPCommand("preset", ["import"], "/rp preset import"),
        Event([str(preset_file)]),
    )

    assert "Imported ST preset: mobile-preset" in imported
    assert "use: /rp preset use " in imported
    assert "inspect: /rp preset inspect " in imported
    assert "Keep replies concise" not in imported


def test_preset_import_explicit_path_includes_mobile_followups(tmp_path):
    preset_file = tmp_path / "explicit-preset.txt"
    preset_file.write_text("Keep replies tight.", encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    imported = runtime.handle_command_sync(
        RPCommand("preset", ["import", str(preset_file)], f"/rp preset import {preset_file}"),
        Event([str(preset_file)]),
    )

    assert "Imported ST preset: explicit-preset" in imported
    assert "use: /rp preset use " in imported
    assert "inspect: /rp preset inspect " in imported
    assert "Keep replies tight" not in imported


def test_preset_import_without_attachment_mentions_attach_json_txt(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    result = runtime.handle_command_sync(
        RPCommand("preset", ["import"], "/rp preset import"),
        Event(),
    )

    assert "Usage: /rp preset import <file.json|file.txt>" in result
    assert "attach a .json or .txt" in result


def test_preset_import_multiple_attachments_asks_for_path(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.txt"
    first.write_text(json.dumps({"name": "First", "prompts": []}), encoding="utf-8")
    second.write_text("Second preset", encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    result = runtime.handle_command_sync(
        RPCommand("preset", ["import"], "/rp preset import"),
        Event([str(first), str(second), "https://example.test/remote.json"]),
    )

    assert "Multiple preset attachments found:" in result
    assert "1. first.json" in result
    assert "2. second.txt" in result
    assert "remote.json" not in result
    assert "Specify one explicitly: /rp preset import <file>" in result


def test_lore_import_uses_single_json_attachment(tmp_path):
    lore_file = tmp_path / "atlas.json"
    lore_file.write_text(
        json.dumps({"name": "Atlas", "entries": [{"comment": "Moon", "content": "The moon.", "keys": ["moon"]}]}),
        encoding="utf-8",
    )
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    imported = runtime.handle_command_sync(
        RPCommand("lore", ["import"], "/rp lore import"),
        Event([str(lore_file)]),
    )

    assert "Imported ST lorebook: Atlas" in imported
    assert "entries: 1" in imported
    assert "use: /rp lore use " in imported
    assert "inspect: /rp lore inspect " in imported


def test_lore_import_explicit_path_includes_mobile_followups(tmp_path):
    lore_file = tmp_path / "explicit-atlas.json"
    lore_file.write_text(
        json.dumps({"name": "Explicit Atlas", "entries": [{"comment": "Moon", "content": "The moon.", "keys": ["moon"]}]}),
        encoding="utf-8",
    )
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    imported = runtime.handle_command_sync(
        RPCommand("lore", ["import", str(lore_file)], f"/rp lore import {lore_file}"),
        Event([str(lore_file)]),
    )

    assert "Imported ST lorebook: Explicit Atlas" in imported
    assert "use: /rp lore use " in imported
    assert "inspect: /rp lore inspect " in imported


def test_lore_import_requires_single_json_attachment(tmp_path):
    txt_file = tmp_path / "not-lore.txt"
    txt_file.write_text("not json", encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    no_importable = runtime.handle_command_sync(
        RPCommand("lore", ["import"], "/rp lore import"),
        Event([str(txt_file)]),
    )
    duplicate = runtime.handle_command_sync(
        RPCommand("lore", ["import"], "/rp lore import"),
        Event([str(tmp_path / "a.json"), str(tmp_path / "b.json")]),
    )

    assert "Usage: /rp lore import <file.json>" in no_importable
    assert "attach a .json" in no_importable
    assert "Multiple lore attachments found:" in duplicate
    assert "1. a.json" in duplicate
    assert "2. b.json" in duplicate


def test_persona_import_uses_single_json_or_txt_attachment(tmp_path):
    persona_file = tmp_path / "traveler.txt"
    persona_file.write_text("I am {{user}}, a patient traveler.", encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    imported = runtime.handle_command_sync(
        RPCommand("persona", ["import"], "/rp persona import"),
        Event([str(persona_file)]),
    )

    assert "Imported Hermes Tavern persona: traveler" in imported
    assert "use: /rp persona use " in imported
    assert "inspect: /rp persona inspect " in imported
    assert "I am {{user}}" not in imported


def test_card_import_attachment_includes_all_mobile_followups(tmp_path):
    card_file = tmp_path / "alice.json"
    card_file.write_text(json.dumps({"name": "Alice", "description": "A scholar."}), encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    imported = runtime.handle_command_sync(
        RPCommand("card", ["import"], "/rp card import"),
        Event([str(card_file)]),
    )

    assert "Imported card: Alice" in imported
    assert "inspect: /rp card inspect " in imported
    assert "use: /rp card use " in imported
    assert "start: /rp start " in imported
    assert '"description"' not in imported


def test_persona_import_attachment_empty_and_multiple_cases(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    empty = runtime.handle_command_sync(
        RPCommand("persona", ["import"], "/rp persona import"),
        Event(),
    )
    multiple = runtime.handle_command_sync(
        RPCommand("persona", ["import"], "/rp persona import"),
        Event([str(tmp_path / "pilot.json"), str(tmp_path / "traveler.txt")]),
    )

    assert "Usage: /rp persona import <file.json|file.txt>" in empty
    assert "attach a .json or .txt" in empty
    assert "Multiple persona attachments found:" in multiple
    assert "1. pilot.json" in multiple
    assert "2. traveler.txt" in multiple


def test_card_use_last_after_import(tmp_path):
    card_file = tmp_path / "alice.json"
    card_file.write_text(json.dumps({"name": "Alice", "description": "A scholar."}), encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.handle_command_sync(RPCommand("card", ["import"], "/rp card import"), Event([str(card_file)]))
    runtime.handle_command_sync(RPCommand("start", ["last"], "/rp start last"), Event())

    result = runtime.handle_command_sync(RPCommand("card", ["use", "last"], "/rp card use last"), Event())

    assert "Hermes Tavern card bound: Alice" in result


def test_preset_use_last_after_import(tmp_path):
    card_file = tmp_path / "alice.json"
    preset_file = tmp_path / "mobile-preset.txt"
    card_file.write_text(json.dumps({"name": "Alice", "description": "A scholar."}), encoding="utf-8")
    preset_file.write_text("Keep replies concise.", encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.handle_command_sync(RPCommand("card", ["import"], "/rp card import"), Event([str(card_file)]))
    runtime.handle_command_sync(RPCommand("start", ["last"], "/rp start last"), Event())
    runtime.handle_command_sync(RPCommand("preset", ["import"], "/rp preset import"), Event([str(preset_file)]))

    result = runtime.handle_command_sync(RPCommand("preset", ["use", "last"], "/rp preset use last"), Event())

    assert "Hermes Tavern preset bound: mobile-preset" in result


def test_lore_use_last_after_import(tmp_path):
    card_file = tmp_path / "alice.json"
    lore_file = tmp_path / "atlas.json"
    card_file.write_text(json.dumps({"name": "Alice", "description": "A scholar."}), encoding="utf-8")
    lore_file.write_text(
        json.dumps({"name": "Atlas", "entries": [{"comment": "Moon", "content": "The moon.", "keys": ["moon"]}]}),
        encoding="utf-8",
    )
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.handle_command_sync(RPCommand("card", ["import"], "/rp card import"), Event([str(card_file)]))
    runtime.handle_command_sync(RPCommand("start", ["last"], "/rp start last"), Event())
    runtime.handle_command_sync(RPCommand("lore", ["import"], "/rp lore import"), Event([str(lore_file)]))

    result = runtime.handle_command_sync(RPCommand("lore", ["use", "last"], "/rp lore use last"), Event())

    assert "Hermes Tavern lorebook bound: Atlas" in result


def test_persona_use_last_after_import(tmp_path):
    card_file = tmp_path / "alice.json"
    persona_file = tmp_path / "traveler.txt"
    card_file.write_text(json.dumps({"name": "Alice", "description": "A scholar."}), encoding="utf-8")
    persona_file.write_text("I am {{user}}, a patient traveler.", encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.handle_command_sync(RPCommand("card", ["import"], "/rp card import"), Event([str(card_file)]))
    runtime.handle_command_sync(RPCommand("start", ["last"], "/rp start last"), Event())
    runtime.handle_command_sync(RPCommand("persona", ["import"], "/rp persona import"), Event([str(persona_file)]))

    result = runtime.handle_command_sync(RPCommand("persona", ["use", "last"], "/rp persona use last"), Event())

    assert "Hermes Tavern persona bound: traveler" in result


def test_card_start_last(tmp_path):
    card_file = tmp_path / "alice.json"
    card_file.write_text(json.dumps({"name": "Alice", "description": "A scholar."}), encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.handle_command_sync(RPCommand("card", ["import"], "/rp card import"), Event([str(card_file)]))

    result = runtime.handle_command_sync(RPCommand("start", ["last"], "/rp start last"), Event())

    assert "Started Hermes Tavern session with Alice." in result


def test_last_resolves_to_most_recent(tmp_path):
    first = tmp_path / "alice.json"
    second = tmp_path / "beatrice.json"
    first.write_text(json.dumps({"name": "Alice", "description": "A scholar."}), encoding="utf-8")
    second.write_text(json.dumps({"name": "Beatrice", "description": "An archivist."}), encoding="utf-8")
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.handle_command_sync(RPCommand("card", ["import"], "/rp card import"), Event([str(first)]))
    runtime.handle_command_sync(RPCommand("card", ["import"], "/rp card import"), Event([str(second)]))

    result = runtime.handle_command_sync(RPCommand("card", ["inspect", "last"], "/rp card inspect last"), Event())

    assert "Card: Beatrice" in result
    assert "Card: Alice" not in result


def test_last_without_import_returns_helpful_message(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    card = runtime.handle_command_sync(RPCommand("card", ["inspect", "last"], "/rp card inspect last"), Event())
    start = runtime.handle_command_sync(RPCommand("start", ["last"], "/rp start last"), Event())
    preset = runtime.handle_command_sync(RPCommand("preset", ["inspect", "last"], "/rp preset inspect last"), Event())
    lore = runtime.handle_command_sync(RPCommand("lore", ["inspect", "last"], "/rp lore inspect last"), Event())
    persona = runtime.handle_command_sync(RPCommand("persona", ["inspect", "last"], "/rp persona inspect last"), Event())

    assert card == "No card has been imported yet. Import a card first: /rp card import <file>"
    assert start == "No card has been imported yet. Import a card first: /rp card import <file>"
    assert preset == "No preset has been imported yet. Import a preset first: /rp preset import <file>"
    assert lore == "No lorebook has been imported yet. Import a lorebook first: /rp lore import <file>"
    assert persona == "No persona has been imported yet. Import a persona first: /rp persona import <file>"
