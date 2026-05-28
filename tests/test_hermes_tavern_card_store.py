import json
import sqlite3

from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import load_card_file, parse_character_card


def test_save_card_persists_character_json(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)
    store.migrate()
    card = parse_character_card({"name": "Alice", "description": "Scholar"})

    card_id = store.save_card(card)

    assert card_id == card.id
    with sqlite3.connect(db_path) as conn:
        row = conn.execute("SELECT id, name, data_json FROM cards").fetchone()
    assert row[0] == card.id
    assert row[1] == "Alice"
    assert json.loads(row[2])["description"] == "Scholar"


def test_list_cards_returns_saved_names(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(parse_character_card({"name": "Alice"}))
    store.save_card(parse_character_card({"name": "Bob"}))

    cards = store.list_cards()

    assert [card["name"] for card in cards] == ["Alice", "Bob"]


def test_get_card_by_id_and_exact_name(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    card = parse_character_card({"name": "Alice", "description": "Scholar"})
    store.save_card(card)

    by_id = store.get_card(card.id)
    by_name = store.get_card("Alice")

    assert by_id["id"] == card.id
    assert by_name["id"] == card.id
    assert json.loads(by_id["data_json"])["name"] == "Alice"


def test_save_card_persists_source_path(tmp_path):
    card_file = tmp_path / "alice.json"
    card_file.write_text(json.dumps({"name": "Alice"}))
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()

    card = load_card_file(card_file)
    store.save_card(card)

    row = store.get_card(card.id)
    data = json.loads(row["data_json"])
    assert data["source_path"] == str(card_file)

