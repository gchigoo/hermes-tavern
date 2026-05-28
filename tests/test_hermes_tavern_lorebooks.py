import json

from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.lorebooks import import_embedded_lorebook_from_card, import_st_lorebook_json
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.lorebook import match_lorebook_entries, modules_from_lore_matches


def _v3_card_with_character_book(entries: dict | None = None) -> dict:
    """Minimal v3 card raw dict with an embedded character_book."""
    return {
        "spec": "chara_card_v3",
        "spec_version": "3.0",
        "data": {
            "name": "苏韵柔",
            "description": "",
            "first_mes": "",
            "character_book": {
                "name": "隐欲 V3",
                "entries": entries or {
                    "0": {"comment": "E1", "content": "First lore.", "keys": ["key1"]},
                    "1": {"comment": "E2", "content": "Second lore.", "keys": ["key2"]},
                },
            },
        },
        "name": "",
        "description": "",
        "first_mes": "",
    }


def test_embedded_lorebook_extracts_v3_character_book():
    card = parse_character_card(_v3_card_with_character_book())

    result = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert result.name == "隐欲 V3"
    assert len(result.entries) == 2
    assert result.entries[0].content == "First lore."


def test_embedded_lorebook_extracts_legacy_top_level_character_book():
    raw = {
        "name": "Gareth",
        "character_book": {
            "name": "Legacy Book",
            "entries": [{"comment": "Old", "content": "Old lore.", "keys": ["old"]}],
        },
    }
    card = parse_character_card(raw)

    result = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert result.name == "Legacy Book"
    assert len(result.entries) == 1


def test_embedded_lorebook_extracts_world_info_shape():
    raw = {
        "spec": "chara_card_v3",
        "data": {
            "name": "Elena",
            "world_info": {
                "name": "World Book",
                "entries": [{"comment": "W", "content": "World lore.", "keys": ["world"]}],
            },
        },
        "name": "",
    }
    card = parse_character_card(raw)

    result = import_embedded_lorebook_from_card(card)

    assert result is not None
    assert result.name == "World Book"


def test_embedded_lorebook_returns_none_when_no_book():
    card = parse_character_card({"name": "Plain Card"})

    assert import_embedded_lorebook_from_card(card) is None


def test_embedded_lorebook_stable_id_on_repeated_calls():
    card = parse_character_card(_v3_card_with_character_book())

    result1 = import_embedded_lorebook_from_card(card)
    result2 = import_embedded_lorebook_from_card(card)

    assert result1 is not None
    assert result1.id == result2.id
    assert result1.id  # non-empty


def test_embedded_lorebook_id_differs_between_cards():
    card_a = parse_character_card(_v3_card_with_character_book())
    raw_b = _v3_card_with_character_book()
    raw_b["data"]["name"] = "顾时薇"
    card_b = parse_character_card(raw_b)

    id_a = import_embedded_lorebook_from_card(card_a).id
    id_b = import_embedded_lorebook_from_card(card_b).id

    assert id_a != id_b


def test_embedded_lorebook_store_round_trip_is_idempotent(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    card = parse_character_card(_v3_card_with_character_book())
    embedded = import_embedded_lorebook_from_card(card)

    lore_id1 = store.save_lorebook(embedded)
    lore_id2 = store.save_lorebook(embedded)

    assert lore_id1 == lore_id2
    lorebooks = store.list_lorebooks()
    assert len(lorebooks) == 1


def test_lorebook_imports_st_entries_dict_shape():
    lorebook = import_st_lorebook_json({
        "name": "Atlas",
        "entries": {
            "1": {"comment": "Moon", "content": "The moon is cracked.", "keys": ["moon"], "order": 2},
            "2": {"comment": "Sun", "content": "The sun is blue.", "key": "sun", "disable": True},
        },
    })

    assert lorebook.name == "Atlas"
    assert len(lorebook.entries) == 2
    assert lorebook.entries[0].title == "Moon"
    assert lorebook.entries[0].keys == ("moon",)
    assert lorebook.entries[1].enabled is False


def test_lorebook_store_round_trips_entries(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    lorebook = import_st_lorebook_json({"name": "Atlas", "entries": [{"comment": "Moon", "content": "Moon lore", "keys": ["moon"]}]})

    lorebook_id = store.save_lorebook(lorebook)
    stored = store.get_lorebook(lorebook_id)
    entries = store.list_lorebook_entries(lorebook_id)

    assert stored["name"] == "Atlas"
    assert entries[0]["title"] == "Moon"
    assert json.loads(entries[0]["keys_json"]) == ["moon"]


def test_lorebook_matcher_reports_matches_and_exclusions():
    entries = [
        {"id": "1", "title": "Moon", "content": "Moon lore", "keys_json": '["moon"]', "enabled": 1, "probability": 1, "priority": 1},
        {"id": "2", "title": "Sun", "content": "Sun lore", "keys_json": '["sun"]', "enabled": 1, "probability": 0},
        {"id": "3", "title": "Always", "content": "Always lore", "keys_json": "[]", "enabled": 1, "constant": 1, "probability": 1},
    ]

    result = match_lorebook_entries(entries, "The moon rises.")
    modules = modules_from_lore_matches(result)

    assert [m.name for m in modules] == ["lore:Moon", "lore:Always"]
    assert any(ex.title == "Sun" and ex.reason == "probability=0" for ex in result.excluded)


def test_lorebook_bad_regex_is_excluded_not_raised():
    result = match_lorebook_entries([
        {"id": "1", "title": "Broken", "content": "Broken lore", "keys_json": '["["]', "enabled": 1, "regex": 1, "probability": 1}
    ], "text")

    assert not result.matches
    assert "regex error" in result.excluded[0].reason
