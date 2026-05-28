import sqlite3

import pytest

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.importers.cards import parse_character_card
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


def _started_runtime(tmp_path, *, adapter=None):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store, hermes_adapter=adapter)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    return store, runtime


def test_note_schema_migration_and_store_helpers(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)
    store.migrate()
    store.migrate()

    with sqlite3.connect(db_path) as conn:
        session_cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)")}

    assert "note_text" in session_cols
    assert "note_position" in session_cols
    assert "note_frequency" in session_cols
    assert "note_every_n" in session_cols

    store.start_session(SESSION_KEY)
    assert store.set_session_note(SESSION_KEY, "Remember {{char}} trusts {{user}}.")
    session = store.get_active_session(SESSION_KEY)
    assert session["note_text"] == "Remember {{char}} trusts {{user}}."
    assert session["note_position"] == "before_user"
    assert session["note_frequency"] == "always"
    assert session["note_every_n"] == 3

    assert store.set_session_note_position(SESSION_KEY, "after_history")
    assert store.get_active_session(SESSION_KEY)["note_position"] == "after_history"
    assert store.set_session_note_frequency(SESSION_KEY, "every_n", every_n=4)
    session = store.get_active_session(SESSION_KEY)
    assert session["note_frequency"] == "every_n"
    assert session["note_every_n"] == 4

    assert store.clear_session_note(SESSION_KEY)
    assert store.get_active_session(SESSION_KEY)["note_text"] == ""


@pytest.mark.asyncio
async def test_note_runtime_commands_set_inspect_position_frequency_clear(tmp_path):
    store, runtime = _started_runtime(tmp_path)

    no_session = await TavernRuntime(TavernStore(tmp_path / "other.sqlite3")).handle_command(
        RPCommand("note", ["inspect"], "/rp note inspect"),
        Event(),
    )
    set_result = await runtime.handle_command(
        RPCommand("note", ["set", "Keep", "the", "scene", "quiet."], "/rp note set Keep the scene quiet."),
        Event(),
    )
    inspect = await runtime.handle_command(RPCommand("note", ["inspect"], "/rp note inspect"), Event())
    positioned = await runtime.handle_command(
        RPCommand("note", ["position", "after_history"], "/rp note position after_history"),
        Event(),
    )
    current_position = await runtime.handle_command(RPCommand("note", ["position"], "/rp note position"), Event())
    frequency = await runtime.handle_command(
        RPCommand("note", ["frequency", "every_n", "4"], "/rp note frequency every_n 4"),
        Event(),
    )
    current_frequency = await runtime.handle_command(RPCommand("note", ["frequency"], "/rp note frequency"), Event())
    cleared = await runtime.handle_command(RPCommand("note", ["clear"], "/rp note clear"), Event())

    assert "No active Hermes Tavern session" in no_session
    assert "Author note saved" in set_result
    assert "Author note" in inspect
    assert "Keep the scene quiet." in inspect
    assert "raw_json" not in inspect
    assert "note position: after_history" in positioned
    assert "position: after_history" in current_position
    assert "note frequency: every_n 4" in frequency
    assert "frequency: every_n 4" in current_frequency
    assert "Author note cleared" in cleared
    assert store.get_active_session(SESSION_KEY)["note_text"] == ""


@pytest.mark.asyncio
async def test_note_prompt_injection_macro_expansion_and_clear(tmp_path):
    store, runtime = _started_runtime(tmp_path)
    store.set_session_note(SESSION_KEY, "Author note: {{char}} should notice {{user}}.")

    prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    store.clear_session_note(SESSION_KEY)
    cleared_prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "note:author" in prompt
    assert "Author note: Alice should notice Steven." in prompt
    assert "note:author" not in cleared_prompt


@pytest.mark.asyncio
async def test_note_active_generation_receives_module(tmp_path):
    adapter = RecordingAdapter()
    store, runtime = _started_runtime(tmp_path, adapter=adapter)
    store.set_session_adapter_mode(SESSION_KEY, "hermes")
    store.set_session_live_confirmed(SESSION_KEY, True)
    store.set_session_note(SESSION_KEY, "Stay close to {{char}}.")

    event = Event()
    event.text = "Hello"
    reply = await runtime.handle_active_message(event)

    assert reply == "recorded reply"
    assert any(m["role"] == "system" and "Stay close to Alice." in m["content"] for m in adapter.messages)


@pytest.mark.asyncio
async def test_note_every_n_frequency_is_deterministic(tmp_path):
    store, runtime = _started_runtime(tmp_path)
    store.set_session_note(SESSION_KEY, "Only every third user turn.")
    store.set_session_note_frequency(SESSION_KEY, "every_n", every_n=3)

    first_prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    store.append_message(store.get_active_session(SESSION_KEY)["id"], "user", "turn 1")
    store.append_message(store.get_active_session(SESSION_KEY)["id"], "assistant", "reply 1")
    second_prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    store.append_message(store.get_active_session(SESSION_KEY)["id"], "user", "turn 2")
    store.append_message(store.get_active_session(SESSION_KEY)["id"], "assistant", "reply 2")
    third_prompt = await runtime.handle_command(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "note:author" not in first_prompt
    assert "note:author" not in second_prompt
    assert "note:author" in third_prompt
