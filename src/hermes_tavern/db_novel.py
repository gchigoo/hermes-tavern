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

        lines: list[str] = [
            f"# {novel_project['title']}",
            "",
            "## Summary",
            novel_project["summary"] or "",
            "",
            "## Chapters",
        ]

        if chapters:
            for chapter in chapters:
                lines.append(
                    f"### Chapter {chapter['chapter_number']}: {chapter['title']}"
                )
                scenes = self.list_scenes(chapter["id"])
                if scenes:
                    for scene in scenes:
                        lines.append("")
                        lines.append(f"#### Scene {scene['scene_number']}: {scene['title']}")
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
