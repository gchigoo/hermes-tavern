"""Tests for `/rp card export <card>` JSON export."""

from __future__ import annotations

import hashlib
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


@pytest.mark.parametrize("data_json", ["{", "[]", "null"])
def test_card_export_tolerates_corrupt_stored_metadata(tmp_path, monkeypatch, data_json):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    card_id = store.save_card(parse_character_card({"name": "Damaged"}))
    with store.connect() as conn:
        conn.execute("UPDATE cards SET data_json = ? WHERE id = ?", (data_json, card_id))
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Damaged"], "/rp card export Damaged"),
        Event(),
    )

    file_path, _ = _extract_export_paths(response)
    exported = json.loads(Path(file_path).read_text(encoding="utf-8"))

    assert response.startswith("Card exported as JSON.\n")
    assert exported["spec"] == "chara_card_v2"
    assert exported["data"]["name"] == "Damaged"


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
    digest = hashlib.sha256("../outside".encode("utf-8")).hexdigest()
    assert export_path.parent == expected_dir
    assert export_path.name == f"card_outside_{digest}.json"
    assert export_path.exists()


def test_card_export_adds_hash_to_safe_short_identifier_filename(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    card_id = "safe-ID_42"
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"id": card_id, "name": "Safe ID"}))
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Safe ID"], "/rp card export Safe ID"),
        Event(),
    )

    export_path = Path(_extract_export_paths(response)[0])
    digest = hashlib.sha256(card_id.encode("utf-8")).hexdigest()
    # Naming behavior intentionally changed: every original ID now contributes a hash.
    assert export_path.name == f"card_safe-ID_42_{digest}.json"
    assert export_path.exists()


def test_card_export_filename_is_bounded_for_oversized_identifier(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    oversized_id = "a" * 300
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"id": oversized_id, "name": "Long ID"}))
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["export", "Long ID"], "/rp card export Long ID"),
        Event(),
    )

    export_path = Path(_extract_export_paths(response)[0])
    digest = hashlib.sha256(oversized_id.encode("utf-8")).hexdigest()
    assert export_path.name == f"card_{'a' * 180}_{digest}.json"
    assert len(export_path.name.encode("utf-8")) == 255
    assert export_path.exists()


@pytest.mark.parametrize(
    ("first_id", "second_id"),
    [
        ("/" * 300, "?" * 300),
        ("e\u0301" * 100, "e\u0300" * 100),
        ("猫" * 100 + "甲", "猫" * 100 + "乙"),
    ],
    ids=("punctuation", "lossy-unicode", "shared-unicode-prefix"),
)
def test_card_export_filenames_do_not_collide_for_lossy_or_oversized_ids(
    tmp_path, monkeypatch, first_id, second_id
):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"id": first_id, "name": "First Collision Card"}))
    store.save_card(parse_character_card({"id": second_id, "name": "Second Collision Card"}))
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    first_response = runtime.handle_command_sync(
        RPCommand(
            "card",
            ["export", "First Collision Card"],
            "/rp card export First Collision Card",
        ),
        Event(),
    )
    second_response = runtime.handle_command_sync(
        RPCommand(
            "card",
            ["export", "Second Collision Card"],
            "/rp card export Second Collision Card",
        ),
        Event(),
    )
    first_path = Path(_extract_export_paths(first_response)[0])
    second_path = Path(_extract_export_paths(second_response)[0])

    assert first_path != second_path
    assert first_path.name.rsplit("_", 1)[0] == second_path.name.rsplit("_", 1)[0]
    for export_path, original_id, expected_name in (
        (first_path, first_id, "First Collision Card"),
        (second_path, second_id, "Second Collision Card"),
    ):
        digest = hashlib.sha256(original_id.encode("utf-8")).hexdigest()
        assert export_path.name.endswith(f"_{digest}.json")
        assert len(export_path.name.encode("utf-8")) <= 255
        assert json.loads(export_path.read_text(encoding="utf-8"))["name"] == expected_name


@pytest.mark.parametrize(
    ("first_id", "second_id"),
    [("caseid", "CASEID"), ("Å", "Å")],
    ids=("case-equivalent", "unicode-normalization-equivalent"),
)
def test_card_export_filenames_do_not_overwrite_filesystem_equivalent_ids(
    tmp_path, monkeypatch, first_id, second_id
):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"id": first_id, "name": "First Equivalent Card"}))
    store.save_card(parse_character_card({"id": second_id, "name": "Second Equivalent Card"}))
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    responses = [
        runtime.handle_command_sync(
            RPCommand("card", ["export", name], f"/rp card export {name}"),
            Event(),
        )
        for name in ("First Equivalent Card", "Second Equivalent Card")
    ]
    first_path, second_path = (
        Path(_extract_export_paths(response)[0]) for response in responses
    )

    assert first_path != second_path
    assert first_path.exists()
    assert second_path.exists()
    assert not first_path.samefile(second_path)
    assert json.loads(first_path.read_text(encoding="utf-8"))["name"] == (
        "First Equivalent Card"
    )
    assert json.loads(second_path.read_text(encoding="utf-8"))["name"] == (
        "Second Equivalent Card"
    )
    for export_path, original_id in (
        (first_path, first_id),
        (second_path, second_id),
    ):
        digest = hashlib.sha256(original_id.encode("utf-8")).hexdigest()
        assert export_path.name.endswith(f"_{digest}.json")
        assert len(export_path.name.encode("utf-8")) <= 255


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
