"""Tests for `/rp card export <card>` JSON export."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.identity import session_key_from_event
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


def _extract_export_paths(response: str) -> tuple[str, str]:
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split('MEDIA:"', 1)[1].split('"', 1)[0]
    return file_path, media_path


def _runtime_with_home(tmp_path: Path, store: TavernStore, monkeypatch) -> TavernRuntime:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    return TavernRuntime(store)


def test_card_export_writes_stored_raw_json_when_raw_is_dict(tmp_path, monkeypatch):
    raw = {
        "spec": "chara_card_v2",
        "spec_version": "3.0",
        "name": "Lyra",
        "data": {
            "name": "Lyra",
            "description": "A bard with strict style.",
            "personality": "Singing and playful.",
            "scenario": "At the tavern.",
            "first_mes": "Hello.",
            "mes_example": "Hi.",
            "alternate_greetings": ["Hello again.", "Welcome back."],
            "creator_notes": "notes",
            "system_prompt": "Stay in-character.",
            "post_history_instructions": "Stay in first person.",
            "tags": ["bard", "fantasy"],
            "talkativeness": 0.9,
            "extensions": {"note": "legacy"},
        },
    }
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card(raw))
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Lyra"], "/rp card export Lyra"),
        Event(),
    )

    file_path, media_path = _extract_export_paths(response)
    assert media_path == file_path
    assert "card_" in file_path

    exported = json.loads(Path(file_path).read_text(encoding="utf-8"))
    assert exported == raw
    assert "\n  " in Path(file_path).read_text(encoding="utf-8")


def test_card_export_generates_normalized_payload_when_raw_is_missing_or_invalid(
    tmp_path, monkeypatch
):
    source_fields = {
        "name": "Mira",
        "description": "A fallback test card.",
        "personality": "Thoughtful.",
        "scenario": "At sunset.",
        "first_mes": "Hi there.",
        "mes_example": "<START>",
        "alternate_greetings": ["Hello.", "Hey."],
        "creator_notes": "from fixture",
        "system_prompt_override": "Respond kindly.",
        "post_history_instructions": "No special instructions.",
        "tags": ["fallback", "export"],
        "talkativeness": 0.75,
        "extensions": {"test": "yes"},
    }
    store = TavernStore(tmp_path / "tavern.sqlite3")
    card = parse_character_card(source_fields)
    card_id = store.save_card(card)
    stored = store.get_card(card_id)
    assert stored is not None
    stored_data = json.loads(stored["data_json"])
    stored_data["raw"] = "not a dict"
    with store.connect() as conn:
        conn.execute(
            "UPDATE cards SET data_json = ? WHERE id = ?",
            (json.dumps(stored_data, sort_keys=True), card_id),
        )

    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Mira"], "/rp card export Mira"),
        Event(),
    )

    file_path, _ = _extract_export_paths(response)
    exported = json.loads(Path(file_path).read_text(encoding="utf-8"))

    assert exported["spec"] == "chara_card_v2"
    assert exported["spec_version"] == "3.0"
    data = exported["data"]
    for key in (
        "name",
        "description",
        "personality",
        "scenario",
        "first_mes",
        "mes_example",
        "creator_notes",
        "post_history_instructions",
    ):
        assert data[key] == source_fields[key]
    assert data["alternate_greetings"] == source_fields["alternate_greetings"]
    assert data["tags"] == source_fields["tags"]
    assert data["system_prompt"] == source_fields["system_prompt_override"]
    assert data["extensions"] == source_fields["extensions"]
    assert data["talkativeness"] == pytest.approx(source_fields["talkativeness"])


def test_card_export_with_last_keyword_uses_last_card(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "First", "description": "Old"}))
    second = parse_character_card(
        {
            "spec": "chara_card_v2",
            "data": {"name": "Second", "description": "New"},
        }
    )
    store.save_card(second)
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "last"], "/rp card export last"),
        Event(),
    )

    file_path, _ = _extract_export_paths(response)
    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))

    assert payload["data"]["name"] == "Second"


def test_card_export_reports_missing_card(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Missing"], "/rp card export Missing"),
        Event(),
    )

    assert response == "Character card not found: Missing"


def test_card_export_requires_argument(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = runtime.handle_command_sync(
        RPCommand("card", ["export"], "/rp card export"),
        Event(),
    )

    assert response == "Usage: /rp card export <card>"


def test_card_export_quotes_media_path_even_with_spaces_in_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home with spaces"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Lyra", "description": "Spaced path"}))
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Lyra"], "/rp card export Lyra"),
        Event(),
    )

    file_path, media_path = _extract_export_paths(response)
    assert media_path == file_path
    assert f'MEDIA:"{file_path}"' in response
    assert " " in file_path
    assert str(file_path).startswith(str(tmp_path / "hermes home with spaces"))
    assert str(file_path).startswith(
        str(
            (tmp_path / "hermes home with spaces")
            / "plugins/hermes-tavern/exports/cards"
        )
    )
    assert Path(file_path).exists()


def test_card_export_keeps_explicit_card_id_inside_cards_export_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"id": "../outside", "name": "Pathy"}))
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Pathy"], "/rp card export Pathy"),
        Event(),
    )

    file_path, _ = _extract_export_paths(response)
    export_path = Path(file_path)
    expected_dir = (
        tmp_path / "hermes home" / "plugins" / "hermes-tavern" / "exports" / "cards"
    )
    assert export_path.parent == expected_dir
    assert export_path.name == "card_outside.json"
    assert export_path.exists()


def test_card_export_does_not_mutate_session_or_messages(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "first_mes": "Hello there."}))
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session_key = session_key_from_event(Event())
    session = store.get_active_session(session_key)
    assert session is not None
    store.append_message(session["id"], "user", "before export")
    before_messages = [(msg["role"], msg["content"]) for msg in store.get_recent_messages(session["id"])]
    before_session = dict(session)

    runtime.handle_command_sync(
        RPCommand("card", ["export", "Alice"], "/rp card export Alice"),
        Event(),
    )

    after_session = store.get_active_session(session_key)
    after_messages = [(msg["role"], msg["content"]) for msg in store.get_recent_messages(session["id"])]
    assert after_session is not None
    assert after_session["id"] == before_session["id"]
    assert after_session["status"] == before_session["status"]
    assert after_session["card_id"] == before_session["card_id"]
    assert after_messages == before_messages
