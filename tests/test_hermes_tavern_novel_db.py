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
        "novel_scene_goals",
        "novel_scene_narration_controls",
    }.issubset(tables)
    novel_tables = {name for name in tables if name.startswith("novel_")}
    assert novel_tables == {
        "novel_projects",
        "novel_chapters",
        "novel_scenes",
        "novel_canon",
        "novel_timeline",
        "novel_scene_goals",
        "novel_scene_narration_controls",
    }


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


def test_scene_goal_set_update_get_clear(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Goals Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter 1")
    scene = store.create_scene(chapter["id"], "Goal Scene")

    set_once = store.set_scene_goal(scene["id"], "Reach the gate before dawn")
    assert set_once["scene_id"] == scene["id"]
    assert set_once["goal_text"] == "Reach the gate before dawn"

    retrieved = store.get_scene_goal(scene["id"])
    assert retrieved is not None
    assert retrieved["goal_text"] == "Reach the gate before dawn"
    assert retrieved["created_at"] == set_once["created_at"]

    set_twice = store.set_scene_goal(scene["id"], "Find the hidden key")
    assert set_twice["id"] == set_once["id"]
    assert set_twice["goal_text"] == "Find the hidden key"
    assert set_twice["updated_at"] >= set_once["updated_at"]

    fetched = store.get_scene_goal(scene["id"])
    assert fetched is not None
    assert fetched["goal_text"] == "Find the hidden key"

    assert store.clear_scene_goal(scene["id"]) is True
    assert store.get_scene_goal(scene["id"]) is None
    assert store.clear_scene_goal(scene["id"]) is False


def test_scene_narration_controls_set_get_update_and_partial_updates(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Narration Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter 1")
    scene = store.create_scene(chapter["id"], "Narration Scene")

    set_once = store.set_scene_narration_controls(
        scene["id"],
        pov_label="third-person limited: Mara",
        tense="past",
    )
    assert set_once is not None
    assert set_once["scene_id"] == scene["id"]
    assert set_once["pov_label"] == "third-person limited: Mara"
    assert set_once["tense"] == "past"

    retrieved = store.get_scene_narration_controls(scene["id"])
    assert retrieved is not None
    assert retrieved["pov_label"] == "third-person limited: Mara"
    assert retrieved["tense"] == "past"

    updated = store.set_scene_narration_controls(
        scene["id"],
        tense="present",
    )
    assert updated is not None
    assert updated["pov_label"] == "third-person limited: Mara"
    assert updated["tense"] == "present"

    updated = store.set_scene_narration_controls(scene["id"], pov_label="first-person")
    assert updated is not None
    assert updated["pov_label"] == "first-person"
    assert updated["tense"] == "present"


def test_scene_narration_controls_blank_clears_field_and_both(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Narration Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter 1")
    scene = store.create_scene(chapter["id"], "Narration Scene")

    store.set_scene_narration_controls(scene["id"], pov_label="Omniscient", tense="present")

    cleared_pov = store.set_scene_narration_controls(scene["id"], pov_label="")
    assert cleared_pov is not None
    assert cleared_pov["pov_label"] == ""
    assert cleared_pov["tense"] == "present"

    cleared_all = store.set_scene_narration_controls(scene["id"], pov_label="", tense="")
    assert cleared_all is None
    assert store.get_scene_narration_controls(scene["id"]) is None


def test_scene_narration_controls_clear_is_idempotent(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Narration Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter 1")
    scene = store.create_scene(chapter["id"], "Narration Scene")

    assert store.clear_scene_narration_controls(scene["id"]) is False
    store.set_scene_narration_controls(scene["id"], pov_label="Close")
    assert store.clear_scene_narration_controls(scene["id"]) is True
    assert store.clear_scene_narration_controls(scene["id"]) is False


def test_scene_narration_controls_missing_scene_errors(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    missing_id = 999

    try:
        store.set_scene_narration_controls(missing_id, pov_label="No one")
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")

    try:
        store.get_scene_narration_controls(missing_id)
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")

    try:
        store.clear_scene_narration_controls(missing_id)
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")


def test_scene_narration_controls_invalid_tense_raises(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Narration Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter 1")
    scene = store.create_scene(chapter["id"], "Narration Scene")

    try:
        store.set_scene_narration_controls(scene["id"], tense="future")
    except ValueError as exc:
        assert str(exc) == "Invalid tense"
    else:
        raise AssertionError("Expected ValueError for invalid tense")


def test_scene_narration_controls_for_session_uses_linked_scene_only(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Session Scope Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter 1")
    linked = store.create_scene(chapter["id"], "Linked Scene")
    unlinked = store.create_scene(chapter["id"], "Other Scene")

    session = store.start_session("scope-linked")
    store.link_scene_session(linked["id"], session["id"])

    store.set_scene_narration_controls(linked["id"], pov_label="Linked POV", tense="past")
    store.set_scene_narration_controls(unlinked["id"], pov_label="Unlinked POV", tense="present")

    linked_controls = store.get_scene_narration_controls_for_session(session["id"])
    assert linked_controls is not None
    assert linked_controls["scene_id"] == linked["id"]
    assert linked_controls["pov_label"] == "Linked POV"

    other_session = store.start_session("scope-unlinked")
    assert store.get_scene_narration_controls_for_session(other_session["id"]) is None


def test_scene_goal_missing_scene_errors(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    missing_id = 999

    try:
        store.set_scene_goal(missing_id, "Impossible")
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")

    try:
        store.get_scene_goal(missing_id)
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")

    try:
        store.clear_scene_goal(missing_id)
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")


def test_scene_goal_for_session_uses_scene_link(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Session Scope Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter 1")
    linked = store.create_scene(chapter["id"], "Linked Scene")
    unlinked = store.create_scene(chapter["id"], "Other Scene")

    session = store.start_session("scope-linked")
    store.link_scene_session(linked["id"], session["id"])

    store.set_scene_goal(linked["id"], "Open the gates")
    store.set_scene_goal(unlinked["id"], "Ignore this link")

    linked_goal = store.get_scene_goal_for_session(session["id"])
    assert linked_goal is not None
    assert linked_goal["scene_id"] == linked["id"]
    assert linked_goal["goal_text"] == "Open the gates"

    other_session = store.start_session("scope-unlinked")
    assert store.get_scene_goal_for_session(other_session["id"]) is None


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


def test_canon_group_empty_string_defaults_to_general(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("Lore House")
    blank_group = store.create_canon(
        novel_project["id"],
        "Sky",
        "Blue",
        group="",
    )

    assert blank_group["canon_group"] == "general"
    canon = store.list_canon(novel_project["id"])
    assert len(canon) == 1
    assert canon[0]["canon_group"] == "general"


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
    store.set_scene_goal(scene["id"], "Locate the hidden shrine")
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
    assert "Goal: Locate the hidden shrine" in markdown
    assert "user" in markdown
    assert "assistant" in markdown
    assert (
        markdown.index("#### Scene 1: Dawn")
        < markdown.index("Goal: Locate the hidden shrine")
        < markdown.index("- **user**: Hello.")
    )
    assert "## Canon" in markdown
    assert "Snow is common in the north" in markdown
    assert "## Timeline" in markdown
