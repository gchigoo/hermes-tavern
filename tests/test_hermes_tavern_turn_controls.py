"""Tests for Hermes Tavern Phase 14 — turn control commands."""

import json

import pytest

from plugins.hermes_tavern.adapters import FAKE_ADAPTER_REPLY
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


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


def _make_runtime(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.save_card(
        parse_character_card(
            {"name": "Alice", "description": "Scholar", "first_mes": "Hello there."}
        )
    )
    return TavernRuntime(store), store


# ---------------------------------------------------------------------------
# TavernStore helpers
# ---------------------------------------------------------------------------


def test_get_recent_messages_includes_id(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "user", "hello")
    messages = store.get_recent_messages(session["id"])
    assert "id" in messages[0]
    assert messages[0]["id"]


def test_delete_last_assistant_message_removes_last(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "user", "hi")
    store.append_message(session["id"], "assistant", "reply")
    deleted_id = store.delete_last_assistant_message(session["id"])
    assert deleted_id is not None
    messages = store.get_recent_messages(session["id"])
    assert len(messages) == 1
    assert messages[0]["role"] == "user"


def test_delete_last_assistant_message_noop_when_none(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "user", "hi")
    result = store.delete_last_assistant_message(session["id"])
    assert result is None
    assert len(store.get_recent_messages(session["id"])) == 1


def test_delete_last_assistant_message_only_removes_last(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "assistant", "first reply")
    store.append_message(session["id"], "user", "turn2")
    store.append_message(session["id"], "assistant", "second reply")
    store.delete_last_assistant_message(session["id"])
    messages = store.get_recent_messages(session["id"])
    assert len(messages) == 2
    assert messages[0]["content"] == "first reply"


def test_delete_last_user_assistant_turn_removes_pair(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "user", "turn1")
    store.append_message(session["id"], "assistant", "reply1")
    store.append_message(session["id"], "user", "turn2")
    store.append_message(session["id"], "assistant", "reply2")
    deleted = store.delete_last_user_assistant_turn(session["id"])
    assert deleted == 2
    messages = store.get_recent_messages(session["id"])
    assert len(messages) == 2
    assert messages[-1]["content"] == "reply1"


def test_delete_last_user_assistant_turn_user_only(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "user", "turn1")
    store.append_message(session["id"], "assistant", "reply1")
    store.append_message(session["id"], "user", "turn2_no_reply")
    deleted = store.delete_last_user_assistant_turn(session["id"])
    assert deleted == 1
    messages = store.get_recent_messages(session["id"])
    assert len(messages) == 2
    assert messages[-1]["content"] == "reply1"


def test_delete_last_user_assistant_turn_noop_on_empty(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    result = store.delete_last_user_assistant_turn(session["id"])
    assert result == 0


def test_delete_last_user_assistant_turn_assistant_only(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "assistant", "greeting")
    result = store.delete_last_user_assistant_turn(session["id"])
    assert result == 0
    assert len(store.get_recent_messages(session["id"])) == 1


def test_update_last_user_message_updates_content(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "user", "original")
    store.append_message(session["id"], "assistant", "reply")
    updated_id = store.update_last_user_message(session["id"], "edited text")
    assert updated_id is not None
    messages = store.get_recent_messages(session["id"])
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert user_msgs[-1]["content"] == "edited text"


def test_update_last_user_message_noop_when_no_user_message(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    result = store.update_last_user_message(session["id"], "something")
    assert result is None


def test_update_last_user_message_updates_most_recent(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "user", "first")
    store.append_message(session["id"], "user", "second")
    store.update_last_user_message(session["id"], "updated")
    messages = store.get_recent_messages(session["id"])
    assert messages[0]["content"] == "first"
    assert messages[1]["content"] == "updated"


def test_delete_assistant_after_last_user_message_removes_only_turn_reply(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    store.append_message(session["id"], "assistant", "greeting")
    store.append_message(session["id"], "user", "turn")
    store.append_message(session["id"], "assistant", "reply")
    deleted_id = store.delete_assistant_after_last_user_message(session["id"])
    assert deleted_id is not None
    messages = store.get_recent_messages(session["id"])
    assert [m["content"] for m in messages] == ["greeting", "turn"]


def test_get_recent_messages_returns_latest_window_in_chronological_order(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    session = store.start_session("test-key")
    for i in range(5):
        store.append_message(session["id"], "user", f"turn-{i}")
    messages = store.get_recent_messages(session["id"], limit=2)
    assert [m["content"] for m in messages] == ["turn-3", "turn-4"]


# ---------------------------------------------------------------------------
# /rp history
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_history_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(RPCommand("history", [], "/rp history"), Event())
    assert "No active" in response


@pytest.mark.asyncio
async def test_history_shows_messages(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MsgEvent(Event):
        text = "What happens next?"

    await runtime.handle_active_message(MsgEvent())
    response = await runtime.handle_command(RPCommand("history", [], "/rp history"), Event())
    assert "session history" in response
    assert "user" in response
    assert "assistant" in response


@pytest.mark.asyncio
async def test_history_with_limit(tmp_path):
    runtime, _ = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("history", ["3"], "/rp history 3"), Event()
    )
    assert "session history" in response


@pytest.mark.asyncio
async def test_history_invalid_limit(tmp_path):
    runtime, _ = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("history", ["abc"], "/rp history abc"), Event()
    )
    assert "Usage" in response


@pytest.mark.asyncio
async def test_history_includes_short_id(tmp_path):
    runtime, _ = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(RPCommand("history", [], "/rp history"), Event())
    # Short id bracketed format
    assert "[" in response and "]" in response


# ---------------------------------------------------------------------------
# /rp retry
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_retry_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(RPCommand("retry", [], "/rp retry"), Event())
    assert "No active" in response


@pytest.mark.asyncio
async def test_retry_regenerates_assistant_reply(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MsgEvent(Event):
        text = "What happens next?"

    await runtime.handle_active_message(MsgEvent())
    session = store.get_active_session(SESSION_KEY)
    msgs_before = store.get_recent_messages(session["id"])
    assistant_before = [m for m in msgs_before if m["role"] == "assistant"]

    response = await runtime.handle_command(RPCommand("retry", [], "/rp retry"), Event())
    assert FAKE_ADAPTER_REPLY in response

    msgs_after = store.get_recent_messages(session["id"])
    assistant_after = [m for m in msgs_after if m["role"] == "assistant"]
    # Old assistant removed, new one appended — net count unchanged
    assert len(assistant_after) == len(assistant_before)
    # User messages preserved
    user_after = [m for m in msgs_after if m["role"] == "user"]
    assert any(m["content"] == "What happens next?" for m in user_after)


@pytest.mark.asyncio
async def test_retry_no_assistant_reply(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session = store.get_active_session(SESSION_KEY)
    # Remove the greeting so no assistant message exists
    store.delete_last_assistant_message(session["id"])
    response = await runtime.handle_command(RPCommand("retry", [], "/rp retry"), Event())
    assert "No assistant reply" in response


@pytest.mark.asyncio
async def test_retry_no_user_message_after_delete(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    # Session has only greeting (assistant). Retry should not treat it as a user-turn reply.
    response = await runtime.handle_command(RPCommand("retry", [], "/rp retry"), Event())
    assert "No assistant reply" in response
    # Greeting is not a user-turn reply and should be preserved.
    session = store.get_active_session(SESSION_KEY)
    assert session is not None
    assert store.get_recent_messages(session["id"])[-1]["content"] == "Hello there."


@pytest.mark.asyncio
async def test_retry_preserves_old_reply_as_swipe_candidate(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MsgEvent(Event):
        text = "What happens next?"

    await runtime.handle_active_message(MsgEvent())
    runtime._run_generation_pipeline = lambda session, user_text, history, event=None: "second candidate"

    response = await runtime.handle_command(RPCommand("retry", [], "/rp retry"), Event())

    assert "second candidate" in response
    session = store.get_active_session(SESSION_KEY)
    messages = store.get_recent_messages(session["id"])
    metadata = json.loads(messages[-1]["metadata_json"])
    assert metadata["swipes"] == [FAKE_ADAPTER_REPLY, "second candidate"]
    assert metadata["active_swipe"] == 1


@pytest.mark.asyncio
async def test_swipe_list_add_and_use_last_turn_candidates(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MsgEvent(Event):
        text = "What happens next?"

    await runtime.handle_active_message(MsgEvent())
    generated = iter(["candidate two", "candidate three"])
    runtime._run_generation_pipeline = lambda session, user_text, history, event=None: next(generated)

    added = await runtime.handle_command(RPCommand("swipe", ["add"], "/rp swipe add"), Event())
    listed = await runtime.handle_command(RPCommand("swipe", ["list"], "/rp swipe list"), Event())
    selected = await runtime.handle_command(RPCommand("swipe", ["use", "0"], "/rp swipe use 0"), Event())

    assert "Swipe 1 added and selected" in added
    assert "candidate two" in added
    assert "Swipes for last turn: 2 candidate(s), active 1" in listed
    assert "[0]" in listed and "[1]" in listed
    assert "Swipe 0 selected" in selected
    session = store.get_active_session(SESSION_KEY)
    messages = store.get_recent_messages(session["id"])
    assert messages[-1]["content"] == FAKE_ADAPTER_REPLY
    metadata = json.loads(messages[-1]["metadata_json"])
    assert metadata["active_swipe"] == 0
    assert metadata["swipes"] == [FAKE_ADAPTER_REPLY, "candidate two"]


@pytest.mark.asyncio
async def test_swipe_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(RPCommand("swipe", ["list"], "/rp swipe list"), Event())
    assert "No active" in response


# ---------------------------------------------------------------------------
# /rp undo
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_undo_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(RPCommand("undo", [], "/rp undo"), Event())
    assert "No active" in response


@pytest.mark.asyncio
async def test_undo_removes_last_turn(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MsgEvent(Event):
        text = "Turn 1"

    await runtime.handle_active_message(MsgEvent())
    session = store.get_active_session(SESSION_KEY)
    count_before = len(store.get_recent_messages(session["id"]))

    response = await runtime.handle_command(RPCommand("undo", [], "/rp undo"), Event())
    assert "undo" in response.lower()
    count_after = len(store.get_recent_messages(session["id"]))
    assert count_after < count_before


@pytest.mark.asyncio
async def test_undo_noop_when_no_user_messages(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    # Remove the greeting so only assistant, no user
    session = store.get_active_session(SESSION_KEY)
    store.delete_last_assistant_message(session["id"])
    response = await runtime.handle_command(RPCommand("undo", [], "/rp undo"), Event())
    assert "No turn" in response


@pytest.mark.asyncio
async def test_undo_multiple_turns(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class T1(Event):
        text = "Turn 1"

    class T2(Event):
        text = "Turn 2"

    await runtime.handle_active_message(T1())
    await runtime.handle_active_message(T2())
    session = store.get_active_session(SESSION_KEY)
    count_before = len(store.get_recent_messages(session["id"]))

    await runtime.handle_command(RPCommand("undo", [], "/rp undo"), Event())
    count_mid = len(store.get_recent_messages(session["id"]))
    assert count_mid < count_before

    await runtime.handle_command(RPCommand("undo", [], "/rp undo"), Event())
    count_after = len(store.get_recent_messages(session["id"]))
    assert count_after < count_mid


# ---------------------------------------------------------------------------
# /rp edit last
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_edit_last_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(
        RPCommand("edit", ["last", "text"], "/rp edit last text"), Event()
    )
    assert "No active" in response


@pytest.mark.asyncio
async def test_edit_last_usage_missing_last(tmp_path):
    runtime, _ = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("edit", ["wrongsub"], "/rp edit wrongsub"), Event()
    )
    assert "Usage" in response


@pytest.mark.asyncio
async def test_edit_last_usage_empty_text(tmp_path):
    runtime, _ = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("edit", ["last"], "/rp edit last"), Event()
    )
    assert "Usage" in response


@pytest.mark.asyncio
async def test_edit_last_updates_user_message_and_regenerates(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MsgEvent(Event):
        text = "Original message"

    await runtime.handle_active_message(MsgEvent())

    response = await runtime.handle_command(
        RPCommand("edit", ["last", "Edited", "message"], "/rp edit last Edited message"),
        Event(),
    )
    assert FAKE_ADAPTER_REPLY in response

    session = store.get_active_session(SESSION_KEY)
    messages = store.get_recent_messages(session["id"])
    user_msgs = [m for m in messages if m["role"] == "user"]
    assert user_msgs[-1]["content"] == "Edited message"


@pytest.mark.asyncio
async def test_edit_last_no_user_message(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    # Only greeting (assistant), no user messages yet
    response = await runtime.handle_command(
        RPCommand("edit", ["last", "something"], "/rp edit last something"), Event()
    )
    assert "No user message" in response
    assert store.get_recent_messages(store.get_active_session(SESSION_KEY)["id"])[-1]["content"] == "Hello there."


@pytest.mark.asyncio
async def test_edit_last_replaces_assistant_reply(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    class MsgEvent(Event):
        text = "Hello"

    await runtime.handle_active_message(MsgEvent())
    session = store.get_active_session(SESSION_KEY)
    msgs_before = store.get_recent_messages(session["id"])
    assistant_before = [m for m in msgs_before if m["role"] == "assistant"]

    await runtime.handle_command(
        RPCommand("edit", ["last", "Revised hello"], "/rp edit last Revised hello"),
        Event(),
    )
    msgs_after = store.get_recent_messages(session["id"])
    assistant_after = [m for m in msgs_after if m["role"] == "assistant"]
    # Net assistant count should be same: old reply removed, new appended
    assert len(assistant_after) == len(assistant_before)


# ---------------------------------------------------------------------------
# Help text
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_help_includes_turn_control_commands(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(RPCommand("help", [], "/rp"), Event())
    assert "/rp history [limit]" in response
    assert "/rp retry" in response
    assert "/rp swipe list" in response
    assert "/rp undo" in response
    assert "/rp edit last <text>" in response
