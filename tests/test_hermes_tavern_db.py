import sqlite3
from pathlib import Path

from plugins.hermes_tavern.db import SQLITE_BUSY_TIMEOUT_MS, TavernStore
from plugins.hermes_tavern.db_novel import NovelDBMixin
from plugins.hermes_tavern.importers.presets import ImportedPreset, ImportedPresetModule


def _table_names(db_path: Path) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        ).fetchall()
    return {row[0] for row in rows}


def _index_names(db_path: Path) -> set[str]:
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()
    return {row[0] for row in rows}


def test_migrate_creates_phase_one_tables(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)

    store.migrate()

    assert {"cards", "sessions", "messages"}.issubset(_table_names(db_path))


def test_migrate_is_idempotent(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)

    store.migrate()
    store.migrate()

    assert {"cards", "sessions", "messages"}.issubset(_table_names(db_path))


def test_migrate_once_guard_skips_second_call(tmp_path, monkeypatch):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)
    store.migrate()

    call_count = 0
    original_connect = store.connect

    def counting_connect():
        nonlocal call_count
        call_count += 1
        return original_connect()

    monkeypatch.setattr(store, "connect", counting_connect)
    store.migrate()  # should be a no-op due to _migrated flag

    assert call_count == 0


def test_migrate_creates_schema_v2_tables(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)

    store.migrate()

    tables = _table_names(db_path)
    assert "presets" in tables
    assert "prompt_modules" in tables
    assert "model_profiles" in tables


def test_migrate_adds_content_mode_column(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)

    store.migrate()

    with sqlite3.connect(db_path) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
    assert "content_mode" in cols


def test_migrate_content_mode_column_idempotent(tmp_path):
    """Running migrate() twice (via two instances) must not error on the ALTER TABLE."""
    db_path = tmp_path / "tavern.sqlite3"
    TavernStore(db_path).migrate()
    TavernStore(db_path).migrate()  # second instance; _migrated=False, but column already exists

    with sqlite3.connect(db_path) as conn:
        cols = {row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()}
    assert "content_mode" in cols


def test_migrate_creates_hot_path_indexes(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"

    TavernStore(db_path).migrate()
    TavernStore(db_path).migrate()

    indexes = _index_names(db_path)
    assert {
        "idx_tavern_messages_session_created",
        "idx_tavern_sessions_key_status",
        "idx_tavern_sessions_scope_status_updated",
        "idx_tavern_session_memory_facts_session",
        "idx_tavern_lorebook_entries_lorebook",
        "idx_tavern_image_jobs_session_created",
        "idx_tavern_cards_name",
        "idx_tavern_presets_name",
        "idx_tavern_lorebooks_name",
        "idx_tavern_personas_name",
        "idx_tavern_model_profiles_name",
        "idx_tavern_prompt_modules_preset",
        "idx_tavern_image_assets_job",
    }.issubset(indexes)


def test_connect_sets_bounded_busy_timeout(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)

    with store.connect() as conn:
        row = conn.execute("PRAGMA busy_timeout").fetchone()

    assert row[0] == SQLITE_BUSY_TIMEOUT_MS


def test_messages_page_large_table_regression(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)
    session = store.start_session("scope")
    message_ids = [
        store.append_message(session["id"], "user", f"message-{index:03d}")
        for index in range(80)
    ]
    with store.connect() as conn:
        for index, message_id in enumerate(message_ids):
            conn.execute(
                "UPDATE messages SET created_at = ? WHERE id = ?",
                (f"2026-05-23T00:00:{index:02d}Z", message_id),
            )

    page = store.get_messages_page(session["id"], limit=10, offset=30)

    assert [row["content"] for row in page] == [
        f"message-{index:03d}" for index in range(30, 40)
    ]


def test_custom_temp_db_path_works(tmp_path):
    db_path = tmp_path / "nested" / "custom.sqlite3"
    store = TavernStore(db_path)

    store.migrate()

    assert db_path.exists()
    assert {"cards", "sessions", "messages"}.issubset(_table_names(db_path))


def test_default_db_path_uses_profile_safe_hermes_home(tmp_path, monkeypatch):
    monkeypatch.setattr("plugins.hermes_tavern.db.get_hermes_home", lambda: tmp_path)

    store = TavernStore()

    assert store.db_path == (
        tmp_path / "plugins" / "hermes-tavern" / "data" / "tavern.sqlite3"
    )


def test_tavern_store_inherits_novel_db_mixin(tmp_path):
    assert issubclass(TavernStore, NovelDBMixin)
    store = TavernStore(tmp_path / "tavern.sqlite3")
    assert isinstance(store, NovelDBMixin)


def test_list_presets_counts_legacy_enabled_values_in_one_batched_read(tmp_path, monkeypatch):
    """Listing preserves order and zero counts while normalizing legacy enabled flags."""
    store = TavernStore(tmp_path / "tavern.sqlite3")
    enabled_rows = (
        ("boolean_true", True),
        ("integer_nonzero", 2),
        ("float_nonzero", 0.5),
        ("string_one", "1"),
        ("string_true", " true "),
        ("string_yes", "YES"),
        ("string_on", "\ton\n"),
    )
    disabled_rows = (
        ("boolean_false", False),
        ("integer_zero", 0),
        ("float_zero", 0.0),
        ("string_zero", "0"),
        ("string_false", "false"),
        ("string_no", "no"),
        ("string_off", "off"),
        ("unknown_legacy_value", "historical-value"),
    )
    preset_id = store.save_preset(
        ImportedPreset(
            name="legacy-enabled",
            source="test",
            raw={},
            modules=tuple(
                ImportedPresetModule(name=name, role="system", content=name, enabled=True)
                for name, _enabled in (*enabled_rows, *disabled_rows)
            ),
        )
    )
    empty_preset_id = store.save_preset(
        ImportedPreset(name="empty", source="test", raw={}, modules=())
    )
    with store.connect() as conn:
        for name, enabled in (*enabled_rows, *disabled_rows):
            conn.execute(
                "UPDATE prompt_modules SET enabled = ? WHERE preset_id = ? AND name = ?",
                (enabled, preset_id, name),
            )
        conn.execute(
            "UPDATE presets SET created_at = ? WHERE id = ?",
            ("2026-01-01T00:00:00+00:00", preset_id),
        )
        conn.execute(
            "UPDATE presets SET created_at = ? WHERE id = ?",
            ("2026-01-02T00:00:00+00:00", empty_preset_id),
        )

    store.migrate()
    connection_calls = 0
    original_connect = store.connect

    def counting_connect():
        nonlocal connection_calls
        connection_calls += 1
        return original_connect()

    monkeypatch.setattr(store, "connect", counting_connect)
    presets = store.list_presets()

    assert connection_calls == 1
    assert [(preset["name"], preset["module_count"], preset["enabled_count"]) for preset in presets] == [
        ("empty", 0, 0),
        ("legacy-enabled", len(enabled_rows) + len(disabled_rows), len(enabled_rows)),
    ]
