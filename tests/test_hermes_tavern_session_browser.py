"""Tests for Hermes Tavern Phase 15 — session browser and multi-session v1."""

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


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


class SourceUser2:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-2"


class EventUser2:
    source = SourceUser2()
    text = ""


SESSION_KEY_USER2 = "telegram:chat:chat-1:thread:main:user:user-2"


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
# Schema / migration
# ---------------------------------------------------------------------------


def test_sessions_title_column_exists_after_migrate(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    with store.connect() as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
    assert "title" in cols


def test_sessions_scope_key_column_exists_after_migrate(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    with store.connect() as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
    assert "scope_key" in cols


def test_start_session_sets_scope_key(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    assert session["scope_key"] == "mykey"


# ---------------------------------------------------------------------------
# list_sessions_for_scope
# ---------------------------------------------------------------------------


def test_list_sessions_for_scope_returns_active_sessions(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("mykey", card_id="alice")
    sessions = store.list_sessions_for_scope("mykey")
    assert len(sessions) == 1
    assert sessions[0]["status"] == "active"


def test_list_sessions_for_scope_default_excludes_archived(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("mykey")
    store.archive_active_session("mykey")
    sessions = store.list_sessions_for_scope("mykey")
    assert len(sessions) == 0


def test_list_sessions_for_scope_all_includes_archived(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("mykey")
    store.archive_active_session("mykey")
    sessions = store.list_sessions_for_scope("mykey", include_all=True)
    assert len(sessions) >= 1
    statuses = {s["status"] for s in sessions}
    assert "archived" in statuses


def test_list_sessions_for_scope_all_includes_ended(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("mykey")
    store.end_session("mykey")
    sessions = store.list_sessions_for_scope("mykey", include_all=True)
    assert any(s["status"] == "ended" for s in sessions)


def test_list_sessions_for_scope_default_excludes_ended(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("mykey")
    store.end_session("mykey")
    sessions = store.list_sessions_for_scope("mykey")
    assert len(sessions) == 0


def test_list_sessions_for_scope_includes_cloned_sessions(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey", card_id="alice")
    store.clone_session(session["id"], "mykey", title="Branch")
    sessions = store.list_sessions_for_scope("mykey")
    assert len(sessions) == 2


def test_list_sessions_for_scope_isolates_different_scopes(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("scope-a")
    store.start_session("scope-b")
    assert len(store.list_sessions_for_scope("scope-a")) == 1
    assert len(store.list_sessions_for_scope("scope-b")) == 1


# ---------------------------------------------------------------------------
# rename_session
# ---------------------------------------------------------------------------


def test_rename_session_sets_title(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    store.rename_session(session["id"], "My Story")
    updated = store.get_active_session("mykey")
    assert updated["title"] == "My Story"


def test_rename_session_allows_empty_to_clear(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    store.rename_session(session["id"], "Story")
    store.rename_session(session["id"], "")
    updated = store.get_active_session("mykey")
    assert not updated.get("title")


# ---------------------------------------------------------------------------
# archive_active_session
# ---------------------------------------------------------------------------


def test_archive_active_session_changes_status_to_archived(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("mykey")
    result = store.archive_active_session("mykey")
    assert result is True
    assert store.get_active_session("mykey") is None


def test_archive_active_session_frees_key_for_new_start(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    first = store.start_session("mykey")
    store.archive_active_session("mykey")
    second = store.start_session("mykey")
    assert second["id"] != first["id"]
    assert store.get_active_session("mykey") is not None


def test_archive_active_session_returns_false_when_no_active(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    result = store.archive_active_session("mykey")
    assert result is False


def test_archived_session_visible_in_list_all(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    first = store.start_session("mykey")
    store.archive_active_session("mykey")
    all_sessions = store.list_sessions_for_scope("mykey", include_all=True)
    ids = [s["id"] for s in all_sessions]
    assert first["id"] in ids


# ---------------------------------------------------------------------------
# clone_session
# ---------------------------------------------------------------------------


def test_clone_session_creates_new_session_with_same_config(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey", card_id="alice")
    cloned = store.clone_session(session["id"], "mykey")
    assert cloned["id"] != session["id"]
    assert cloned["card_id"] == "alice"
    assert cloned["status"] == "active"
    assert cloned["scope_key"] == "mykey"


def test_clone_session_with_title(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    cloned = store.clone_session(session["id"], "mykey", title="Branch A")
    assert cloned["title"] == "Branch A"


def test_clone_session_copies_messages(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    store.append_message(session["id"], "user", "hi")
    store.append_message(session["id"], "assistant", "hey")
    cloned = store.clone_session(session["id"], "mykey")
    clone_messages = store.get_recent_messages(cloned["id"], limit=50)
    assert len(clone_messages) == 2
    assert clone_messages[0]["content"] == "hi"
    assert clone_messages[1]["content"] == "hey"


def test_clone_session_does_not_mutate_source(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    store.append_message(session["id"], "user", "original")
    cloned = store.clone_session(session["id"], "mykey")
    store.append_message(cloned["id"], "user", "clone-only")
    source_messages = store.get_recent_messages(session["id"], limit=50)
    assert all(m["content"] != "clone-only" for m in source_messages)


def test_clone_session_copies_content_mode(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    store.set_session_content_mode("mykey", "adult-fiction")
    cloned = store.clone_session(session["id"], "mykey")
    assert cloned["content_mode"] == "adult-fiction"


# ---------------------------------------------------------------------------
# get_session_by_id_prefix
# ---------------------------------------------------------------------------


def test_get_session_by_id_prefix_finds_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    prefix = session["id"][:8]
    found = store.get_session_by_id_prefix(prefix)
    assert found is not None
    assert found["id"] == session["id"]


def test_get_session_by_id_prefix_returns_none_when_not_found(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    found = store.get_session_by_id_prefix("nonexistent")
    assert found is None


def test_get_session_by_id_prefix_full_id_works(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    found = store.get_session_by_id_prefix(session["id"])
    assert found["id"] == session["id"]


# ---------------------------------------------------------------------------
# switch_to_session
# ---------------------------------------------------------------------------


def test_switch_to_session_archives_current_and_activates_target(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session_a = store.start_session("mykey", card_id="alice")
    session_b = store.clone_session(session_a["id"], "mykey", title="Session B")
    result = store.switch_to_session("mykey", session_b["id"])
    assert result is True
    active = store.get_active_session("mykey")
    assert active is not None
    assert active["id"] == session_b["id"]
    all_sessions = store.list_sessions_for_scope("mykey", include_all=True)
    session_a_row = next((s for s in all_sessions if s["id"] == session_a["id"]), None)
    assert session_a_row is not None
    assert session_a_row["status"] != "active"


def test_switch_to_session_returns_false_when_target_not_found(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("mykey")
    result = store.switch_to_session("mykey", "nonexistent-id")
    assert result is False


def test_switch_to_already_active_session_is_noop(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("mykey")
    result = store.switch_to_session("mykey", session["id"])
    assert result is True
    active = store.get_active_session("mykey")
    assert active["id"] == session["id"]


def test_switch_back_to_archived_session_restores_it(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session_a = store.start_session("mykey")
    session_b = store.clone_session(session_a["id"], "mykey")
    store.switch_to_session("mykey", session_b["id"])
    # Now switch back to archived session_a
    result = store.switch_to_session("mykey", session_a["id"])
    assert result is True
    active = store.get_active_session("mykey")
    assert active["id"] == session_a["id"]


# ---------------------------------------------------------------------------
# /rp sessions command
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rp_sessions_no_sessions(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(
        RPCommand("sessions", [], "/rp sessions"), Event()
    )
    assert "no" in response.lower() or "sessions" in response.lower()


@pytest.mark.asyncio
async def test_rp_sessions_lists_active_session(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("sessions", [], "/rp sessions"), Event()
    )
    assert "Alice" in response or "active" in response


@pytest.mark.asyncio
async def test_rp_sessions_marks_current_active(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("sessions", [], "/rp sessions"), Event()
    )
    assert "*" in response or "(active)" in response or "active" in response.lower()


@pytest.mark.asyncio
async def test_rp_sessions_all_includes_archived(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    await runtime.handle_command(RPCommand("archive", [], "/rp archive"), Event())
    response_all = await runtime.handle_command(
        RPCommand("sessions", ["all"], "/rp sessions all"), Event()
    )
    assert "archived" in response_all


@pytest.mark.asyncio
async def test_rp_sessions_shows_short_id(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("sessions", [], "/rp sessions"), Event()
    )
    assert "[" in response and "]" in response


# ---------------------------------------------------------------------------
# /rp rename command
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rp_rename_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(
        RPCommand("rename", ["My Story"], "/rp rename My Story"), Event()
    )
    assert "No active" in response


@pytest.mark.asyncio
async def test_rp_rename_sets_title(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("rename", ["My", "Story"], "/rp rename My Story"), Event()
    )
    assert "My Story" in response
    session = store.get_active_session(SESSION_KEY)
    assert session["title"] == "My Story"


@pytest.mark.asyncio
async def test_rp_rename_missing_name(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("rename", [], "/rp rename"), Event()
    )
    assert "Usage" in response


# ---------------------------------------------------------------------------
# /rp archive command
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rp_archive_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(
        RPCommand("archive", [], "/rp archive"), Event()
    )
    assert "No active" in response


@pytest.mark.asyncio
async def test_rp_archive_archives_active_session(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("archive", [], "/rp archive"), Event()
    )
    assert "archived" in response.lower()
    assert store.get_active_session(SESSION_KEY) is None


# ---------------------------------------------------------------------------
# /rp clone command
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rp_clone_no_active_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(
        RPCommand("clone", [], "/rp clone"), Event()
    )
    assert "No active" in response


@pytest.mark.asyncio
async def test_rp_clone_creates_new_session(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("clone", [], "/rp clone"), Event()
    )
    assert "clone" in response.lower() or "branch" in response.lower() or "session" in response.lower()
    sessions = store.list_sessions_for_scope(SESSION_KEY)
    assert len(sessions) == 2


@pytest.mark.asyncio
async def test_rp_clone_with_name(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("clone", ["Branch", "A"], "/rp clone Branch A"), Event()
    )
    assert "Branch A" in response or "clone" in response.lower()


@pytest.mark.asyncio
async def test_rp_clone_shows_new_session_id(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("clone", [], "/rp clone"), Event()
    )
    assert "[" in response and "]" in response


# ---------------------------------------------------------------------------
# /rp switch command
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_rp_switch_missing_arg(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("switch", [], "/rp switch"), Event()
    )
    assert "Usage" in response


@pytest.mark.asyncio
async def test_rp_switch_not_found(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    response = await runtime.handle_command(
        RPCommand("switch", ["notexist"], "/rp switch notexist"), Event()
    )
    assert "not found" in response.lower()


@pytest.mark.asyncio
async def test_rp_switch_changes_active_session(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session_a = store.get_active_session(SESSION_KEY)
    session_b = store.clone_session(session_a["id"], SESSION_KEY, title="Session B")
    prefix = session_b["id"][:8]
    response = await runtime.handle_command(
        RPCommand("switch", [prefix], f"/rp switch {prefix}"), Event()
    )
    assert "switch" in response.lower() or "active" in response.lower() or "session" in response.lower()
    active = store.get_active_session(SESSION_KEY)
    assert active["id"] == session_b["id"]


@pytest.mark.asyncio
async def test_rp_switch_does_not_cross_user_scope(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), EventUser2())
    user_a = store.get_active_session(SESSION_KEY)
    user_b = store.get_active_session(SESSION_KEY_USER2)

    response = await runtime.handle_command(
        RPCommand("switch", [user_b["id"][:8]], f"/rp switch {user_b['id'][:8]}"), Event()
    )

    assert "not found" in response.lower()
    assert store.get_active_session(SESSION_KEY)["id"] == user_a["id"]


@pytest.mark.asyncio
async def test_rp_switch_ambiguous_same_scope_prefix_returns_clear_message(tmp_path):
    runtime, store = _make_runtime(tmp_path)
    await runtime.handle_command(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session_a = store.get_active_session(SESSION_KEY)
    session_b = store.clone_session(session_a["id"], SESSION_KEY, title="Session B")
    with store.connect() as conn:
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", ("abc11111-1111-1111-1111-111111111111", session_a["id"]))
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", ("abc22222-2222-2222-2222-222222222222", session_b["id"]))

    response = await runtime.handle_command(RPCommand("switch", ["abc"], "/rp switch abc"), Event())

    assert "Multiple sessions match abc" in response
    assert "Use a longer session id" in response


# ---------------------------------------------------------------------------
# /rp help updated
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_help_includes_session_browser_commands(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = await runtime.handle_command(RPCommand("help", [], "/rp"), Event())
    assert "/rp sessions" in response
    assert "/rp switch" in response
    assert "/rp rename" in response
    assert "/rp archive" in response
    assert "/rp clone" in response
