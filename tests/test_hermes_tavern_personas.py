import json
import sqlite3

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.personas import import_persona_file
from plugins.hermes_tavern.importers import MAX_LOCAL_IMPORT_BYTES
from plugins.hermes_tavern.runtime import TavernRuntime


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"
    user_name = "Steven"


class Event:
    source = Source()
    text = ""


class RecordingAdapter:
    def __init__(self):
        self.messages = []

    def generate(self, messages, profile):
        del profile
        self.messages = messages
        return "recorded reply"


def test_persona_schema_migration_and_store_helpers(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)
    store.migrate()
    store.migrate()

    with sqlite3.connect(db_path) as conn:
        tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        session_cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)")}

    assert "personas" in tables
    assert "persona_id" in session_cols

    path = tmp_path / "pilot.json"
    path.write_text(
        json.dumps(
            {
                "name": "Pilot",
                "persona": "I am {{user}}, a careful pilot.",
                "api_key": "must-not-persist",
            }
        ),
        encoding="utf-8",
    )
    persona = import_persona_file(path)
    persona_id = store.save_persona(persona)

    assert store.count_personas() == 1
    assert store.get_persona(persona_id[:8])["name"] == "Pilot"
    assert store.get_persona("Pilot")["id"] == persona_id
    assert "api_key" not in store.get_persona("Pilot")["raw_json"]

    store.start_session(SESSION_KEY)
    assert store.set_session_persona(SESSION_KEY, persona_id)
    assert store.get_active_session(SESSION_KEY)["persona_id"] == persona_id
    assert store.set_session_persona(SESSION_KEY, None)
    assert store.get_active_session(SESSION_KEY)["persona_id"] is None


def test_persona_import_supports_raw_text(tmp_path):
    path = tmp_path / "traveler.txt"
    path.write_text("I am {{user}}, a patient traveler.", encoding="utf-8")

    persona = import_persona_file(path)

    assert persona.name == "traveler"
    assert persona.content == "I am {{user}}, a patient traveler."
    assert persona.source_path == str(path)
    assert persona.raw_json["format"] == "raw_text"


def test_persona_import_rejects_oversize_json(tmp_path):
    path = tmp_path / "oversize-persona.json"
    payload = {"name": "Pilot", "persona": "A" * (MAX_LOCAL_IMPORT_BYTES + 1)}
    path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="too large"):
        import_persona_file(path)


def test_persona_import_rejects_oversize_text(tmp_path):
    path = tmp_path / "oversize-persona.txt"
    path.write_text("A" * (MAX_LOCAL_IMPORT_BYTES + 1), encoding="utf-8")

    with pytest.raises(ValueError, match="too large"):
        import_persona_file(path)


@pytest.mark.asyncio
async def test_persona_runtime_commands_import_list_inspect_use_debug_clear(tmp_path):
    path = tmp_path / "navigator.json"
    path.write_text(
        json.dumps({"name": "Navigator", "persona": "I am {{user}}, a star navigator."}),
        encoding="utf-8",
    )
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    imported = await runtime.handle_command(
        RPCommand("persona", ["import", str(path)], "/rp persona import"),
        Event(),
    )
    listed = await runtime.handle_command(RPCommand("persona", ["list"], "/rp persona list"), Event())
    inspected = await runtime.handle_command(
        RPCommand("persona", ["inspect", "Navigator"], "/rp persona inspect Navigator"),
        Event(),
    )
    bound = await runtime.handle_command(
        RPCommand("persona", ["use", "Navigator"], "/rp persona use Navigator"),
        Event(),
    )
    debug = await runtime.handle_command(RPCommand("persona", ["debug"], "/rp persona debug"), Event())
    cleared = await runtime.handle_command(RPCommand("persona", ["clear"], "/rp persona clear"), Event())

    assert "Imported Hermes Tavern persona: Navigator" in imported
    assert "Navigator" in listed
    assert "preview:" in inspected
    assert "raw_json" not in inspected
    assert '"name"' not in inspected
    assert "persona bound" in bound
    assert "module: persona:Navigator" in debug
    assert "I am {{user}}, a star navigator." in debug
    assert "persona cleared" in cleared
    assert store.get_active_session(SESSION_KEY)["persona_id"] is None


@pytest.mark.asyncio
async def test_persona_new_creates_reusable_persona(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)

    created = await runtime.handle_command(
        RPCommand("persona", ["new", "Pilot", "I", "am", "{{user}},", "a", "careful", "pilot."], "/rp persona new"),
        Event(),
    )
    listed = await runtime.handle_command(RPCommand("persona", ["list"], "/rp persona list"), Event())

    assert "persona created: Pilot" in created
    assert "use: /rp persona use" in created
    assert "Pilot" in listed
    assert "careful pilot" in listed


@pytest.mark.asyncio
async def test_persona_temp_creates_and_binds_to_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    bound = await runtime.handle_command(
        RPCommand("persona", ["temp", "I", "am", "{{user}},", "the", "pilot."], "/rp persona temp"),
        Event(),
    )
    debug = await runtime.handle_command(RPCommand("persona", ["debug"], "/rp persona debug"), Event())

    assert "temporary persona bound" in bound
    assert store.get_active_session(SESSION_KEY)["persona_id"]
    assert "module: persona:temporary" in debug
    assert "I am {{user}}, the pilot." in debug


@pytest.mark.asyncio
async def test_persona_prompt_injection_macro_expansion_and_clear(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    persona_id = store.save_persona(
        import_persona_file(
            _write_text(tmp_path / "pilot.txt", "I am {{user}}, a careful pilot for {{char}}.")
        )
    )
    store.set_session_persona(SESSION_KEY, persona_id)

    prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    store.set_session_persona(SESSION_KEY, None)
    cleared_prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "persona:" in prompt
    assert "persona:pilot" in prompt
    assert "I am Steven, a careful pilot for Alice." in prompt
    assert "persona:pilot" not in cleared_prompt


@pytest.mark.asyncio
async def test_persona_active_generation_receives_module(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    adapter = RecordingAdapter()
    runtime = TavernRuntime(store, hermes_adapter=adapter)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    persona_id = store.save_persona(
        import_persona_file(_write_text(tmp_path / "pilot.txt", "I am {{user}}, the pilot."))
    )
    store.set_session_persona(SESSION_KEY, persona_id)
    store.set_session_adapter_mode(SESSION_KEY, "hermes")
    store.set_session_live_confirmed(SESSION_KEY, True)

    event = Event()
    event.text = "Hello"
    reply = await runtime.handle_active_message(event)

    assert reply == "recorded reply"
    assert any(m["role"] == "system" and "I am Steven, the pilot." in m["content"] for m in adapter.messages)


@pytest.mark.asyncio
async def test_persona_pagination_and_inspect_do_not_emit_raw_json(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = TavernRuntime(store)
    for idx in range(3):
        path = tmp_path / f"persona-{idx}.json"
        path.write_text(
            json.dumps(
                {
                    "name": f"Persona {idx}",
                    "persona": f"Persona body {idx}",
                    "token": "must-not-show",
                }
            ),
            encoding="utf-8",
        )
        store.save_persona(import_persona_file(path))

    page_1 = await runtime.handle_command(RPCommand("persona", ["list", "2", "1"], "/rp persona list 2 1"), Event())
    page_2 = await runtime.handle_command(RPCommand("persona", ["list", "2", "2"], "/rp persona list 2 2"), Event())
    inspected = await runtime.handle_command(
        RPCommand("persona", ["inspect", "Persona", "0"], "/rp persona inspect Persona 0"),
        Event(),
    )

    assert "page 1/2" in page_1
    assert "next: /rp persona list 2 2" in page_1
    assert "page 2/2" in page_2
    assert "prev: /rp persona list 2 1" in page_2
    assert "raw_json" not in inspected
    assert "token" not in inspected
    assert "must-not-show" not in inspected
    assert "{" not in inspected and "}" not in inspected


def _write_text(path, text):
    path.write_text(text, encoding="utf-8")
    return path
