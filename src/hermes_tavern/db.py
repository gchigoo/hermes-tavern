"""SQLite persistence for Hermes Tavern."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from hermes_constants import get_hermes_home
from plugins.hermes_tavern.db_utils import (
    assert_no_secret_keys as _assert_no_secret_keys,
    row_to_dict as _row_to_dict,
    utc_now as _utc_now,
)

SQLITE_BUSY_TIMEOUT_MS = 5000


class TavernStore:
    """Small SQLite store for Tavern cards, sessions, and messages."""

    def __init__(self, db_path: str | Path | None = None) -> None:
        if db_path is None:
            db_path = (
                get_hermes_home()
                / "plugins"
                / "hermes-tavern"
                / "data"
                / "tavern.sqlite3"
        )
        self.db_path = Path(db_path)
        self._migrated: bool = False
        self._last_card_id: str | None = None
        self._last_preset_id: str | None = None
        self._last_lorebook_id: str | None = None
        self._last_persona_id: str | None = None

    def set_last_card(self, card_id: str | None) -> None:
        self._last_card_id = card_id or None

    def set_last_preset(self, preset_id: str | None) -> None:
        self._last_preset_id = preset_id or None

    def set_last_lorebook(self, lorebook_id: str | None) -> None:
        self._last_lorebook_id = lorebook_id or None

    def set_last_persona(self, persona_id: str | None) -> None:
        self._last_persona_id = persona_id or None

    def _get_row_by_id(self, table: str, columns: str, row_id: str | None) -> dict[str, Any] | None:
        if not row_id:
            return None
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                f"SELECT {columns} FROM {table} WHERE id = ? LIMIT 1",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def connect(self) -> sqlite3.Connection:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute(f"PRAGMA busy_timeout = {SQLITE_BUSY_TIMEOUT_MS}")
        return conn

    def migrate(self) -> None:
        if self._migrated:
            return
        with self.connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS cards (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    session_key TEXT UNIQUE NOT NULL,
                    card_id TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    metadata_json TEXT
                );

                CREATE TABLE IF NOT EXISTS presets (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'native',
                    raw_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS prompt_modules (
                    id TEXT PRIMARY KEY,
                    preset_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL DEFAULT 'system',
                    content TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    position TEXT NOT NULL DEFAULT 'before_char',
                    insertion_order INTEGER NOT NULL DEFAULT 0,
                    raw_json TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS model_profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    mode TEXT NOT NULL DEFAULT 'chat',
                    context_window INTEGER NOT NULL DEFAULT 8192,
                    raw_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS lorebooks (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source TEXT NOT NULL DEFAULT 'native',
                    raw_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS lorebook_entries (
                    id TEXT PRIMARY KEY,
                    lorebook_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    keys_json TEXT NOT NULL,
                    secondary_keys_json TEXT NOT NULL,
                    enabled INTEGER NOT NULL DEFAULT 1,
                    constant INTEGER NOT NULL DEFAULT 0,
                    regex INTEGER NOT NULL DEFAULT 0,
                    position TEXT NOT NULL DEFAULT 'before_char',
                    insertion_order INTEGER NOT NULL DEFAULT 0,
                    priority INTEGER NOT NULL DEFAULT 0,
                    probability REAL NOT NULL DEFAULT 1.0,
                    raw_json TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS session_memory_facts (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    content TEXT NOT NULL,
                    importance INTEGER NOT NULL DEFAULT 1,
                    source TEXT NOT NULL DEFAULT 'manual',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS session_summaries (
                    session_id TEXT PRIMARY KEY,
                    summary TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS personas (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    raw_json TEXT NOT NULL,
                    source_path TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS image_jobs (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    negative_prompt TEXT NOT NULL DEFAULT '',
                    source_message_id TEXT,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    metadata_json TEXT
                );

                CREATE TABLE IF NOT EXISTS image_assets (
                    id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    width INTEGER,
                    height INTEGER,
                    prompt_snapshot TEXT NOT NULL,
                    metadata_json TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS image_settings (
                    session_id TEXT PRIMARY KEY,
                    settings_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS image_safety (
                    session_id TEXT PRIMARY KEY,
                    safety_json TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS image_styles (
                    name TEXT PRIMARY KEY,
                    positive_template TEXT NOT NULL DEFAULT '',
                    negative_template TEXT NOT NULL DEFAULT '',
                    settings_json TEXT NOT NULL DEFAULT '{}',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                """
            )
            # Add content_mode to sessions if missing (SQLite < 3.37 has no
            # ADD COLUMN IF NOT EXISTS, so guard with PRAGMA table_info).
            existing_cols = {
                row[1]
                for row in conn.execute("PRAGMA table_info(sessions)").fetchall()
            }
            if "content_mode" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN "
                    "content_mode TEXT NOT NULL DEFAULT 'safe'"
                )
            if "model_profile_id" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN model_profile_id TEXT"
                )
            if "preset_id" not in existing_cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN preset_id TEXT")
            if "lorebook_id" not in existing_cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN lorebook_id TEXT")
            if "persona_id" not in existing_cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN persona_id TEXT")
            if "note_text" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN "
                    "note_text TEXT NOT NULL DEFAULT ''"
                )
            if "note_position" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN "
                    "note_position TEXT NOT NULL DEFAULT 'before_user'"
                )
            if "note_frequency" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN "
                    "note_frequency TEXT NOT NULL DEFAULT 'always'"
                )
            if "note_every_n" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN "
                    "note_every_n INTEGER NOT NULL DEFAULT 3"
                )
            if "adapter_mode" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN "
                    "adapter_mode TEXT NOT NULL DEFAULT 'fake'"
                )
            if "live_confirmed" not in existing_cols:
                conn.execute(
                    "ALTER TABLE sessions ADD COLUMN "
                    "live_confirmed INTEGER NOT NULL DEFAULT 0"
                )
            if "title" not in existing_cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN title TEXT")
            if "scope_key" not in existing_cols:
                conn.execute("ALTER TABLE sessions ADD COLUMN scope_key TEXT")
                # Backfill scope_key for existing sessions: use session_key as scope.
                conn.execute(
                    "UPDATE sessions SET scope_key = session_key WHERE scope_key IS NULL"
                )
            conn.executescript(
                """
                CREATE INDEX IF NOT EXISTS idx_tavern_cards_name
                    ON cards(name);
                CREATE INDEX IF NOT EXISTS idx_tavern_messages_session_created
                    ON messages(session_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_tavern_sessions_key_status
                    ON sessions(session_key, status);
                CREATE INDEX IF NOT EXISTS idx_tavern_sessions_scope_status_updated
                    ON sessions(scope_key, status, updated_at);
                CREATE INDEX IF NOT EXISTS idx_tavern_presets_name
                    ON presets(name);
                CREATE INDEX IF NOT EXISTS idx_tavern_prompt_modules_preset
                    ON prompt_modules(preset_id);
                CREATE INDEX IF NOT EXISTS idx_tavern_model_profiles_name
                    ON model_profiles(name);
                CREATE INDEX IF NOT EXISTS idx_tavern_lorebooks_name
                    ON lorebooks(name);
                CREATE INDEX IF NOT EXISTS idx_tavern_lorebook_entries_lorebook
                    ON lorebook_entries(lorebook_id);
                CREATE INDEX IF NOT EXISTS idx_tavern_session_memory_facts_session
                    ON session_memory_facts(session_id);
                CREATE INDEX IF NOT EXISTS idx_tavern_personas_name
                    ON personas(name);
                CREATE INDEX IF NOT EXISTS idx_tavern_image_jobs_session_created
                    ON image_jobs(session_id, created_at);
                CREATE INDEX IF NOT EXISTS idx_tavern_image_assets_job
                    ON image_assets(job_id);
                """
            )
        self._migrated = True

        # Seed ST-inspired image style presets if the table is empty.
        from plugins.hermes_tavern.images import seed_image_styles as _seed
        _seed(self)

    def get_active_session(self, session_key: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT sessions.*, cards.name AS card_name
                FROM sessions
                LEFT JOIN cards ON cards.id = sessions.card_id
                WHERE sessions.session_key = ? AND sessions.status = 'active'
                """,
                (session_key,),
            ).fetchone()
        return _row_to_dict(row)

    def get_paused_session(self, session_key: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT sessions.*, cards.name AS card_name
                FROM sessions
                LEFT JOIN cards ON cards.id = sessions.card_id
                WHERE sessions.session_key = ? AND sessions.status = 'paused'
                ORDER BY sessions.updated_at DESC
                LIMIT 1
                """,
                (session_key,),
            ).fetchone()
        return _row_to_dict(row)

    def start_session(
        self,
        session_key: str,
        card_id: str | None = None,
    ) -> dict[str, Any]:
        self.migrate()
        now = _utc_now()
        with self.connect() as conn:
            existing = conn.execute(
                "SELECT id, status FROM sessions WHERE session_key = ?",
                (session_key,),
            ).fetchone()
            if existing and existing["status"] == "active":
                conn.execute(
                    """
                    UPDATE sessions
                    SET card_id = COALESCE(?, card_id),
                        scope_key = COALESCE(scope_key, ?),
                        status = 'active',
                        updated_at = ?
                    WHERE session_key = ?
                    """,
                    (card_id, session_key, now, session_key),
                )
            else:
                if existing:
                    conn.execute(
                        """
                        UPDATE sessions
                        SET session_key = COALESCE(NULLIF(id, ''), session_key),
                            scope_key = COALESCE(scope_key, ?),
                            updated_at = ?
                        WHERE id = ?
                        """,
                        (session_key, now, existing["id"]),
                    )
                conn.execute(
                    """
                    INSERT INTO sessions (
                        id,
                        session_key,
                        scope_key,
                        card_id,
                        status,
                        created_at,
                        updated_at
                    )
                    VALUES (?, ?, ?, ?, 'active', ?, ?)
                    """,
                    (str(uuid4()), session_key, session_key, card_id, now, now),
                )
            row = conn.execute(
                """
                SELECT sessions.*, cards.name AS card_name
                FROM sessions
                LEFT JOIN cards ON cards.id = sessions.card_id
                WHERE sessions.session_key = ?
                """,
                (session_key,),
            ).fetchone()
        result = _row_to_dict(row)
        if result is None:
            raise RuntimeError("failed to start Tavern session")
        return result

    def end_session(self, session_key: str) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET status = 'ended', updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (_utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def pause_session(self, session_key: str) -> bool:
        """Pause the active session so ordinary messages fall through to Hermes."""
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET status = 'paused', updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (_utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def resume_session(self, session_key: str) -> bool:
        """Resume the most recent paused session for this gateway scope."""
        self.migrate()
        now = _utc_now()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id FROM sessions
                WHERE session_key = ? AND status = 'paused'
                ORDER BY updated_at DESC
                LIMIT 1
                """,
                (session_key,),
            ).fetchone()
            if row is None:
                return False
            cursor = conn.execute(
                """
                UPDATE sessions
                SET status = 'active', updated_at = ?
                WHERE id = ?
                """,
                (now, row["id"]),
            )
            return cursor.rowcount > 0

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self.migrate()
        message_id = str(uuid4())
        metadata_json = (
            json.dumps(metadata, sort_keys=True) if metadata is not None else None
        )
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO messages (
                    id,
                    session_id,
                    role,
                    content,
                    created_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (message_id, session_id, role, content, _utc_now(), metadata_json),
            )
        return message_id

    def save_card(self, card: "CharacterCard") -> str:
        self.migrate()
        data = {
            "id": card.id,
            "name": card.name,
            "description": card.description,
            "personality": card.personality,
            "scenario": card.scenario,
            "first_mes": card.first_mes,
            "mes_example": card.mes_example,
            "alternate_greetings": list(card.alternate_greetings),
            "creator_notes": card.creator_notes,
            "system_prompt_override": card.system_prompt_override,
            "post_history_instructions": card.post_history_instructions,
            "tags": list(card.tags),
            "talkativeness": card.talkativeness,
            "extensions": dict(card.extensions),
            "source_path": card.source_path,
            "raw": card.raw,
        }
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO cards (id, name, data_json, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    data_json = excluded.data_json
                """,
                (card.id, card.name, json.dumps(data, sort_keys=True), _utc_now()),
            )
        self.set_last_card(card.id)
        return card.id

    def list_cards(self) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT id, name, data_json, created_at FROM cards ORDER BY name, created_at"
            ).fetchall()
        return [dict(row) for row in rows]

    def set_session_card(self, session_key: str, card_id: str) -> bool:
        """Bind a different character card to the active session."""
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET card_id = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (card_id, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def get_recent_messages(
        self, session_id: str, limit: int = 20
    ) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, role, content, created_at, metadata_json
                FROM (
                    SELECT id, role, content, created_at, metadata_json
                    FROM messages
                    WHERE session_id = ?
                    ORDER BY created_at DESC, id DESC
                    LIMIT ?
                )
                ORDER BY created_at ASC, id ASC
                """,
                (session_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]

    def count_messages(self, session_id: str) -> int:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM messages WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return row[0] if row else 0

    def get_messages_page(self, session_id: str, limit: int, offset: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, role, content, created_at, metadata_json
                FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                LIMIT ? OFFSET ?
                """,
                (session_id, limit, offset),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_message(self, message_id: str) -> bool:
        """Delete a single message by id. Returns True when a row was removed."""
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
            return cursor.rowcount > 0

    def update_message(
        self,
        message_id: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> bool:
        """Update a message body and optional metadata by id."""
        self.migrate()
        metadata_json = (
            json.dumps(metadata, sort_keys=True) if metadata is not None else None
        )
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE messages SET content = ?, metadata_json = ? WHERE id = ?",
                (content, metadata_json, message_id),
            )
            return cursor.rowcount > 0

    def delete_last_assistant_message(self, session_id: str) -> str | None:
        """Delete the most recent assistant message. Returns its id or None."""
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id FROM messages
                WHERE session_id = ? AND role = 'assistant'
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            msg_id = row["id"]
            conn.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
        return msg_id

    def delete_assistant_after_last_user_message(self, session_id: str) -> str | None:
        """Delete the assistant message immediately following the latest user message."""
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, role FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (session_id,),
            ).fetchall()
            last_user_idx = None
            for i, row in enumerate(rows):
                if row["role"] == "user":
                    last_user_idx = i
            if last_user_idx is None:
                return None
            next_idx = last_user_idx + 1
            if next_idx >= len(rows) or rows[next_idx]["role"] != "assistant":
                return None
            msg_id = rows[next_idx]["id"]
            conn.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
        return msg_id

    def delete_last_user_assistant_turn(self, session_id: str) -> int:
        """Delete the last user message and any immediately following assistant message.

        Returns count of deleted messages (0, 1, or 2).
        """
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, role FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (session_id,),
            ).fetchall()
            last_user_idx = None
            for i, row in enumerate(rows):
                if row["role"] == "user":
                    last_user_idx = i
            if last_user_idx is None:
                return 0
            ids_to_delete = [rows[last_user_idx]["id"]]
            next_idx = last_user_idx + 1
            if next_idx < len(rows) and rows[next_idx]["role"] == "assistant":
                ids_to_delete.append(rows[next_idx]["id"])
            for msg_id in ids_to_delete:
                conn.execute("DELETE FROM messages WHERE id = ?", (msg_id,))
        return len(ids_to_delete)

    def update_last_user_message(self, session_id: str, new_content: str) -> str | None:
        """Update the content of the most recent user message. Returns its id or None."""
        self.migrate()
        new_content = new_content.strip()
        if not new_content:
            raise ValueError("message content must not be empty")
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id FROM messages
                WHERE session_id = ? AND role = 'user'
                ORDER BY created_at DESC, id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
            if row is None:
                return None
            conn.execute(
                "UPDATE messages SET content = ? WHERE id = ?",
                (new_content, row["id"]),
            )
        return row["id"]

    def save_preset(self, preset: Any) -> str:
        """Persist an imported preset and its prompt modules."""
        self.migrate()
        preset_id = getattr(preset, "id", None) or str(uuid4())
        now = _utc_now()
        raw = getattr(preset, "raw", {}) or {}
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO presets (id, name, source, raw_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    source = excluded.source,
                    raw_json = excluded.raw_json
                """,
                (
                    preset_id,
                    preset.name,
                    preset.source,
                    json.dumps(raw, ensure_ascii=False, sort_keys=True),
                    now,
                ),
            )
            conn.execute("DELETE FROM prompt_modules WHERE preset_id = ?", (preset_id,))
            for module in preset.modules:
                module_raw = dict(getattr(module, "raw", {}) or {})
                module_raw["risk_level"] = module.risk_level
                module_raw["risk_reasons"] = list(module.risk_reasons)
                conn.execute(
                    """
                    INSERT INTO prompt_modules (
                        id, preset_id, name, role, content, enabled,
                        position, insertion_order, raw_json, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid4()),
                        preset_id,
                        module.name,
                        module.role,
                        module.content,
                        1 if module.enabled else 0,
                        module.position,
                        module.insertion_order,
                        json.dumps(module_raw, ensure_ascii=False, sort_keys=True),
                        now,
                    ),
                )
        self.set_last_preset(preset_id)
        return preset_id

    def list_presets(self) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT presets.id, presets.name, presets.source, presets.created_at,
                       COUNT(prompt_modules.id) AS module_count,
                       SUM(CASE WHEN prompt_modules.enabled = 1 THEN 1 ELSE 0 END) AS enabled_count
                FROM presets
                LEFT JOIN prompt_modules ON prompt_modules.preset_id = presets.id
                GROUP BY presets.id
                ORDER BY presets.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_preset(self, preset_id_or_name: str) -> dict[str, Any] | None:
        self.migrate()
        ref = preset_id_or_name.strip()
        if ref.lower() == "last":
            return self._get_row_by_id(
                "presets",
                "id, name, source, raw_json, created_at",
                self._last_preset_id,
            )
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, source, raw_json, created_at
                FROM presets
                WHERE id = ? OR name = ?
                ORDER BY CASE WHEN id = ? THEN 0 ELSE 1 END, created_at DESC
                LIMIT 1
                """,
                (ref, ref, ref),
            ).fetchone()
        return _row_to_dict(row)

    def list_prompt_modules(self, preset_id: str) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, preset_id, name, role, content, enabled, position,
                       insertion_order, raw_json, created_at
                FROM prompt_modules
                WHERE preset_id = ?
                ORDER BY insertion_order, created_at
                """,
                (preset_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_prompt_module(
        self,
        module_ref: str,
        *,
        preset_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Resolve a prompt module by id prefix or name, optionally scoped to a preset."""
        self.migrate()
        ref = module_ref.strip()
        if not ref:
            return None
        prefix = f"{ref}%"
        where = "(id = ? OR name = ? OR id LIKE ?)"
        params: list[Any] = [ref, ref, prefix]
        if preset_id:
            where = f"preset_id = ? AND {where}"
            params.insert(0, preset_id)
        with self.connect() as conn:
            row = conn.execute(
                f"""
                SELECT id, preset_id, name, role, content, enabled, position,
                       insertion_order, raw_json, created_at
                FROM prompt_modules
                WHERE {where}
                ORDER BY CASE WHEN id = ? THEN 0 WHEN name = ? THEN 1 ELSE 2 END,
                         insertion_order, created_at
                LIMIT 1
                """,
                (*params, ref, ref),
            ).fetchone()
        return _row_to_dict(row)

    def set_prompt_module_enabled(self, module_id: str, enabled: bool) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE prompt_modules SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, module_id),
            )
            return cursor.rowcount > 0

    def save_lorebook(self, lorebook: Any) -> str:
        """Persist an imported lorebook and its entries."""
        self.migrate()
        lorebook_id = getattr(lorebook, "id", None) or str(uuid4())
        now = _utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO lorebooks (id, name, source, raw_json, created_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    source = excluded.source,
                    raw_json = excluded.raw_json
                """,
                (
                    lorebook_id,
                    lorebook.name,
                    lorebook.source,
                    json.dumps(getattr(lorebook, "raw", {}) or {}, ensure_ascii=False, sort_keys=True),
                    now,
                ),
            )
            conn.execute("DELETE FROM lorebook_entries WHERE lorebook_id = ?", (lorebook_id,))
            for entry in lorebook.entries:
                conn.execute(
                    """
                    INSERT INTO lorebook_entries (
                        id, lorebook_id, title, content, keys_json,
                        secondary_keys_json, enabled, constant, regex, position,
                        insertion_order, priority, probability, raw_json, created_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        f"{lorebook_id}:{entry.id}",
                        lorebook_id,
                        entry.title,
                        entry.content,
                        json.dumps(list(entry.keys), ensure_ascii=False),
                        json.dumps(list(entry.secondary_keys), ensure_ascii=False),
                        1 if entry.enabled else 0,
                        1 if entry.constant else 0,
                        1 if entry.regex else 0,
                        entry.position,
                        entry.insertion_order,
                        entry.priority,
                        entry.probability,
                        json.dumps(entry.raw, ensure_ascii=False, sort_keys=True),
                        now,
                    ),
                )
        self.set_last_lorebook(lorebook_id)
        return lorebook_id

    def list_lorebooks(self) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT lorebooks.id, lorebooks.name, lorebooks.source, lorebooks.created_at,
                       COUNT(lorebook_entries.id) AS entry_count,
                       SUM(CASE WHEN lorebook_entries.enabled = 1 THEN 1 ELSE 0 END) AS enabled_count
                FROM lorebooks
                LEFT JOIN lorebook_entries ON lorebook_entries.lorebook_id = lorebooks.id
                GROUP BY lorebooks.id
                ORDER BY lorebooks.created_at DESC
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_lorebook(self, lorebook_id_or_name: str) -> dict[str, Any] | None:
        self.migrate()
        ref = lorebook_id_or_name.strip()
        if ref.lower() == "last":
            return self._get_row_by_id(
                "lorebooks",
                "id, name, source, raw_json, created_at",
                self._last_lorebook_id,
            )
        prefix = f"{ref}%"
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, source, raw_json, created_at
                FROM lorebooks
                WHERE id = ? OR name = ? OR id LIKE ?
                ORDER BY CASE WHEN id = ? THEN 0 WHEN name = ? THEN 1 ELSE 2 END, created_at DESC
                LIMIT 1
                """,
                (ref, ref, prefix, ref, ref),
            ).fetchone()
        return _row_to_dict(row)

    def list_lorebook_entries(self, lorebook_id: str) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, lorebook_id, title, content, keys_json, secondary_keys_json,
                       enabled, constant, regex, position, insertion_order, priority,
                       probability, raw_json, created_at
                FROM lorebook_entries
                WHERE lorebook_id = ?
                ORDER BY priority DESC, insertion_order, created_at
                """,
                (lorebook_id,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_lorebook_entry(
        self,
        entry_ref: str,
        *,
        lorebook_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Resolve a lorebook entry by id prefix or title."""
        self.migrate()
        ref = entry_ref.strip()
        if not ref:
            return None
        prefix = f"{ref}%"
        where = "(id = ? OR title = ? OR id LIKE ?)"
        params: list[Any] = [ref, ref, prefix]
        if lorebook_id:
            where = f"lorebook_id = ? AND {where}"
            params.insert(0, lorebook_id)
        with self.connect() as conn:
            row = conn.execute(
                f"""
                SELECT id, lorebook_id, title, content, keys_json, secondary_keys_json,
                       enabled, constant, regex, position, insertion_order, priority,
                       probability, raw_json, created_at
                FROM lorebook_entries
                WHERE {where}
                ORDER BY CASE WHEN id = ? THEN 0 WHEN title = ? THEN 1 ELSE 2 END,
                         priority DESC, insertion_order, created_at
                LIMIT 1
                """,
                (*params, ref, ref),
            ).fetchone()
        return _row_to_dict(row)

    def set_lorebook_entry_enabled(self, entry_id: str, enabled: bool) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE lorebook_entries SET enabled = ? WHERE id = ?",
                (1 if enabled else 0, entry_id),
            )
            return cursor.rowcount > 0

    def set_session_lorebook(self, session_key: str, lorebook_id: str | None) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET lorebook_id = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (lorebook_id, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def save_persona(self, persona: Any) -> str:
        """Persist a secret-free user persona import."""
        self.migrate()
        raw_json = getattr(persona, "raw_json", {}) or {}
        persona_id = getattr(persona, "id", None) or str(uuid4())
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO personas (id, name, content, raw_json, source_path, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    content = excluded.content,
                    raw_json = excluded.raw_json,
                    source_path = excluded.source_path
                """,
                (
                    persona_id,
                    persona.name,
                    persona.content,
                    json.dumps(raw_json, ensure_ascii=False, sort_keys=True),
                    getattr(persona, "source_path", "") or "",
                    _utc_now(),
                ),
            )
        self.set_last_persona(persona_id)
        return persona_id

    def count_personas(self) -> int:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute("SELECT COUNT(*) FROM personas").fetchone()
        return row[0] if row else 0

    def list_personas(self, *, limit: int = 25, offset: int = 0) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, name, content, raw_json, source_path, created_at
                FROM personas
                ORDER BY name ASC, created_at DESC
                LIMIT ? OFFSET ?
                """,
                (limit, offset),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_persona(self, persona_id_or_name: str) -> dict[str, Any] | None:
        self.migrate()
        ref = persona_id_or_name.strip()
        if ref.lower() == "last":
            return self._get_row_by_id(
                "personas",
                "id, name, content, raw_json, source_path, created_at",
                self._last_persona_id,
            )
        prefix = f"{ref}%"
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, content, raw_json, source_path, created_at
                FROM personas
                WHERE id = ? OR name = ? OR id LIKE ?
                ORDER BY CASE WHEN id = ? THEN 0 WHEN name = ? THEN 1 ELSE 2 END,
                         name ASC, created_at DESC
                LIMIT 1
                """,
                (ref, ref, prefix, ref, ref),
            ).fetchone()
        return _row_to_dict(row)

    def set_session_persona(self, session_key: str, persona_id: str | None) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET persona_id = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (persona_id, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def set_session_note(self, session_key: str, note_text: str) -> bool:
        """Set the active session's Author's Note / Scene Note text."""
        self.migrate()
        note_text = note_text.strip()
        if not note_text:
            raise ValueError("note text must not be empty")
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET note_text = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (note_text, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def clear_session_note(self, session_key: str) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET note_text = '', updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (_utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def set_session_note_position(self, session_key: str, position: str) -> bool:
        self.migrate()
        if position not in {"before_char", "after_history", "before_user"}:
            raise ValueError("note position must be before_char, after_history, or before_user")
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET note_position = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (position, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def set_session_note_frequency(
        self, session_key: str, frequency: str, *, every_n: int | None = None
    ) -> bool:
        self.migrate()
        if frequency not in {"always", "every_n"}:
            raise ValueError("note frequency must be always or every_n")
        interval = 3 if every_n is None else max(2, min(20, int(every_n)))
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET note_frequency = ?, note_every_n = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (frequency, interval, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def add_session_memory_fact(
        self,
        session_key: str,
        content: str,
        *,
        importance: int = 1,
        source: str = "manual",
    ) -> str | None:
        """Add a manual memory fact to an active session."""
        self.migrate()
        content = content.strip()
        if not content:
            raise ValueError("memory fact content must not be empty")
        importance = max(1, min(5, int(importance)))
        fact_id = str(uuid4())
        with self.connect() as conn:
            session = conn.execute(
                "SELECT id FROM sessions WHERE session_key = ? AND status = 'active'",
                (session_key,),
            ).fetchone()
            if session is None:
                return None
            conn.execute(
                """
                INSERT INTO session_memory_facts (
                    id, session_id, content, importance, source, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (fact_id, session["id"], content, importance, source, _utc_now()),
            )
        return fact_id

    def count_session_memory_facts(self, session_key: str) -> int:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) FROM session_memory_facts
                JOIN sessions ON sessions.id = session_memory_facts.session_id
                WHERE sessions.session_key = ? AND sessions.status = 'active'
                """,
                (session_key,),
            ).fetchone()
        return row[0] if row else 0

    def list_session_memory_facts(
        self, session_key: str, *, limit: int | None = None, offset: int = 0
    ) -> list[dict[str, Any]]:
        self.migrate()
        limit_clause = f"LIMIT {int(limit)} OFFSET {int(offset)}" if limit is not None else ""
        with self.connect() as conn:
            rows = conn.execute(
                f"""
                SELECT session_memory_facts.id,
                       session_memory_facts.session_id,
                       session_memory_facts.content,
                       session_memory_facts.importance,
                       session_memory_facts.source,
                       session_memory_facts.created_at
                FROM session_memory_facts
                JOIN sessions ON sessions.id = session_memory_facts.session_id
                WHERE sessions.session_key = ? AND sessions.status = 'active'
                ORDER BY session_memory_facts.importance DESC,
                         session_memory_facts.created_at ASC
                {limit_clause}
                """,
                (session_key,),
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_session_memory_fact(self, session_key: str, fact_ref: str) -> int:
        """Delete one active-session memory fact by id prefix, or all facts."""
        self.migrate()
        ref = fact_ref.strip()
        if not ref:
            return 0
        with self.connect() as conn:
            session = conn.execute(
                "SELECT id FROM sessions WHERE session_key = ? AND status = 'active'",
                (session_key,),
            ).fetchone()
            if session is None:
                return 0
            if ref.lower() == "all":
                cursor = conn.execute(
                    "DELETE FROM session_memory_facts WHERE session_id = ?",
                    (session["id"],),
                )
                return cursor.rowcount
            cursor = conn.execute(
                """
                DELETE FROM session_memory_facts
                WHERE session_id = ? AND id LIKE ?
                """,
                (session["id"], f"{ref}%"),
            )
            return cursor.rowcount

    def set_session_summary(self, session_key: str, summary: str) -> bool:
        self.migrate()
        summary = summary.strip()
        with self.connect() as conn:
            session = conn.execute(
                "SELECT id FROM sessions WHERE session_key = ? AND status = 'active'",
                (session_key,),
            ).fetchone()
            if session is None:
                return False
            conn.execute(
                """
                INSERT INTO session_summaries (session_id, summary, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    summary = excluded.summary,
                    updated_at = excluded.updated_at
                """,
                (session["id"], summary, _utc_now()),
            )
        return True

    def get_session_summary(self, session_key: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT session_summaries.session_id,
                       session_summaries.summary,
                       session_summaries.updated_at
                FROM session_summaries
                JOIN sessions ON sessions.id = session_summaries.session_id
                WHERE sessions.session_key = ? AND sessions.status = 'active'
                """,
                (session_key,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_session_summary(self, session_key: str) -> bool:
        self.migrate()
        with self.connect() as conn:
            session = conn.execute(
                "SELECT id FROM sessions WHERE session_key = ? AND status = 'active'",
                (session_key,),
            ).fetchone()
            if session is None:
                return False
            cursor = conn.execute(
                "DELETE FROM session_summaries WHERE session_id = ?",
                (session["id"],),
            )
            return cursor.rowcount > 0

    def save_model_profile(
        self,
        *,
        name: str,
        provider: str,
        model_id: str,
        mode: str = "chat",
        context_window: int = 200_000,
        raw: dict[str, Any] | None = None,
        profile_id: str | None = None,
    ) -> str:
        """Persist secret-free model routing metadata and return profile id."""
        self.migrate()
        raw = raw or {}
        _assert_no_secret_keys(raw)
        profile_id = profile_id or name
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO model_profiles (
                    id, name, provider, model_id, mode, context_window, raw_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    provider = excluded.provider,
                    model_id = excluded.model_id,
                    mode = excluded.mode,
                    context_window = excluded.context_window,
                    raw_json = excluded.raw_json
                """,
                (
                    profile_id,
                    name,
                    provider,
                    model_id,
                    mode,
                    context_window,
                    json.dumps(raw, sort_keys=True),
                    _utc_now(),
                ),
            )
        return profile_id

    def list_model_profiles(self) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, name, provider, model_id, mode, context_window, raw_json, created_at
                FROM model_profiles
                ORDER BY name, created_at
                """
            ).fetchall()
        return [dict(row) for row in rows]

    def get_model_profile(self, profile_id_or_name: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, provider, model_id, mode, context_window, raw_json, created_at
                FROM model_profiles
                WHERE id = ? OR name = ?
                ORDER BY CASE WHEN id = ? THEN 0 ELSE 1 END, created_at
                LIMIT 1
                """,
                (profile_id_or_name, profile_id_or_name, profile_id_or_name),
            ).fetchone()
        return _row_to_dict(row)

    def set_session_model_profile(
        self, session_key: str, profile_id: str | None
    ) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET model_profile_id = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (profile_id, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def set_session_preset(self, session_key: str, preset_id: str | None) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET preset_id = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (preset_id, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def set_session_content_mode(self, session_key: str, content_mode: str) -> bool:
        self.migrate()
        if content_mode not in {"safe", "adult-fiction"}:
            raise ValueError("content_mode must be 'safe' or 'adult-fiction'")
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET content_mode = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (content_mode, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def set_session_adapter_mode(self, session_key: str, adapter_mode: str) -> bool:
        self.migrate()
        if adapter_mode not in {"fake", "hermes"}:
            raise ValueError("adapter_mode must be 'fake' or 'hermes'")
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET adapter_mode = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (adapter_mode, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def set_session_live_confirmed(self, session_key: str, enabled: bool) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE sessions
                SET live_confirmed = ?, updated_at = ?
                WHERE session_key = ? AND status = 'active'
                """,
                (1 if enabled else 0, _utc_now(), session_key),
            )
            return cursor.rowcount > 0

    def count_sessions_for_scope(self, scope_key: str, *, include_all: bool = False) -> int:
        self.migrate()
        where_scope = (
            "(sessions.scope_key = ? OR (sessions.scope_key IS NULL AND sessions.session_key = ?))"
        )
        if include_all:
            sql = f"SELECT COUNT(*) FROM sessions WHERE {where_scope}"
        else:
            sql = f"SELECT COUNT(*) FROM sessions WHERE {where_scope} AND sessions.status = 'active'"
        with self.connect() as conn:
            row = conn.execute(sql, (scope_key, scope_key)).fetchone()
        return row[0] if row else 0

    def list_sessions_for_scope(
        self, scope_key: str, *, include_all: bool = False, limit: int = 50, offset: int = 0
    ) -> list[dict[str, Any]]:
        """List sessions belonging to a scope (platform/chat/thread/user identity).

        By default only 'active' sessions are returned. Pass include_all=True to
        include 'ended' and 'archived' sessions as well.
        """
        self.migrate()
        where_scope = (
            "(sessions.scope_key = ? OR (sessions.scope_key IS NULL AND sessions.session_key = ?))"
        )
        params: tuple[Any, ...]
        if include_all:
            sql = f"""
                SELECT sessions.*, cards.name AS card_name
                FROM sessions
                LEFT JOIN cards ON cards.id = sessions.card_id
                WHERE {where_scope}
                ORDER BY sessions.updated_at DESC
                LIMIT ? OFFSET ?
            """
            params = (scope_key, scope_key, limit, offset)
        else:
            sql = f"""
                SELECT sessions.*, cards.name AS card_name
                FROM sessions
                LEFT JOIN cards ON cards.id = sessions.card_id
                WHERE {where_scope}
                  AND sessions.status = 'active'
                ORDER BY sessions.updated_at DESC
                LIMIT ? OFFSET ?
            """
            params = (scope_key, scope_key, limit, offset)
        with self.connect() as conn:
            rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    def rename_session(self, session_id: str, title: str) -> bool:
        """Set or clear the human-readable title for a session."""
        self.migrate()
        title_value: str | None = title.strip() if title.strip() else None
        with self.connect() as conn:
            cursor = conn.execute(
                "UPDATE sessions SET title = ?, updated_at = ? WHERE id = ?",
                (title_value, _utc_now(), session_id),
            )
            return cursor.rowcount > 0

    def archive_active_session(self, session_key: str) -> bool:
        """Archive the active session for session_key, freeing the key slot.

        The archived row's session_key is renamed to its own id (a UUID) so that
        a subsequent start_session call can claim the original session_key again.
        """
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM sessions WHERE session_key = ? AND status = 'active'",
                (session_key,),
            ).fetchone()
            if row is None:
                return False
            session_id = row["id"]
            conn.execute(
                """
                UPDATE sessions
                SET session_key = ?, status = 'archived', updated_at = ?
                WHERE id = ?
                """,
                (session_id, _utc_now(), session_id),
            )
        return True

    def clone_session(
        self,
        from_session_id: str,
        scope_key: str,
        *,
        title: str | None = None,
    ) -> dict[str, Any]:
        """Clone a session: create a new active session with same card/config and copy messages.

        The clone gets a fresh unique session_key derived from the scope_key so it can
        coexist with the source session. Use switch_to_session to make it the primary
        active session for the event identity.
        """
        self.migrate()
        clone_id = str(uuid4())
        clone_key = f"{scope_key}:b:{clone_id[:8]}"
        now = _utc_now()
        with self.connect() as conn:
            source_row = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (from_session_id,),
            ).fetchone()
            if source_row is None:
                raise ValueError(f"Source session not found: {from_session_id}")
            source = dict(source_row)
            source_scope = source.get("scope_key") or scope_key
            conn.execute(
                """
                INSERT INTO sessions (
                    id, session_key, scope_key, card_id, status,
                    content_mode, model_profile_id, preset_id, lorebook_id,
                    persona_id, adapter_mode, live_confirmed, title, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
                """,
                (
                    clone_id,
                    clone_key,
                    source_scope,
                    source.get("card_id"),
                    source.get("content_mode") or "safe",
                    source.get("model_profile_id"),
                    source.get("preset_id"),
                    source.get("lorebook_id"),
                    source.get("persona_id"),
                    source.get("adapter_mode") or "fake",
                    title,
                    now,
                    now,
                ),
            )
            messages = conn.execute(
                """
                SELECT role, content, metadata_json FROM messages
                WHERE session_id = ?
                ORDER BY created_at ASC, id ASC
                """,
                (from_session_id,),
            ).fetchall()
            message_base_time = datetime.now(timezone.utc)
            for index, msg in enumerate(messages):
                cloned_created_at = (message_base_time + timedelta(microseconds=index)).isoformat()
                conn.execute(
                    """
                    INSERT INTO messages (id, session_id, role, content, created_at, metadata_json)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid4()),
                        clone_id,
                        msg["role"],
                        msg["content"],
                        cloned_created_at,
                        msg["metadata_json"],
                    ),
                )
            cloned_row = conn.execute(
                """
                SELECT sessions.*, cards.name AS card_name
                FROM sessions
                LEFT JOIN cards ON cards.id = sessions.card_id
                WHERE sessions.id = ?
                """,
                (clone_id,),
            ).fetchone()
        result = _row_to_dict(cloned_row)
        if result is None:
            raise RuntimeError("clone_session: failed to read cloned session")
        return result

    def get_session_by_id_prefix(self, prefix: str) -> dict[str, Any] | None:
        """Find a session by a prefix of its id (case-sensitive)."""
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE id LIKE ? LIMIT 1",
                (f"{prefix}%",),
            ).fetchone()
        return _row_to_dict(row)

    def list_sessions_by_id_prefix_for_scope(
        self,
        scope_key: str,
        prefix: str,
        *,
        include_all: bool = True,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Find sessions with id prefix within a single caller scope."""
        self.migrate()
        where_scope = (
            "(sessions.scope_key = ? OR (sessions.scope_key IS NULL AND sessions.session_key = ?))"
        )
        status_clause = "" if include_all else " AND sessions.status = 'active'"
        sql = f"""
            SELECT sessions.*, cards.name AS card_name
            FROM sessions
            LEFT JOIN cards ON cards.id = sessions.card_id
            WHERE {where_scope}
              AND sessions.id LIKE ?
              {status_clause}
            ORDER BY sessions.updated_at DESC
            LIMIT ?
        """
        with self.connect() as conn:
            rows = conn.execute(sql, (scope_key, scope_key, f"{prefix}%", limit)).fetchall()
        return [dict(row) for row in rows]

    def switch_to_session(self, current_session_key: str, target_session_id: str) -> bool:
        """Make target_session_id the active session for current_session_key.

        Archives the currently-active session (renames its session_key to its own id
        to free the key slot), then updates the target's session_key to
        current_session_key and marks it active. Returns False if the target is not found.
        """
        self.migrate()
        now = _utc_now()
        with self.connect() as conn:
            target_row = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (target_session_id,),
            ).fetchone()
            if target_row is None:
                return False
            target = dict(target_row)
            target_scope = target.get("scope_key") or target.get("session_key")
            if target_scope != current_session_key:
                return False

            # Already active under current key — nothing to do.
            if target["session_key"] == current_session_key and target["status"] == "active":
                return True

            # Archive the current active session to free the key slot.
            current = conn.execute(
                "SELECT id FROM sessions WHERE session_key = ? AND status = 'active'",
                (current_session_key,),
            ).fetchone()
            if current and current["id"] != target_session_id:
                conn.execute(
                    """
                    UPDATE sessions
                    SET session_key = ?, status = 'archived', updated_at = ?
                    WHERE id = ?
                    """,
                    (current["id"], now, current["id"]),
                )

            # Activate target under current_session_key.
            conn.execute(
                """
                UPDATE sessions
                SET session_key = ?,
                    scope_key = COALESCE(scope_key, ?),
                    status = 'active',
                    updated_at = ?
                WHERE id = ?
                """,
                (current_session_key, current_session_key, now, target_session_id),
            )
        return True

    def get_card(self, card_id_or_name: str) -> dict[str, Any] | None:
        self.migrate()
        ref = card_id_or_name.strip()
        if ref.lower() == "last":
            return self._get_row_by_id(
                "cards",
                "id, name, data_json, created_at",
                self._last_card_id,
            )
        prefix = f"{ref}%"
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT id, name, data_json, created_at
                FROM cards
                WHERE id = ? OR name = ? OR id LIKE ?
                ORDER BY CASE WHEN id = ? THEN 0 WHEN name = ? THEN 1 ELSE 2 END, created_at
                LIMIT 1
                """,
                (ref, ref, prefix, ref, ref),
            ).fetchone()
        return _row_to_dict(row)

    def create_image_job(
        self,
        *,
        session_id: str,
        provider: str,
        model: str,
        mode: str,
        prompt: str,
        negative_prompt: str = "",
        source_message_id: str | None = None,
        status: str = "pending",
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self.migrate()
        job_id = str(uuid4())
        metadata_json = json.dumps(metadata or {}, sort_keys=True)
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO image_jobs (
                    id, session_id, provider, model, mode, prompt,
                    negative_prompt, source_message_id, status, created_at,
                    metadata_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job_id,
                    session_id,
                    provider,
                    model,
                    mode,
                    prompt,
                    negative_prompt,
                    source_message_id,
                    status,
                    _utc_now(),
                    metadata_json,
                ),
            )
        return job_id

    def complete_image_job(
        self,
        *,
        job_id: str,
        session_id: str,
        file_path: str,
        mime_type: str,
        width: int | None,
        height: int | None,
        prompt_snapshot: str,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self.migrate()
        asset_id = str(uuid4())
        now = _utc_now()
        metadata_json = json.dumps(metadata or {}, sort_keys=True)
        with self.connect() as conn:
            conn.execute(
                "UPDATE image_jobs SET status = 'completed', completed_at = ? WHERE id = ?",
                (now, job_id),
            )
            conn.execute(
                """
                INSERT INTO image_assets (
                    id, job_id, session_id, file_path, mime_type, width, height,
                    prompt_snapshot, metadata_json, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    asset_id,
                    job_id,
                    session_id,
                    file_path,
                    mime_type,
                    width,
                    height,
                    prompt_snapshot,
                    metadata_json,
                    now,
                ),
            )
        return asset_id

    def fail_image_job(self, job_id: str, error: str, metadata: dict[str, Any] | None = None) -> None:
        self.migrate()
        payload = dict(metadata or {})
        payload["error"] = error[:500]
        metadata_json = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        with self.connect() as conn:
            conn.execute(
                "UPDATE image_jobs SET status = 'failed', completed_at = ?, metadata_json = ? WHERE id = ?",
                (_utc_now(), metadata_json, job_id),
            )

    def get_last_image_job(self, session_id: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT image_jobs.*, image_assets.id AS asset_id,
                       image_assets.file_path, image_assets.mime_type,
                       image_assets.width, image_assets.height,
                       image_assets.prompt_snapshot,
                       image_assets.metadata_json AS asset_metadata_json,
                       image_assets.created_at AS asset_created_at
                FROM image_jobs
                LEFT JOIN image_assets ON image_assets.job_id = image_jobs.id
                WHERE image_jobs.session_id = ?
                ORDER BY image_jobs.created_at DESC, image_jobs.id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        return _row_to_dict(row)

    def count_image_jobs(self, session_id: str) -> int:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM image_jobs WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        return row[0] if row else 0

    def list_image_jobs(self, session_id: str, limit: int = 10, offset: int = 0) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT image_jobs.*, image_assets.id AS asset_id,
                       image_assets.file_path, image_assets.mime_type,
                       image_assets.width, image_assets.height,
                       image_assets.prompt_snapshot,
                       image_assets.metadata_json AS asset_metadata_json,
                       image_assets.created_at AS asset_created_at
                FROM image_jobs
                LEFT JOIN image_assets ON image_assets.job_id = image_jobs.id
                WHERE image_jobs.session_id = ?
                ORDER BY image_jobs.created_at DESC, image_jobs.id DESC
                LIMIT ? OFFSET ?
                """,
                (session_id, limit, offset),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_image_settings(self, session_id: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT settings_json FROM image_settings WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if not row:
            return {}
        try:
            value = json.loads(row[0] or "{}")
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def set_image_settings(self, session_id: str, settings: dict[str, Any]) -> None:
        self.migrate()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO image_settings (session_id, settings_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    settings_json = excluded.settings_json,
                    updated_at = excluded.updated_at
                """,
                (session_id, json.dumps(settings, ensure_ascii=False, sort_keys=True), _utc_now()),
            )

    def get_image_safety(self, session_id: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT safety_json FROM image_safety WHERE session_id = ?",
                (session_id,),
            ).fetchone()
        if not row:
            return {}
        try:
            value = json.loads(row[0] or "{}")
            return value if isinstance(value, dict) else {}
        except Exception:
            return {}

    def set_image_safety(self, session_id: str, safety: dict[str, Any]) -> None:
        self.migrate()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO image_safety (session_id, safety_json, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    safety_json = excluded.safety_json,
                    updated_at = excluded.updated_at
                """,
                (session_id, json.dumps(safety, ensure_ascii=False, sort_keys=True), _utc_now()),
            )

    def save_image_style(self, name: str, positive_template: str = "", negative_template: str = "", settings: dict[str, Any] | None = None) -> None:
        self.migrate()
        settings_json = json.dumps(settings or {}, ensure_ascii=False, sort_keys=True)
        now = _utc_now()
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO image_styles (name, positive_template, negative_template, settings_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    positive_template = excluded.positive_template,
                    negative_template = excluded.negative_template,
                    settings_json = excluded.settings_json,
                    updated_at = excluded.updated_at
                """,
                (name, positive_template, negative_template, settings_json, now, now),
            )

    def get_image_style(self, name: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM image_styles WHERE name = ?", (name,)
            ).fetchone()
        if not row:
            return None
        result = dict(row)
        try:
            result["settings"] = json.loads(result.get("settings_json") or "{}")
        except Exception:
            result["settings"] = {}
        return result

    def list_image_styles(self) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                "SELECT * FROM image_styles ORDER BY name ASC"
            ).fetchall()
        return [dict(row) for row in rows]

    def delete_image_style(self, name: str) -> bool:
        self.migrate()
        with self.connect() as conn:
            cur = conn.execute("DELETE FROM image_styles WHERE name = ?", (name,))
        return cur.rowcount > 0
