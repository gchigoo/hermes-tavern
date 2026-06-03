import sqlite3

from plugins.hermes_tavern.db import TavernStore


def _table_names(db_path):
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    return {row[0] for row in rows}


def test_migrate_creates_novel_tables(tmp_path):
    db_path = tmp_path / "tavern.sqlite3"
    store = TavernStore(db_path)

    store.migrate()

    tables = _table_names(db_path)
    assert {
        "novel_projects",
        "novel_chapters",
        "novel_scenes",
        "novel_canon",
        "novel_timeline",
    }.issubset(tables)


def test_novel_project_crud_and_counts(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("Aurora", "space opera")
    assert novel_project["title"] == "Aurora"
    assert novel_project["summary"] == "space opera"
    assert novel_project["status"] == "draft"
    assert novel_project["id"] > 0

    chapter = store.create_chapter(novel_project["id"], "Chapter One")
    assert chapter["project_id"] == novel_project["id"]
    assert chapter["chapter_number"] == 1

    listed = store.list_projects()
    assert len(listed) == 1
    assert listed[0]["chapter_count"] == 1

    fetched = store.get_project(novel_project["id"])
    assert fetched is not None
    assert fetched["id"] == novel_project["id"]

    no_project = store.get_project(999)
    assert no_project is None


def test_scene_crud_and_parent_validation(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("No Chapter")
    chapter = store.create_chapter(novel_project["id"], "Scene Setup")
    scene = store.create_scene(chapter["id"], "Opening")

    assert scene["chapter_id"] == chapter["id"]
    assert scene["scene_number"] == 1
    assert scene["session_id"] is None

    scenes = store.list_scenes(chapter["id"])
    assert len(scenes) == 1
    assert scenes[0]["title"] == "Opening"

    fetched = store.get_scene(scene["id"])
    assert fetched is not None
    assert fetched["title"] == "Opening"

    active_session = store.start_session("scope-aurora")
    linked = store.link_scene_session(scene["id"], active_session["id"])
    assert linked is True
    after_link = store.get_scene(scene["id"])
    assert after_link is not None
    assert after_link["session_id"] == active_session["id"]

    missing = ""
    try:
        store.create_chapter(9999, "Broken")
    except ValueError as exc:
        missing = str(exc)
    assert "Project not found" in missing

    missing = ""
    try:
        store.create_scene(9999, "Broken")
    except ValueError as exc:
        missing = str(exc)
    assert "Chapter not found" in missing

    missing = ""
    try:
        store.link_scene_session(9999, active_session["id"])
    except ValueError as exc:
        missing = str(exc)
    assert "Scene not found" in missing


def test_canon_group_default_and_prompt_ordering(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("Lore House")
    general_a = store.create_canon(novel_project["id"], "Sky", "Blue")
    general_b = store.create_canon(novel_project["id"], "Ground", "Brown")
    world = store.create_canon(novel_project["id"], "Laws", "Magic", group="world")

    canon = store.list_canon(novel_project["id"])
    assert len(canon) == 3
    assert {row["canon_group"] for row in canon} == {"general", "world"}
    assert general_a["canon_group"] == "general"

    grouped = store.list_canon(novel_project["id"], group="general")
    assert all(row["canon_group"] == "general" for row in grouped)
    assert len(grouped) == 2
    assert len(store.get_canon_for_prompt(novel_project["id"], limit=2)) == 2

    ordered = store.get_canon_for_prompt(novel_project["id"], limit=10)
    assert ordered[0]["id"] == world["id"]


def test_timeline_ordering(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Timeline")

    store.create_timeline_event(novel_project["id"], "2450.03", "Later", sort_key="2450.03")
    store.create_timeline_event(novel_project["id"], "2450.01", "First", sort_key="2450.01")
    store.create_timeline_event(novel_project["id"], "2450.02", "Middle", sort_key="2450.02")

    timeline = store.list_timeline(novel_project["id"])
    assert [event["event_date"] for event in timeline] == [
        "2450.01",
        "2450.02",
        "2450.03",
    ]


def test_export_project_markdown_structure(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("The Long Road", "adventure in winter")
    chapter = store.create_chapter(novel_project["id"], "Beginning")
    scene = store.create_scene(chapter["id"], "Dawn")
    session = store.start_session("scope-epic")
    store.link_scene_session(scene["id"], session["id"])
    store.append_message(session["id"], "user", "Hello.")
    store.append_message(session["id"], "assistant", "Welcome.")

    store.create_canon(novel_project["id"], "Climate", "Snow is common in the north")
    store.create_timeline_event(
        novel_project["id"],
        "Day 1",
        "Arrival",
        description="At camp."
    )

    markdown = store.export_project_markdown(novel_project["id"])

    assert "# The Long Road" in markdown
    assert "## Summary" in markdown
    assert "adventure in winter" in markdown
    assert "## Chapters" in markdown
    assert "### Chapter 1: Beginning" in markdown
    assert "#### Scene 1: Dawn" in markdown
    assert "user" in markdown
    assert "assistant" in markdown
    assert "## Canon" in markdown
    assert "Snow is common in the north" in markdown
    assert "## Timeline" in markdown
