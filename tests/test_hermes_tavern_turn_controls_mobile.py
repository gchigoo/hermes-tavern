"""Mobile output polish tests for Hermes Tavern turn controls."""

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


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


def _runtime_with_turn(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session(SESSION_KEY)
    store.append_message(session["id"], "user", "hello")
    store.append_message(session["id"], "assistant", "old reply")
    runtime = TavernRuntime(store)
    runtime._run_generation_pipeline = lambda session, user_text, history, event=None: "new reply"
    return runtime, store, session


def test_retry_output_is_mobile_friendly(tmp_path):
    runtime, _, _ = _runtime_with_turn(tmp_path)

    response = runtime.handle_command_sync(RPCommand("retry", [], "/rp retry"), Event())

    assert len(response) < 500
    assert response.startswith("Hermes Tavern retry:")
    assert "new reply" in response
    assert "retry again: /rp retry" in response


def test_undo_output_is_mobile_friendly(tmp_path):
    runtime, _, _ = _runtime_with_turn(tmp_path)

    response = runtime.handle_command_sync(RPCommand("undo", [], "/rp undo"), Event())

    assert len(response) < 200
    assert response == "Undid last turn (removed 2 messages).\nundo again: /rp undo"


def test_edit_last_output_is_mobile_friendly(tmp_path):
    runtime, store, session = _runtime_with_turn(tmp_path)
    before = len(store.get_recent_messages(session["id"]))

    response = runtime.handle_command_sync(
        RPCommand("edit", ["last", "revised", "hello"], "/rp edit last revised hello"),
        Event(),
    )

    assert len(response) < 500
    assert response.startswith("Hermes Tavern edit:")
    assert "new reply" in response
    assert "edit again: /rp edit last <text>" in response
    assert len(store.get_recent_messages(session["id"])) == before


def test_turn_control_error_messages_stay_concise(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    no_active_messages = [
        runtime.handle_command_sync(RPCommand("retry", [], "/rp retry"), Event()),
        runtime.handle_command_sync(RPCommand("undo", [], "/rp undo"), Event()),
        runtime.handle_command_sync(
            RPCommand("edit", ["last", "text"], "/rp edit last text"), Event()
        ),
    ]

    runtime, store, session = _runtime_with_turn(tmp_path)
    store.delete_last_user_assistant_turn(session["id"])
    empty_session_messages = [
        runtime.handle_command_sync(RPCommand("retry", [], "/rp retry"), Event()),
        runtime.handle_command_sync(RPCommand("undo", [], "/rp undo"), Event()),
        runtime.handle_command_sync(
            RPCommand("edit", ["last", "text"], "/rp edit last text"), Event()
        ),
    ]

    messages = no_active_messages + empty_session_messages
    assert messages == [
        "No active Hermes Tavern session.",
        "No active Hermes Tavern session.",
        "No active Hermes Tavern session.",
        "No assistant reply to retry.",
        "No turn to undo.",
        "No user message to edit.",
    ]
    assert all(len(message) < 200 for message in messages)
    assert all(len(message.splitlines()) <= 3 for message in messages)
