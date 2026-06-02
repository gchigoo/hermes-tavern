import json
import sqlite3

from plugins.hermes_tavern.db import TavernStore


def test_start_session_creates_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()

    session = store.start_session("telegram:chat:1:thread:main:user:2", card_id="alice")

    assert session["session_key"] == "telegram:chat:1:thread:main:user:2"
    assert session["card_id"] == "alice"
    assert session["status"] == "active"
    assert store.get_active_session(session["session_key"])["id"] == session["id"]


def test_start_session_same_key_reuses_and_updates_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()

    first = store.start_session("key", card_id="alice")
    second = store.start_session("key", card_id="bob")

    assert second["id"] == first["id"]
    assert second["card_id"] == "bob"
    assert store.get_active_session("key")["card_id"] == "bob"


def test_start_session_reuses_only_matching_scope_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()

    caller_first = store.start_session("caller-key", card_id="alice")
    other_active = store.start_session("other-active-key", card_id="other-active")
    other_paused = store.start_session("other-paused-key", card_id="other-paused")
    assert store.pause_session("other-paused-key") is True

    caller_second = store.start_session("caller-key", card_id="bob")

    assert caller_second["id"] == caller_first["id"]
    assert caller_second["card_id"] == "bob"
    assert len(store.list_sessions_for_scope("caller-key")) == 1
    assert store.get_active_session("other-active-key")["id"] == other_active["id"]
    assert store.get_active_session("other-active-key")["card_id"] == "other-active"
    assert store.get_paused_session("other-paused-key")["id"] == other_paused["id"]
    assert store.get_paused_session("other-paused-key")["card_id"] == "other-paused"


def test_start_session_after_end_creates_fresh_active_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()

    first = store.start_session("key", card_id="alice")
    store.append_message(first["id"], "user", "old turn")
    assert store.end_session("key") is True

    second = store.start_session("key", card_id="bob")

    assert second["id"] != first["id"]
    assert second["session_key"] == "key"
    assert second["card_id"] == "bob"
    assert store.get_recent_messages(second["id"], limit=10) == []
    ended = store.list_sessions_by_id_prefix_for_scope("key", first["id"][:8], include_all=True)
    assert ended[0]["status"] == "ended"
    assert ended[0]["session_key"] == first["id"]


def test_list_sessions_by_id_prefix_for_scope_filters_cross_scope_collisions(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()

    scope_a = "telegram:chat:1:thread:main:user:1"
    scope_b = "telegram:chat:1:thread:main:user:2"
    session_a = store.start_session(scope_a, card_id="alice")
    session_b = store.start_session(scope_b, card_id="bob")
    id_a = "abc12345-0000-4000-8000-000000000001"
    id_b = "abc12345-0000-4000-8000-000000000002"
    with store.connect() as conn:
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", (id_a, session_a["id"]))
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", (id_b, session_b["id"]))

    matches_a = store.list_sessions_by_id_prefix_for_scope(
        scope_a,
        "abc12345",
        include_all=True,
    )
    matches_b = store.list_sessions_by_id_prefix_for_scope(
        scope_b,
        "abc12345",
        include_all=True,
    )
    full_id_cross_scope = store.list_sessions_by_id_prefix_for_scope(
        scope_a,
        id_b,
        include_all=True,
    )

    assert [row["id"] for row in matches_a] == [id_a]
    assert [row["id"] for row in matches_b] == [id_b]
    assert full_id_cross_scope == []


def test_list_sessions_by_id_prefix_for_scope_keeps_same_scope_ambiguity(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()

    scope_key = "telegram:chat:1:thread:main:user:1"
    first = store.start_session(scope_key, card_id="alice")
    second = store.clone_session(first["id"], scope_key, title="Second")
    id_first = "def67890-0000-4000-8000-000000000001"
    id_second = "def67890-0000-4000-8000-000000000002"
    with store.connect() as conn:
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", (id_first, first["id"]))
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", (id_second, second["id"]))

    matches = store.list_sessions_by_id_prefix_for_scope(
        scope_key,
        "def67890",
        include_all=True,
    )

    assert {row["id"] for row in matches} == {id_first, id_second}
    assert len(matches) == 2


def test_end_session_marks_session_inactive(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    store.start_session("key", card_id="alice")

    assert store.end_session("key") is True

    assert store.get_active_session("key") is None
    assert store.end_session("key") is False


def test_pause_and_resume_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("key", card_id="alice")

    assert store.pause_session("key") is True
    assert store.get_active_session("key") is None
    assert store.pause_session("key") is False

    assert store.resume_session("key") is True
    resumed = store.get_active_session("key")
    assert resumed["id"] == session["id"]
    assert resumed["status"] == "active"
    assert store.resume_session("key") is False


def test_get_paused_session_reports_paused_row(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.migrate()
    session = store.start_session("key", card_id="alice")

    assert store.pause_session("key") is True

    paused = store.get_paused_session("key")
    assert paused["id"] == session["id"]
    assert paused["status"] == "paused"
    assert store.get_paused_session("missing") is None


def test_append_message_persists_content_and_metadata(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)
    store.migrate()
    session = store.start_session("key")

    message_id = store.append_message(
        session["id"],
        "user",
        "hello",
        metadata={"message_id": "m1"},
    )

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, session_id, role, content, metadata_json FROM messages"
        ).fetchone()
    assert row == (message_id, session["id"], "user", "hello", json.dumps({"message_id": "m1"}, sort_keys=True))
