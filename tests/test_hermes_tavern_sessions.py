import json
from copy import deepcopy
from pathlib import Path
import sqlite3

from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.hermes_home import get_hermes_home
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.lorebooks import import_lorebook_file
from plugins.hermes_tavern.importers.presets import import_preset_file
from plugins.hermes_tavern.runtime import TavernRuntime


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"
    user_name = "Steven"


class Event:
    source = Source()
    text = ""


SESSION_KEY = "telegram:chat:chat-1:thread:main:user:user-1"


def _extract_export_paths(response: str) -> tuple[str, str]:
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split('MEDIA:"', 1)[1].split('"', 1)[0]
    return file_path, media_path


def _runtime_with_home(tmp_path, store: TavernStore, monkeypatch) -> TavernRuntime:
    monkeypatch.setenv("HERMES_HOME", str(tmp_path))
    return TavernRuntime(store)


def _count_sessions(store: TavernStore) -> int:
    with store.connect() as conn:
        return conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]


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


def test_session_runtime_export_exports_exact_id_payload(tmp_path, monkeypatch):
    card_path = tmp_path / "card.json"
    card_path.write_text(
        json.dumps({"name": "Alice", "description": "Scholar", "personality": "Curious"}),
        encoding="utf-8",
    )
    preset_path = tmp_path / "preset.txt"
    preset_path.write_text("Hello", encoding="utf-8")
    lorebook_path = tmp_path / "lorebook.json"
    lorebook_path.write_text(
        json.dumps(
            {
                "name": "Library",
                "entries": [
                    {"title": "Entry", "content": "A lantern glows."},
                ],
            }
        ),
        encoding="utf-8",
    )
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    card_id = store.save_card(parse_character_card(json.loads(card_path.read_text(encoding="utf-8"))))
    preset_id = store.save_preset(import_preset_file(preset_path))
    lorebook_id = store.save_lorebook(import_lorebook_file(lorebook_path))
    store.start_session(SESSION_KEY, card_id=card_id)
    store.set_session_preset(SESSION_KEY, preset_id)
    store.set_session_lorebook(SESSION_KEY, lorebook_id)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None

    store.append_message(session["id"], "user", "Hello")
    store.append_message(
        session["id"],
        "user",
        "Continue",
        metadata={"swipes": ["alpha", "beta"], "active_swipe": 1},
    )

    response = runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )
    file_path, media_path = _extract_export_paths(response)
    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
    card_row = store.get_card(card_id)

    assert response == (
        "Session exported as JSON.\n"
        f"file: {file_path}\n"
        f'MEDIA:"{media_path}"'
    )
    assert media_path == file_path
    assert payload["hermes_tavern_export"] is True
    assert payload["session_title"] == session["id"]
    assert payload["card_name"] == "Alice"
    assert payload["content_mode"] == "safe"
    assert payload["preset_name"] == (store.get_preset(preset_id) or {}).get("name")
    assert payload["lorebook_name"] == (store.get_lorebook(lorebook_id) or {}).get("name")
    assert payload["message_count"] == 2
    assert payload["messages"][1]["swipes"] == ["alpha", "beta"]
    assert payload["messages"][1]["active_swipe"] == 1
    assert payload["card"] == json.loads(card_row.get("data_json") or "{}")


def test_session_runtime_export_by_valid_id_prefix(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    store.start_session(SESSION_KEY)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None
    prefix = (session["id"] or "")[:12]

    response = runtime.handle_command_sync(
        RPCommand("session", ["export", prefix], f"/rp session export {prefix}"),
        Event(),
    )
    payload = json.loads(Path(_extract_export_paths(response)[0]).read_text(encoding="utf-8"))

    assert payload["session_title"] == session["id"]
    assert payload["message_count"] == 0
    assert payload["messages"] == []


def test_session_runtime_export_returns_not_found_for_missing_id(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)

    assert (
        runtime.handle_command_sync(
            RPCommand("session", ["export", "missing-id"], "/rp session export missing-id"),
            Event(),
        )
        == "Session not found: missing-id"
    )


def test_session_runtime_export_rejects_ambiguous_id_prefix(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    first = store.start_session(SESSION_KEY, card_id="alice")
    second = store.clone_session(first["id"], SESSION_KEY, title="Second")
    first_id = "abcde0000000000000000000000000001"
    second_id = "abcde0000000000000000000000000002"
    with store.connect() as conn:
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", (first_id, first["id"]))
        conn.execute("UPDATE sessions SET id = ? WHERE id = ?", (second_id, second["id"]))

    matches = store.list_sessions_by_id_prefix_for_scope(SESSION_KEY, "abcde", include_all=True)
    choices = ", ".join(f"[{(session.get('id') or '')[:8]}]" for session in matches[:3])
    response = runtime.handle_command_sync(
        RPCommand("session", ["export", "abcde"], "/rp session export abcde"),
        Event(),
    )

    assert response == f"Multiple sessions match abcde: {choices}. Use a longer session id."


def test_session_runtime_export_exports_all_messages_with_pagination(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    store.start_session(SESSION_KEY)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None
    for idx in range(250):
        store.append_message(session["id"], "user" if idx % 2 == 0 else "assistant", f"msg-{idx}")

    response = runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )
    payload = json.loads(Path(_extract_export_paths(response)[0]).read_text(encoding="utf-8"))

    assert payload["message_count"] == 250
    assert len(payload["messages"]) == 250
    assert payload["messages"][0]["content"] == "msg-0"
    assert payload["messages"][-1]["content"] == "msg-249"


def test_session_runtime_export_with_message_contents_includes_content(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    store.start_session(SESSION_KEY)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None
    store.append_message(session["id"], "user", "first line")
    store.append_message(session["id"], "assistant", "second line")

    response = runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )
    payload = json.loads(Path(_extract_export_paths(response)[0]).read_text(encoding="utf-8"))

    assert payload["messages"][0]["content"] == "first line"
    assert payload["messages"][1]["content"] == "second line"


def test_session_runtime_export_returns_empty_messages_array_for_empty_session(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    store.start_session(SESSION_KEY)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None

    response = runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )
    payload = json.loads(Path(_extract_export_paths(response)[0]).read_text(encoding="utf-8"))

    assert payload["message_count"] == 0
    assert payload["messages"] == []


def test_session_runtime_export_with_no_card_preset_or_lorebook(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    store.start_session(SESSION_KEY)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None

    response = runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )
    payload = json.loads(Path(_extract_export_paths(response)[0]).read_text(encoding="utf-8"))

    assert payload["card_name"] == "unknown"
    assert payload["preset_name"] == "none"
    assert payload["lorebook_name"] == "none"
    assert "card" not in payload


def test_session_runtime_export_file_stays_within_sessions_export_dir(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home with spaces", store, monkeypatch)
    store.start_session(SESSION_KEY)
    with store.connect() as conn:
        conn.execute(
            "UPDATE sessions SET id = ? WHERE id = ?",
            ("../..//../../outside", store.get_active_session(SESSION_KEY)["id"]),
        )
    session = store.get_active_session(SESSION_KEY)
    assert session is not None

    response = runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )
    file_path = _extract_export_paths(response)[0]
    export_dir = get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "sessions"
    export_path = Path(file_path)

    assert export_path.parent == export_dir
    assert export_path.resolve().is_relative_to(export_dir.resolve())
    assert export_path.name == "session_" + "".join(c for c in session["id"] if c.isalnum())[:16] + ".json"


def test_session_runtime_export_quotes_media_path_with_spaces(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home with spaces", store, monkeypatch)
    store.start_session(SESSION_KEY)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None
    response = runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )
    file_path, media_path = _extract_export_paths(response)

    assert " " in media_path
    assert media_path == file_path
    assert 'MEDIA:"' in response
    assert f'MEDIA:"{media_path}"' in response


def test_session_runtime_export_does_not_mutate_session_or_messages(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    runtime = _runtime_with_home(tmp_path / "hermes home", store, monkeypatch)
    store.start_session(SESSION_KEY)
    session = store.get_active_session(SESSION_KEY)
    assert session is not None
    store.append_message(session["id"], "user", "before export")
    session_count_before = _count_sessions(store)
    session_before = deepcopy(session)
    messages_before = deepcopy(store.get_recent_messages(session["id"]))

    runtime.handle_command_sync(
        RPCommand("session", ["export", session["id"]], f"/rp session export {session['id']}"),
        Event(),
    )

    session_after = store.get_active_session(SESSION_KEY)
    messages_after = store.get_recent_messages(session["id"])

    assert session_before == session_after
    assert messages_before == messages_after
    assert session_count_before == _count_sessions(store)


def test_session_runtime_help_includes_session_export_command(tmp_path, monkeypatch):
    runtime = _runtime_with_home(tmp_path / "hermes home", TavernStore(tmp_path / "tavern.sqlite3"), monkeypatch)

    assert "/rp session export <id>" in runtime.handle_command_sync(RPCommand("help", [], "/rp help"), Event())
