"""Tests for Hermes Tavern card search."""

from __future__ import annotations

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
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


def test_card_search_matches_name_tags_and_description(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({
        "name": "Lyra",
        "description": "A bard from Aldenmere.",
        "tags": ["fantasy", "music"],
    }))
    store.save_card(parse_character_card({
        "name": "Mira",
        "description": "A city detective.",
        "tags": ["noir"],
    }))
    runtime = TavernRuntime(store)

    by_tag = runtime.handle_command_sync(
        RPCommand("card", ["search", "fantasy"], "/rp card search fantasy"),
        Event(),
    )
    by_desc = runtime.handle_command_sync(
        RPCommand("card", ["search", "city", "detective"], "/rp card search city detective"),
        Event(),
    )
    missing = runtime.handle_command_sync(
        RPCommand("card", ["search", "space"], "/rp card search space"),
        Event(),
    )

    assert "Lyra" in by_tag
    assert "Mira" not in by_tag
    assert "start: /rp start" in by_tag
    assert "Mira" in by_desc
    assert "No Hermes Tavern character cards matched: space" in missing


def test_card_search_requires_query(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = runtime.handle_command_sync(
        RPCommand("card", ["search"], "/rp card search"),
        Event(),
    )

    assert response == "Usage: /rp card search <query>"


def test_card_search_skips_malformed_metadata_and_matches_healthy_description(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({
        "name": "Healthy Card",
        "description": "Carries the verdant signal.",
    }))
    corrupt_id = store.save_card(parse_character_card({
        "name": "Corrupt Card",
        "description": "This metadata must not be searchable.",
    }))
    with store.connect() as conn:
        conn.execute(
            "UPDATE cards SET data_json = ? WHERE id = ?",
            ("{", corrupt_id),
        )
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["search", "verdant", "signal"], "/rp card search verdant signal"),
        Event(),
    )

    assert "Healthy Card" in response
    assert "Corrupt Card" not in response


@pytest.mark.parametrize("data_json", ["null", "[]", '"metadata"', "42"])
def test_card_search_treats_non_object_metadata_as_empty(tmp_path, data_json):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    card_id = store.save_card(parse_character_card({
        "name": "Payload Hero",
        "tags": ["should-disappear"],
    }))
    with store.connect() as conn:
        conn.execute(
            "UPDATE cards SET data_json = ? WHERE id = ?",
            (data_json, card_id),
        )
    runtime = TavernRuntime(store)

    response = runtime.handle_command_sync(
        RPCommand("card", ["search", "Payload", "Hero"], "/rp card search Payload Hero"),
        Event(),
    )

    assert "Payload Hero — no tags" in response
    assert "should-disappear" not in response
