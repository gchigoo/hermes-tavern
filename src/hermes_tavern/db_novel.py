"""Novel-domain persistence helpers for ``TavernStore``."""

from __future__ import annotations

from typing import Any

from hermes_tavern.db_utils import row_to_dict as _row_to_dict
from hermes_tavern.db_utils import utc_now as _utc_now


class NovelDBMixin:
    """Mixin implementing novel project/chapter/scene/canon/timeline persistence."""

    def _migrate_novel_schema(self, conn: Any) -> None:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS novel_projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_chapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                chapter_number INTEGER NOT NULL DEFAULT 1,
                summary TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_scenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chapter_id INTEGER NOT NULL REFERENCES novel_chapters(id) ON DELETE CASCADE,
                session_id TEXT REFERENCES sessions(id),
                title TEXT NOT NULL,
                summary TEXT NOT NULL DEFAULT '',
                scene_number INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL DEFAULT 'draft',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_canon (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                canon_group TEXT NOT NULL DEFAULT 'general',
                importance INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_timeline (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                event_date TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                chapter_id INTEGER REFERENCES novel_chapters(id),
                sort_key TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_scene_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id INTEGER NOT NULL UNIQUE REFERENCES novel_scenes(id) ON DELETE CASCADE,
                goal_text TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_scene_narration_controls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id INTEGER NOT NULL UNIQUE REFERENCES novel_scenes(id) ON DELETE CASCADE,
                pov_label TEXT NOT NULL DEFAULT '',
                tense TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_scene_beats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scene_id INTEGER NOT NULL REFERENCES novel_scenes(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                beat_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_project_style_guides (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL UNIQUE REFERENCES novel_projects(id) ON DELETE CASCADE,
                style_text TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_project_briefs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL UNIQUE REFERENCES novel_projects(id) ON DELETE CASCADE,
                project_type TEXT NOT NULL DEFAULT '',
                premise_text TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_project_outlines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL UNIQUE REFERENCES novel_projects(id) ON DELETE CASCADE,
                outline_text TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_relationship_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                state_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_locations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                description_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_style_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                sample_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_revision_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                note_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS novel_character_states (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                state_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE INDEX IF NOT EXISTS idx_novel_projects_created
                ON novel_projects(created_at);
            CREATE INDEX IF NOT EXISTS idx_novel_chapters_project
                ON novel_chapters(project_id, chapter_number);
            CREATE INDEX IF NOT EXISTS idx_novel_scenes_chapter
                ON novel_scenes(chapter_id, scene_number);
            CREATE INDEX IF NOT EXISTS idx_novel_scenes_session
                ON novel_scenes(session_id);
            CREATE INDEX IF NOT EXISTS idx_novel_canon_project
                ON novel_canon(project_id, canon_group, importance);
            CREATE INDEX IF NOT EXISTS idx_novel_timeline_project
                ON novel_timeline(project_id, sort_key, created_at);
            CREATE INDEX IF NOT EXISTS idx_novel_scene_goals_scene
                ON novel_scene_goals(scene_id);
            CREATE INDEX IF NOT EXISTS idx_novel_scene_narration_controls_scene
                ON novel_scene_narration_controls(scene_id);
            CREATE INDEX IF NOT EXISTS idx_novel_scene_beats_scene
                ON novel_scene_beats(scene_id, id);
            CREATE INDEX IF NOT EXISTS idx_novel_project_style_guides_project
                ON novel_project_style_guides(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_project_briefs_project
                ON novel_project_briefs(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_project_outlines_project
                ON novel_project_outlines(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_locations_project
                ON novel_locations(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_style_samples_project
                ON novel_style_samples(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_revision_notes_project
                ON novel_revision_notes(project_id, id);
            CREATE TABLE IF NOT EXISTS novel_organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                description_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS novel_plot_threads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
                label TEXT NOT NULL,
                description_text TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS novel_default_bindings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scope_type TEXT NOT NULL,
                scope_id INTEGER NOT NULL,
                asset_type TEXT NOT NULL,
                asset_id TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                updated_at TEXT NOT NULL DEFAULT (datetime('now')),
                UNIQUE(scope_type, scope_id, asset_type)
            );
            CREATE INDEX IF NOT EXISTS idx_novel_organizations_project
                ON novel_organizations(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_plot_threads_project
                ON novel_plot_threads(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_relationship_states_project
                ON novel_relationship_states(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_character_states_project
                ON novel_character_states(project_id);
            CREATE INDEX IF NOT EXISTS idx_novel_default_bindings_scope
                ON novel_default_bindings(scope_type, scope_id);
            """
        )

    def create_project(self, title: str, summary: str = "") -> dict[str, Any]:
        self.migrate()
        now = _utc_now()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO novel_projects (title, summary, status, created_at, updated_at)
                VALUES (?, ?, 'draft', ?, ?)
                """,
                (title, summary, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_projects WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_projects(self) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    np.*,
                    COALESCE(COUNT(nc.id), 0) AS chapter_count
                FROM novel_projects AS np
                LEFT JOIN novel_chapters AS nc
                    ON nc.project_id = np.id
                GROUP BY np.id
                ORDER BY np.created_at DESC, np.id DESC
                """
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT np.*, COALESCE(COUNT(nc.id), 0) AS chapter_count
                FROM novel_projects AS np
                LEFT JOIN novel_chapters AS nc
                    ON nc.project_id = np.id
                WHERE np.id = ?
                GROUP BY np.id
                """,
                (project_id,),
            ).fetchone()
        return _row_to_dict(row)

    def set_default_binding(
        self,
        scope_type: str,
        scope_id: int,
        asset_type: str,
        asset_id: str,
    ) -> dict[str, Any]:
        scope_type = (scope_type or "").strip().lower()
        asset_type = (asset_type or "").strip().lower()
        asset_id = str(asset_id or "").strip()
        valid_scope_types = {"project", "chapter", "scene"}
        if scope_type not in valid_scope_types:
            raise ValueError("Invalid scope type")
        valid_asset_types = {"card", "preset", "lorebook", "persona"}
        if asset_type not in valid_asset_types:
            raise ValueError("Invalid asset type")
        if not asset_id:
            raise ValueError("Asset not found")

        self.migrate()
        with self.connect() as conn:
            if scope_type == "project":
                scope = conn.execute(
                    "SELECT id FROM novel_projects WHERE id = ?",
                    (scope_id,),
                ).fetchone()
                if scope is None:
                    raise ValueError("Project not found")
            elif scope_type == "chapter":
                scope = conn.execute(
                    "SELECT id FROM novel_chapters WHERE id = ?",
                    (scope_id,),
                ).fetchone()
                if scope is None:
                    raise ValueError("Chapter not found")
            else:
                scope = conn.execute(
                    "SELECT id FROM novel_scenes WHERE id = ?",
                    (scope_id,),
                ).fetchone()
                if scope is None:
                    raise ValueError("Scene not found")

            asset_tables = {
                "card": ("cards", "Card not found"),
                "preset": ("presets", "Preset not found"),
                "lorebook": ("lorebooks", "Lorebook not found"),
                "persona": ("personas", "Persona not found"),
            }
            table_name, missing_error = asset_tables[asset_type]
            asset = conn.execute(
                f"SELECT id FROM {table_name} WHERE id = ?",
                (asset_id,),
            ).fetchone()
            if asset is None:
                raise ValueError(missing_error)

            del scope
            del asset

            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_default_bindings (
                    scope_type, scope_id, asset_type, asset_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(scope_type, scope_id, asset_type) DO UPDATE SET
                    asset_id = excluded.asset_id,
                    updated_at = excluded.updated_at
                """,
                (scope_type, scope_id, asset_type, asset_id, now, now),
            )
            binding_id = cursor.lastrowid or conn.execute(
                """
                SELECT id
                FROM novel_default_bindings
                WHERE scope_type = ? AND scope_id = ? AND asset_type = ?
                """,
                (scope_type, scope_id, asset_type),
            ).fetchone()[0]
            row = conn.execute(
                "SELECT * FROM novel_default_bindings WHERE id = ?",
                (binding_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_default_bindings(
        self,
        scope_type: str,
        scope_id: int,
    ) -> list[dict[str, Any]]:
        scope_type = (scope_type or "").strip().lower()
        if scope_type not in {"project", "chapter", "scene"}:
            raise ValueError("Invalid scope type")

        self.migrate()
        with self.connect() as conn:
            if scope_type == "project":
                scope = conn.execute(
                    "SELECT id FROM novel_projects WHERE id = ?",
                    (scope_id,),
                ).fetchone()
                if scope is None:
                    raise ValueError("Project not found")
            elif scope_type == "chapter":
                scope = conn.execute(
                    "SELECT id FROM novel_chapters WHERE id = ?",
                    (scope_id,),
                ).fetchone()
                if scope is None:
                    raise ValueError("Chapter not found")
            else:
                scope = conn.execute(
                    "SELECT id FROM novel_scenes WHERE id = ?",
                    (scope_id,),
                ).fetchone()
                if scope is None:
                    raise ValueError("Scene not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_default_bindings
                WHERE scope_type = ? AND scope_id = ?
                ORDER BY asset_type ASC, asset_id ASC
                """,
                (scope_type, scope_id),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def list_default_bindings_for_project(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT b.*
                FROM novel_default_bindings AS b
                WHERE
                    b.scope_type = 'project' AND b.scope_id = ?
                    OR b.scope_type = 'chapter' AND b.scope_id IN (
                        SELECT id FROM novel_chapters WHERE project_id = ?
                    )
                    OR b.scope_type = 'scene' AND b.scope_id IN (
                        SELECT s.id
                        FROM novel_scenes AS s
                        INNER JOIN novel_chapters AS c
                            ON c.id = s.chapter_id
                        WHERE c.project_id = ?
                    )
                ORDER BY b.scope_type ASC, b.scope_id ASC, b.asset_type ASC, b.asset_id ASC
                """,
                (project_id, project_id, project_id),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_default_binding(self, binding_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_default_bindings WHERE id = ?",
                (binding_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_default_binding(self, binding_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_default_bindings WHERE id = ?",
                (binding_id,),
            )
            return cursor.rowcount > 0

    def set_project_style_guide(
        self,
        project_id: int,
        style_text: str,
    ) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO novel_project_style_guides (
                    project_id, style_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    style_text = excluded.style_text,
                    updated_at = excluded.updated_at
                """,
                (project_id, style_text, now, now),
            )
            row = conn.execute(
                "SELECT * FROM novel_project_style_guides WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_project_style_guide(self, project_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            row = conn.execute(
                "SELECT * FROM novel_project_style_guides WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_project_style_guide(self, project_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            cursor = conn.execute(
                "DELETE FROM novel_project_style_guides WHERE project_id = ?",
                (project_id,),
            )
            return cursor.rowcount > 0

    def create_style_sample(
        self,
        project_id: int,
        label: str,
        sample_text: str,
    ) -> dict[str, Any]:
        label = (label or "").strip()
        sample_text = (sample_text or "").strip()
        if not label:
            raise ValueError("Style sample label cannot be blank")
        if not sample_text:
            raise ValueError("Style sample text cannot be blank")

        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_style_samples (
                    project_id,
                    label,
                    sample_text,
                    created_at,
                    updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, label, sample_text, now, now),
            )
            style_sample_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_style_samples WHERE id = ?",
                (style_sample_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_style_samples(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_style_samples
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_style_sample(self, style_sample_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_style_samples WHERE id = ?",
                (style_sample_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_style_sample(
        self,
        style_sample_id: int,
        sample_text: str,
    ) -> dict[str, Any] | None:
        sample_text = (sample_text or "").strip()
        if not sample_text:
            raise ValueError("Style sample text cannot be blank")

        now = _utc_now()
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE novel_style_samples
                SET sample_text = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (sample_text, now, style_sample_id),
            )
            if cursor.rowcount == 0:
                return None
            row = conn.execute(
                "SELECT * FROM novel_style_samples WHERE id = ?",
                (style_sample_id,),
            ).fetchone()
        return _row_to_dict(row)

    def delete_style_sample(self, style_sample_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_style_samples WHERE id = ?",
                (style_sample_id,),
            )
            return cursor.rowcount > 0

    def create_revision_note(
        self,
        project_id: int,
        label: str,
        note_text: str,
    ) -> dict[str, Any]:
        label = (label or "").strip()
        note_text = (note_text or "").strip()
        if not label:
            raise ValueError("Revision note label cannot be blank")
        if not note_text:
            raise ValueError("Revision note text cannot be blank")

        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_revision_notes (
                    project_id, label, note_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, label, note_text, now, now),
            )
            revision_note_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_revision_notes WHERE id = ?",
                (revision_note_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_revision_notes(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_revision_notes
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_revision_note(self, revision_note_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_revision_notes WHERE id = ?",
                (revision_note_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_revision_note(
        self,
        revision_note_id: int,
        note_text: str,
    ) -> dict[str, Any] | None:
        note_text = (note_text or "").strip()
        if not note_text:
            raise ValueError("Revision note text cannot be blank")

        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE novel_revision_notes
                SET note_text = ?, updated_at = ?
                WHERE id = ?
                """,
                (note_text, _utc_now(), revision_note_id),
            )
            if cursor.rowcount == 0:
                return None
            row = conn.execute(
                "SELECT * FROM novel_revision_notes WHERE id = ?",
                (revision_note_id,),
            ).fetchone()
        return _row_to_dict(row)

    def delete_revision_note(self, revision_note_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_revision_notes WHERE id = ?",
                (revision_note_id,),
            )
            return cursor.rowcount > 0

    def get_project_brief(self, project_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            row = conn.execute(
                "SELECT * FROM novel_project_briefs WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        brief = _row_to_dict(row)
        if brief is None:
            return None
        if not brief["project_type"].strip() and not brief["premise_text"].strip():
            return None
        return brief

    def set_project_brief_type(self, project_id: int, project_type: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            if project_type not in {"novel", "serial", "rp", "worldbuilding", "other"}:
                raise ValueError("Invalid project type")
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO novel_project_briefs (
                    project_id, project_type, created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    project_type = excluded.project_type,
                    updated_at = excluded.updated_at
                """,
                (project_id, project_type, now, now),
            )
            row = conn.execute(
                "SELECT * FROM novel_project_briefs WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_project_brief_type(self, project_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            row = conn.execute(
                "SELECT project_id, project_type, premise_text FROM novel_project_briefs WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if row is None:
                return False
            if row["project_type"] == "":
                return False
            if row["premise_text"].strip() == "":
                cursor = conn.execute(
                    "DELETE FROM novel_project_briefs WHERE project_id = ?",
                    (project_id,),
                )
                return cursor.rowcount > 0
            cursor = conn.execute(
                """
                UPDATE novel_project_briefs
                SET project_type = '', updated_at = ?
                WHERE project_id = ?
                """,
                (_utc_now(), project_id),
            )
            return cursor.rowcount > 0

    def set_project_premise(self, project_id: int, premise_text: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO novel_project_briefs (
                    project_id, premise_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    premise_text = excluded.premise_text,
                    updated_at = excluded.updated_at
                """,
                (project_id, premise_text, now, now),
            )
            row = conn.execute(
                "SELECT * FROM novel_project_briefs WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_project_premise(self, project_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            row = conn.execute(
                "SELECT project_id, project_type, premise_text FROM novel_project_briefs WHERE project_id = ?",
                (project_id,),
            ).fetchone()
            if row is None:
                return False
            if row["premise_text"] == "":
                return False
            if row["project_type"].strip() == "":
                cursor = conn.execute(
                    "DELETE FROM novel_project_briefs WHERE project_id = ?",
                    (project_id,),
                )
                return cursor.rowcount > 0
            cursor = conn.execute(
                """
                UPDATE novel_project_briefs
                SET premise_text = '', updated_at = ?
                WHERE project_id = ?
                """,
                (_utc_now(), project_id),
            )
            return cursor.rowcount > 0

    def set_project_outline(self, project_id: int, outline_text: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO novel_project_outlines (
                    project_id, outline_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(project_id) DO UPDATE SET
                    outline_text = excluded.outline_text,
                    updated_at = excluded.updated_at
                """,
                (project_id, outline_text, now, now),
            )
            row = conn.execute(
                "SELECT * FROM novel_project_outlines WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_project_outline(self, project_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            row = conn.execute(
                "SELECT * FROM novel_project_outlines WHERE project_id = ?",
                (project_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_project_outline(self, project_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            cursor = conn.execute(
                "DELETE FROM novel_project_outlines WHERE project_id = ?",
                (project_id,),
            )
            return cursor.rowcount > 0

    def create_relationship_state(self, project_id: int, label: str, state_text: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_relationship_states (
                    project_id, label, state_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, label, state_text, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_relationship_states WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def rename_relationship_state(self, relationship_id: int, label: str) -> dict[str, Any]:
        label = (label or "").strip()
        if not label:
            raise ValueError("Relationship label cannot be blank")

        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM novel_relationship_states WHERE id = ?",
                (relationship_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Relationship state not found")

            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_relationship_states
                SET label = ?, updated_at = ?
                WHERE id = ?
                """,
                (label, now, relationship_id),
            )
            updated = conn.execute(
                "SELECT * FROM novel_relationship_states WHERE id = ?",
                (relationship_id,),
            ).fetchone()
        return _row_to_dict(updated)

    def create_location(self, project_id: int, label: str, description_text: str) -> dict[str, Any]:
        if not (label or "").strip():
            raise ValueError("Location label cannot be blank")
        if not (description_text or "").strip():
            raise ValueError("Location description cannot be blank")
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_locations (
                    project_id, label, description_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, label, description_text, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_locations WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_locations(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_locations
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_location(self, location_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_locations WHERE id = ?",
                (location_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_location(self, location_id: int, description_text: str) -> dict[str, Any]:
        if not (description_text or "").strip():
            raise ValueError("Location description cannot be blank")
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM novel_locations WHERE id = ?",
                (location_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Location not found")
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_locations
                SET description_text = ?, updated_at = ?
                WHERE id = ?
                """,
                (description_text, now, location_id),
            )
            updated = conn.execute(
                "SELECT * FROM novel_locations WHERE id = ?",
                (location_id,),
            ).fetchone()
        return _row_to_dict(updated)

    def delete_location(self, location_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_locations WHERE id = ?",
                (location_id,),
            )
            return cursor.rowcount > 0

    def create_organization(self, project_id: int, label: str, description_text: str) -> dict[str, Any]:
        if not (label or "").strip():
            raise ValueError("Organization label cannot be blank")
        if not (description_text or "").strip():
            raise ValueError("Organization description cannot be blank")
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_organizations (
                    project_id, label, description_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, label, description_text, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_organizations WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_organizations(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_organizations
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_organization(self, organization_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_organizations WHERE id = ?",
                (organization_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_organization(self, organization_id: int, description_text: str) -> dict[str, Any]:
        if not (description_text or "").strip():
            raise ValueError("Organization description cannot be blank")
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM novel_organizations WHERE id = ?",
                (organization_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Organization not found")
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_organizations
                SET description_text = ?, updated_at = ?
                WHERE id = ?
                """,
                (description_text, now, organization_id),
            )
            updated = conn.execute(
                "SELECT * FROM novel_organizations WHERE id = ?",
                (organization_id,),
            ).fetchone()
        return _row_to_dict(updated)

    def delete_organization(self, organization_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_organizations WHERE id = ?",
                (organization_id,),
            )
            return cursor.rowcount > 0

    def create_plot_thread(self, project_id: int, label: str, description_text: str) -> dict[str, Any]:
        if not (label or "").strip():
            raise ValueError("Plot thread label cannot be blank")
        if not (description_text or "").strip():
            raise ValueError("Plot thread description cannot be blank")
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_plot_threads (
                    project_id, label, description_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, label, description_text, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_plot_threads WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_plot_threads(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_plot_threads
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_plot_thread(self, plot_thread_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_plot_threads WHERE id = ?",
                (plot_thread_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_plot_thread(self, plot_thread_id: int, description_text: str) -> dict[str, Any]:
        if not (description_text or "").strip():
            raise ValueError("Plot thread description cannot be blank")
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM novel_plot_threads WHERE id = ?",
                (plot_thread_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Plot thread not found")
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_plot_threads
                SET description_text = ?, updated_at = ?
                WHERE id = ?
                """,
                (description_text, now, plot_thread_id),
            )
            updated = conn.execute(
                "SELECT * FROM novel_plot_threads WHERE id = ?",
                (plot_thread_id,),
            ).fetchone()
        return _row_to_dict(updated)

    def delete_plot_thread(self, plot_thread_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_plot_threads WHERE id = ?",
                (plot_thread_id,),
            )
            return cursor.rowcount > 0

    def list_relationship_states(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_relationship_states
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_relationship_state(self, relationship_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_relationship_states WHERE id = ?",
                (relationship_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_relationship_state(self, relationship_id: int, state_text: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM novel_relationship_states WHERE id = ?",
                (relationship_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Relationship state not found")
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_relationship_states
                SET state_text = ?, updated_at = ?
                WHERE id = ?
                """,
                (state_text, now, relationship_id),
            )
            updated = conn.execute(
                "SELECT * FROM novel_relationship_states WHERE id = ?",
                (relationship_id,),
            ).fetchone()
        return _row_to_dict(updated)

    def delete_relationship_state(self, relationship_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_relationship_states WHERE id = ?",
                (relationship_id,),
            )
            return cursor.rowcount > 0

    def create_character_state(self, project_id: int, label: str, state_text: str) -> dict[str, Any]:
        if not (label or "").strip():
            raise ValueError("Character state label cannot be blank")
        if not (state_text or "").strip():
            raise ValueError("Character state text cannot be blank")
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_character_states (
                    project_id, label, state_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (project_id, label, state_text, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_character_states WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_character_states(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_character_states
                WHERE project_id = ?
                ORDER BY id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_character_state(self, character_state_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_character_states WHERE id = ?",
                (character_state_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_character_state(self, character_state_id: int, state_text: str) -> dict[str, Any]:
        if not (state_text or "").strip():
            raise ValueError("Character state text cannot be blank")
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id FROM novel_character_states WHERE id = ?",
                (character_state_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Character state not found")
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_character_states
                SET state_text = ?, updated_at = ?
                WHERE id = ?
                """,
                (state_text, now, character_state_id),
            )
            updated = conn.execute(
                "SELECT * FROM novel_character_states WHERE id = ?",
                (character_state_id,),
            ).fetchone()
        return _row_to_dict(updated)

    def delete_character_state(self, character_state_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_character_states WHERE id = ?",
                (character_state_id,),
            )
            return cursor.rowcount > 0

    def create_chapter(self, project_id: int, title: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            novel_project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if novel_project is None:
                raise ValueError("Project not found")
            chapter_count = conn.execute(
                """
                SELECT COALESCE(MAX(chapter_number), 0) + 1
                FROM novel_chapters
                WHERE project_id = ?
                """,
                (project_id,),
            ).fetchone()[0]
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_chapters (
                    project_id, title, chapter_number, summary, status, created_at, updated_at
                )
                VALUES (?, ?, ?, '', 'draft', ?, ?)
                """,
                (project_id, title, chapter_count, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_chapters WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_chapters(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            novel_project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if novel_project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_chapters
                WHERE project_id = ?
                ORDER BY chapter_number ASC, id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_chapter(self, chapter_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_chapter_summary(self, chapter_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Chapter not found")
            if not (row["summary"] or "").strip():
                return None
        return _row_to_dict(row)

    def set_chapter_summary(self, chapter_id: int, summary: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            chapter = conn.execute(
                "SELECT id FROM novel_chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
            if chapter is None:
                raise ValueError("Chapter not found")
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_chapters
                SET summary = ?, updated_at = ?
                WHERE id = ?
                """,
                (summary, now, chapter_id),
            )
            row = conn.execute(
                "SELECT * FROM novel_chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_chapter_summary(self, chapter_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id, summary FROM novel_chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Chapter not found")
            was_set = row["summary"] != ""
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_chapters
                SET summary = '', updated_at = ?
                WHERE id = ?
                """,
                (now, chapter_id),
            )
            return was_set

    def create_scene(
        self,
        chapter_id: int,
        title: str,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            chapter = conn.execute(
                "SELECT id FROM novel_chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
            if chapter is None:
                raise ValueError("Chapter not found")
            if session_id is not None:
                session = conn.execute(
                    "SELECT id FROM sessions WHERE id = ?",
                    (session_id,),
                ).fetchone()
                if session is None:
                    raise ValueError("Session not found")
            scene_count = conn.execute(
                """
                SELECT COALESCE(MAX(scene_number), 0) + 1
                FROM novel_scenes
                WHERE chapter_id = ?
                """,
                (chapter_id,),
            ).fetchone()[0]
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_scenes (
                    chapter_id, session_id, title, summary, scene_number, status, created_at, updated_at
                )
                VALUES (?, ?, ?, '', ?, 'draft', ?, ?)
                """,
                (chapter_id, session_id, title, scene_count, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_scenes WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_scenes(self, chapter_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            chapter = conn.execute(
                "SELECT id FROM novel_chapters WHERE id = ?",
                (chapter_id,),
            ).fetchone()
            if chapter is None:
                raise ValueError("Chapter not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_scenes
                WHERE chapter_id = ?
                ORDER BY scene_number ASC, id ASC
                """,
                (chapter_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_scene(self, scene_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_scene_summary(self, scene_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Scene not found")
            if not (row["summary"] or "").strip():
                return None
        return _row_to_dict(row)

    def set_scene_summary(self, scene_id: int, summary: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_scenes
                SET summary = ?, updated_at = ?
                WHERE id = ?
                """,
                (summary, now, scene_id),
            )
            row = conn.execute(
                "SELECT * FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_scene_summary(self, scene_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT id, summary FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if row is None:
                raise ValueError("Scene not found")
            was_set = row["summary"] != ""
            now = _utc_now()
            conn.execute(
                """
                UPDATE novel_scenes
                SET summary = '', updated_at = ?
                WHERE id = ?
                """,
                (now, scene_id),
            )
            return was_set

    def set_scene_goal(self, scene_id: int, goal_text: str) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            now = _utc_now()
            conn.execute(
                """
                INSERT INTO novel_scene_goals (
                    scene_id, goal_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?)
                ON CONFLICT(scene_id) DO UPDATE SET
                    goal_text = excluded.goal_text,
                    updated_at = excluded.updated_at
                """,
                (scene_id, goal_text, now, now),
            )
            row = conn.execute(
                "SELECT * FROM novel_scene_goals WHERE scene_id = ?",
                (scene_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_scene_goal(self, scene_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            row = conn.execute(
                "SELECT * FROM novel_scene_goals WHERE scene_id = ?",
                (scene_id,),
            ).fetchone()
        return _row_to_dict(row)

    def create_scene_beat(
        self,
        scene_id: int,
        label: str,
        beat_text: str,
    ) -> dict[str, Any]:
        label = (label or "").strip()
        beat_text = (beat_text or "").strip()
        if not label:
            raise ValueError("Scene beat label cannot be blank")
        if not beat_text:
            raise ValueError("Scene beat text cannot be blank")

        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_scene_beats (
                    scene_id, label, beat_text, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (scene_id, label, beat_text, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_scene_beats WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_scene_beats(self, scene_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_scene_beats
                WHERE scene_id = ?
                ORDER BY id ASC
                """,
                (scene_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_scene_beat(self, beat_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM novel_scene_beats WHERE id = ?",
                (beat_id,),
            ).fetchone()
        return _row_to_dict(row)

    def update_scene_beat(self, beat_id: int, beat_text: str) -> dict[str, Any] | None:
        beat_text = (beat_text or "").strip()
        if not beat_text:
            raise ValueError("Scene beat text cannot be blank")

        now = _utc_now()
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE novel_scene_beats
                SET beat_text = ?, updated_at = ?
                WHERE id = ?
                """,
                (beat_text, now, beat_id),
            )
            if cursor.rowcount == 0:
                return None
            row = conn.execute(
                "SELECT * FROM novel_scene_beats WHERE id = ?",
                (beat_id,),
            ).fetchone()
        return _row_to_dict(row)

    def delete_scene_beat(self, beat_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            cursor = conn.execute(
                "DELETE FROM novel_scene_beats WHERE id = ?",
                (beat_id,),
            )
            return cursor.rowcount > 0

    def clear_scene_goal(self, scene_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            cursor = conn.execute(
                "DELETE FROM novel_scene_goals WHERE scene_id = ?",
                (scene_id,),
            )
            return cursor.rowcount > 0

    def set_scene_narration_controls(
        self,
        scene_id: int,
        *,
        pov_label: str | None = None,
        tense: str | None = None,
    ) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")

            existing = conn.execute(
                "SELECT * FROM novel_scene_narration_controls WHERE scene_id = ?",
                (scene_id,),
            ).fetchone()
            current_pov = existing["pov_label"] if existing is not None else ""
            current_tense = existing["tense"] if existing is not None else ""

            if pov_label is None:
                next_pov = current_pov
            else:
                next_pov = pov_label

            if tense is None:
                next_tense = current_tense
            else:
                if tense != "" and tense not in {"past", "present"}:
                    raise ValueError("Invalid tense")
                next_tense = tense

            if next_pov == "" and next_tense == "":
                if existing is not None:
                    conn.execute(
                        "DELETE FROM novel_scene_narration_controls WHERE scene_id = ?",
                        (scene_id,),
                    )
                return None

            now = _utc_now()
            if existing is not None:
                conn.execute(
                    """
                    UPDATE novel_scene_narration_controls
                    SET pov_label = ?, tense = ?, updated_at = ?
                    WHERE scene_id = ?
                    """,
                    (next_pov, next_tense, now, scene_id),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO novel_scene_narration_controls (
                        scene_id, pov_label, tense, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (scene_id, next_pov, next_tense, now, now),
                )
            row = conn.execute(
                "SELECT * FROM novel_scene_narration_controls WHERE scene_id = ?",
                (scene_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_scene_narration_controls(self, scene_id: int) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            row = conn.execute(
                "SELECT * FROM novel_scene_narration_controls WHERE scene_id = ?",
                (scene_id,),
            ).fetchone()
        return _row_to_dict(row)

    def clear_scene_narration_controls(self, scene_id: int) -> bool:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            cursor = conn.execute(
                "DELETE FROM novel_scene_narration_controls WHERE scene_id = ?",
                (scene_id,),
            )
            return cursor.rowcount > 0

    def get_scene_narration_controls_for_session(self, session_id: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT nssc.*
                FROM novel_scenes AS ns
                JOIN novel_scene_narration_controls AS nssc
                    ON nssc.scene_id = ns.id
                WHERE ns.session_id = ?
                ORDER BY ns.updated_at DESC, ns.id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_scene_goal_for_session(self, session_id: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT nsg.*
                FROM novel_scenes AS ns
                JOIN novel_scene_goals AS nsg
                    ON nsg.scene_id = ns.id
                WHERE ns.session_id = ?
                ORDER BY ns.updated_at DESC, ns.id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_project_style_guide_for_session(self, session_id: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    npsg.*,
                    np.title AS project_title
                FROM novel_scenes AS ns
                JOIN novel_chapters AS nc
                    ON nc.id = ns.chapter_id
                JOIN novel_projects AS np
                    ON np.id = nc.project_id
                JOIN novel_project_style_guides AS npsg
                    ON npsg.project_id = np.id
                WHERE ns.session_id = ?
                ORDER BY ns.updated_at DESC, ns.id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        return _row_to_dict(row)

    def get_project_id_for_session(self, session_id: str) -> int | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT np.id AS project_id
                FROM novel_scenes AS ns
                JOIN novel_chapters AS nc
                    ON nc.id = ns.chapter_id
                JOIN novel_projects AS np
                    ON np.id = nc.project_id
                WHERE ns.session_id = ?
                ORDER BY ns.updated_at DESC, ns.id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        return row["project_id"] if row else None

    def get_novel_context_for_session(self, session_id: str) -> dict[str, Any] | None:
        self.migrate()
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT
                    np.title AS project_title,
                    nc.title AS chapter_title,
                    ns.title AS scene_title,
                    ns.id AS scene_id
                FROM novel_scenes AS ns
                JOIN novel_chapters AS nc
                    ON nc.id = ns.chapter_id
                JOIN novel_projects AS np
                    ON np.id = nc.project_id
                WHERE ns.session_id = ?
                ORDER BY ns.updated_at DESC, ns.id DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()
        return _row_to_dict(row)

    def link_scene_session(self, scene_id: int, session_id: str) -> bool:
        self.migrate()
        with self.connect() as conn:
            scene = conn.execute(
                "SELECT id FROM novel_scenes WHERE id = ?",
                (scene_id,),
            ).fetchone()
            if scene is None:
                raise ValueError("Scene not found")
            session = conn.execute(
                "SELECT id FROM sessions WHERE id = ?",
                (session_id,),
            ).fetchone()
            if session is None:
                raise ValueError("Session not found")
            cursor = conn.execute(
                """
                UPDATE novel_scenes
                SET session_id = ?, updated_at = ?
                WHERE id = ?
                """,
                (session_id, _utc_now(), scene_id),
            )
            return cursor.rowcount > 0

    def create_canon(
        self,
        project_id: int,
        title: str,
        content: str,
        group: str = "general",
    ) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            novel_project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if novel_project is None:
                raise ValueError("Project not found")
            effective_group = group or "general"
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_canon (
                    project_id, title, content, canon_group, importance, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 0, ?, ?)
                """,
                (project_id, title, content, effective_group, now, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_canon WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_canon(self, project_id: int, group: str | None = None) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            novel_project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if novel_project is None:
                raise ValueError("Project not found")
            query = """
                SELECT *
                FROM novel_canon
                WHERE project_id = ?
            """
            params: list[Any] = [project_id]
            if group is not None:
                query += " AND canon_group = ?"
                params.append(group)
            query += " ORDER BY importance DESC, created_at DESC, id DESC"
            rows = conn.execute(query, params).fetchall()
        return [_row_to_dict(row) for row in rows]

    def get_canon_for_prompt(self, project_id: int, limit: int = 10) -> list[dict[str, Any]]:
        self.migrate()
        canons = self.list_canon(project_id)
        return canons[:limit]

    def create_timeline_event(
        self,
        project_id: int,
        event_date: str,
        title: str,
        description: str = "",
        sort_key: str = "",
    ) -> dict[str, Any]:
        self.migrate()
        with self.connect() as conn:
            novel_project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if novel_project is None:
                raise ValueError("Project not found")
            now = _utc_now()
            cursor = conn.execute(
                """
                INSERT INTO novel_timeline (
                    project_id, event_date, title, description, sort_key, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (project_id, event_date, title, description, sort_key, now),
            )
            row_id = cursor.lastrowid
            row = conn.execute(
                "SELECT * FROM novel_timeline WHERE id = ?",
                (row_id,),
            ).fetchone()
        return _row_to_dict(row)

    def list_timeline(self, project_id: int) -> list[dict[str, Any]]:
        self.migrate()
        with self.connect() as conn:
            novel_project = conn.execute(
                "SELECT id FROM novel_projects WHERE id = ?",
                (project_id,),
            ).fetchone()
            if novel_project is None:
                raise ValueError("Project not found")
            rows = conn.execute(
                """
                SELECT *
                FROM novel_timeline
                WHERE project_id = ?
                ORDER BY sort_key ASC, id ASC
                """,
                (project_id,),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def export_project_markdown(self, project_id: int) -> str:
        self.migrate()
        novel_project = self.get_project(project_id)
        if novel_project is None:
            raise ValueError("Project not found")
        chapters = self.list_chapters(project_id)
        canons = self.list_canon(project_id)
        timeline = self.list_timeline(project_id)
        style_guide = self.get_project_style_guide(project_id)
        style_samples = self.list_style_samples(project_id)
        brief = self.get_project_brief(project_id)
        outline = self.get_project_outline(project_id)
        locations = self.list_locations(project_id)
        plot_threads = self.list_plot_threads(project_id)
        relationships = self.list_relationship_states(project_id)

        lines: list[str] = [
            f"# {novel_project['title']}",
            "",
            "## Summary",
            novel_project["summary"] or "",
            "",
        ]
        if brief is not None:
            project_type = brief["project_type"].strip()
            premise_text = brief["premise_text"].strip()
            if project_type or premise_text:
                lines.append("## Project Brief")
                if project_type:
                    lines.append(f"Type: {project_type}")
                if premise_text:
                    lines.append(f"Premise: {premise_text}")
                lines.append("")
        if outline is not None and outline["outline_text"].strip():
            lines.extend([
                "## Outline",
                outline["outline_text"],
                "",
            ])
        style_text = style_guide["style_text"] if style_guide is not None else ""
        if style_text.strip():
            lines.extend(
                [
                    "## Style Guide",
                    style_text,
                    "",
                ]
            )

        if style_samples:
            lines.extend(
                [
                    "## Style Samples",
                    "",
                ]
            )
            for sample in style_samples:
                lines.append(f"### {sample['label']}")
                lines.append("")
                lines.append(sample['sample_text'])
                lines.append("")

        if locations:
            lines.extend(
                [
                    "## Locations",
                    "",
                ]
            )
            for location in locations:
                lines.append(f"- {location['label']}: {location['description_text']}")
            lines.append("")

        organizations = self.list_organizations(project_id)
        if organizations:
            lines.extend(
                [
                    "## Organizations",
                    "",
                ]
            )
            for organization in organizations:
                lines.append(
                    f"- {organization['label']}: {organization['description_text']}"
                )
            lines.append("")

        if plot_threads:
            lines.extend(
                [
                    "## Plot Threads",
                    "",
                ]
            )
            for plot_thread in plot_threads:
                lines.append(
                    f"- {plot_thread['label']}: {plot_thread['description_text']}"
                )
            lines.append("")

        characters = self.list_character_states(project_id)
        if characters:
            lines.extend(
                [
                    "## Characters",
                    "",
                ]
            )
            for character in characters:
                lines.append(f"- {character['label']}: {character['state_text']}")
            lines.append("")

        if relationships:
            lines.extend(
                [
                    "## Relationships",
                    "",
                ]
            )
            for relationship in relationships:
                lines.append(f"- {relationship['label']}: {relationship['state_text']}")
            lines.append("")

        revision_notes = self.list_revision_notes(novel_project["id"])
        if revision_notes:
            lines.extend(
                [
                    "## Revision Notes",
                    "",
                ]
            )
            for revision_note in revision_notes:
                lines.append(
                    f"- {revision_note['label']}: {revision_note['note_text']}"
                )
            lines.append("")

        default_bindings = self.list_default_bindings_for_project(novel_project["id"])
        if default_bindings:
            lines.extend(
                [
                    "## Default Bindings",
                    "",
                ]
            )
            for binding in default_bindings:
                lines.append(
                    f"- [{binding['id']}] {binding['scope_type']}:{binding['scope_id']} "
                    f"-> {binding['asset_type']}:{binding['asset_id']}"
                )
            lines.append("")

        lines.append("## Chapters")

        if chapters:
            for chapter in chapters:
                lines.append(
                    f"### Chapter {chapter['chapter_number']}: {chapter['title']}"
                )
                chapter_summary = (chapter["summary"] or "").strip()
                if chapter_summary:
                    lines.append(f"Summary: {chapter_summary}")
                scenes = self.list_scenes(chapter["id"])
                if scenes:
                    for scene in scenes:
                        lines.append("")
                        lines.append(f"#### Scene {scene['scene_number']}: {scene['title']}")
                        scene_summary = (scene["summary"] or "").strip()
                        if scene_summary:
                            lines.append(f"Summary: {scene_summary}")
                        scene_goal = self.get_scene_goal(scene["id"])
                        if scene_goal and scene_goal["goal_text"].strip():
                            lines.append(f"Goal: {scene_goal['goal_text']}")
                        scene_beats = self.list_scene_beats(scene["id"])
                        if scene_beats:
                            lines.append("Scene beats:")
                            for beat in scene_beats:
                                lines.append(f"- {beat['label']}: {beat['beat_text']}")
                        scene_narration_controls = self.get_scene_narration_controls(scene["id"])
                        if scene_narration_controls is not None:
                            pov_label = scene_narration_controls["pov_label"].strip()
                            tense = scene_narration_controls["tense"].strip()
                            if pov_label or tense:
                                lines.append("Scene narration controls:")
                                if pov_label:
                                    lines.append(f"POV: {pov_label}")
                                if tense:
                                    lines.append(f"Tense: {tense}")
                        if scene["session_id"]:
                            with self.connect() as conn:
                                messages = conn.execute(
                                    """
                                    SELECT role, content
                                    FROM messages
                                    WHERE session_id = ?
                                    ORDER BY created_at ASC, id ASC
                                    """,
                                    (scene["session_id"],),
                                ).fetchall()
                            if messages:
                                for message in messages:
                                    lines.append(f"- **{message['role']}**: {message['content']}")
                            else:
                                lines.append("*No messages yet.*")
                        else:
                            lines.append("*No session linked.*")
                else:
                    lines.append("No scenes yet.")
        else:
            lines.append("No chapters yet.")

        lines.extend(
            [
                "",
                "## Canon",
            ]
        )
        if canons:
            grouped = {}
            for canon in canons:
                grouped.setdefault(canon["canon_group"], []).append(canon)
            for group, items in grouped.items():
                lines.append(f"### {group}")
                for item in items:
                    lines.append(f"- **{item['title']}**: {item['content']}")
        else:
            lines.append("No canon entries.")

        lines.extend(
            [
                "",
                "## Timeline",
            ]
        )
        if timeline:
            for event in timeline:
                description = event["description"]
                suffix = f" — {description}" if description else ""
                lines.append(f"- **{event['event_date']}**: {event['title']}{suffix}")
        else:
            lines.append("No timeline events.")

        return "\n".join(lines)
