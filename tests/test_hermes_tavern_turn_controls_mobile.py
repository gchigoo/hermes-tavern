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


def test_edit_last_requires_replacement_text(tmp_path):
    runtime, _, _ = _runtime_with_turn(tmp_path)
    response = runtime.handle_command_sync(
        RPCommand("edit", ["last"], "/rp edit last"),
        Event(),
    )
    assert "Usage: /rp edit last <text>" in response
    assert len(response) < 200

def test_turn_controls_forward_event_to_generation_pipeline(tmp_path):
    runtime, _, _ = _runtime_with_turn(tmp_path)
    captured_events = []

    def mock_pipeline(session, user_text, history, event=None):
        captured_events.append(event)
        return "regenerated reply"

    runtime._run_generation_pipeline = mock_pipeline
    test_event = Event()

    # 1. retry forwards event
    runtime.handle_command_sync(RPCommand("retry", [], "/rp retry"), test_event)
    assert len(captured_events) == 1
    assert captured_events[0] is test_event

    # 2. swipe add forwards event
    runtime.handle_command_sync(RPCommand("swipe", ["add"], "/rp swipe add"), test_event)
    assert len(captured_events) == 2
    assert captured_events[1] is test_event

    # 3. edit last forwards event
    runtime.handle_command_sync(RPCommand("edit", ["last", "new", "prompt"], "/rp edit last new prompt"), test_event)
    assert len(captured_events) == 3
    assert captured_events[2] is test_event


def test_swipe_use_invokes_auto_speak_when_voice_enabled(tmp_path):
    spoken = []

    def mock_tts(text):
        spoken.append(text)
        return {
            "success": True,
            "provider": "mock-tts",
            "media_tag": 'MEDIA:"test.mp3"',
        }

    runtime, _, _ = _runtime_with_turn(tmp_path)
    runtime.tts_renderer = mock_tts
    test_event = Event()

    # Add candidate 1
    runtime._run_generation_pipeline = lambda session, user_text, history, event=None: "candidate two"
    runtime.handle_command_sync(RPCommand("swipe", ["add"], "/rp swipe add"), test_event)

    # Enable voice
    runtime.handle_command_sync(RPCommand("voice", ["on"], "/rp voice on"), test_event)

    # Use swipe 0
    res = runtime.handle_command_sync(RPCommand("swipe", ["use", "0"], "/rp swipe use 0"), test_event)
    assert "Swipe 0 selected" in res
    assert "Hermes Tavern speak: audio ready (mock-tts)." in res
    assert 'MEDIA:"test.mp3"' in res

    # Next swipe 1
    res_next = runtime.handle_command_sync(RPCommand("swipe", ["next"], "/rp swipe next"), test_event)
    assert "Swipe 1 selected" in res_next
    assert "Hermes Tavern speak: audio ready (mock-tts)." in res_next
    assert 'MEDIA:"test.mp3"' in res_next

