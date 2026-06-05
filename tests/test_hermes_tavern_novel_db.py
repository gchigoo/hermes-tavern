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
        "novel_project_style_guides",
        "novel_project_briefs",
        "novel_project_outlines",
        "novel_relationship_states",
        "novel_character_states",
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
        "novel_project_style_guides",
        "novel_project_briefs",
        "novel_project_outlines",
        "novel_relationship_states",
        "novel_character_states",
    }

    with sqlite3.connect(db_path) as conn:
        indexes = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='index'
                    AND tbl_name='novel_project_style_guides'
                """
            ).fetchall()
        }
    assert "idx_novel_project_style_guides_project" in indexes
    with sqlite3.connect(db_path) as conn:
        brief_indexes = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='index'
                    AND tbl_name='novel_project_briefs'
                """
            ).fetchall()
    }
    assert "idx_novel_project_briefs_project" in brief_indexes
    with sqlite3.connect(db_path) as conn:
        relationship_indexes = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='index'
                    AND tbl_name='novel_relationship_states'
                """
            ).fetchall()
        }
    assert "idx_novel_relationship_states_project" in relationship_indexes
    with sqlite3.connect(db_path) as conn:
        character_indexes = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type='index'
                    AND tbl_name='novel_character_states'
                """
            ).fetchall()
        }
    assert "idx_novel_character_states_project" in character_indexes


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


def test_project_style_guide_set_update_get(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Voice", "distinctive")

    created = store.set_project_style_guide(
        novel_project["id"],
        "voice: first-person\npace: brisk",
    )
    assert created["project_id"] == novel_project["id"]
    assert created["style_text"] == "voice: first-person\npace: brisk"

    fetched = store.get_project_style_guide(novel_project["id"])
    assert fetched is not None
    assert fetched["style_text"] == "voice: first-person\npace: brisk"

    updated = store.set_project_style_guide(
        novel_project["id"],
        "voice: second-person\npace: methodical",
    )
    assert updated["id"] == created["id"]
    assert updated["style_text"] == "voice: second-person\npace: methodical"
    assert updated["updated_at"] >= created["updated_at"]
    assert store.get_project_style_guide(novel_project["id"]) == updated


def test_project_outline_set_update_get(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Plot Outline", "plot")

    created = store.set_project_outline(
        novel_project["id"],
        "Act One: The world breaks.",
    )
    assert created["project_id"] == novel_project["id"]
    assert created["outline_text"] == "Act One: The world breaks."

    fetched = store.get_project_outline(novel_project["id"])
    assert fetched is not None
    assert fetched["outline_text"] == "Act One: The world breaks."

    updated = store.set_project_outline(
        novel_project["id"],
        "Act One: The world mends.",
    )
    assert updated["id"] == created["id"]
    assert updated["outline_text"] == "Act One: The world mends."
    assert updated["updated_at"] >= created["updated_at"]
    assert store.get_project_outline(novel_project["id"]) == updated


def test_project_outline_clear_returns_bool(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Outline Memory")
    assert store.clear_project_outline(novel_project["id"]) is False

    store.set_project_outline(novel_project["id"], "opening arc")
    assert store.clear_project_outline(novel_project["id"]) is True
    assert store.get_project_outline(novel_project["id"]) is None
    assert store.clear_project_outline(novel_project["id"]) is False


def test_project_outline_missing_project_raises(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    try:
        store.get_project_outline(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")


def test_relationship_state_crud_and_missing_owner_errors(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    project = store.create_project("Relationship State")

    created = store.create_relationship_state(
        project["id"],
        "mara-elya",
        "Trust is built on silence and hard bargains.",
    )
    assert created["project_id"] == project["id"]
    assert created["label"] == "mara-elya"
    assert created["state_text"] == "Trust is built on silence and hard bargains."

    listed = store.list_relationship_states(project["id"])
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]
    assert listed[0]["label"] == created["label"]

    fetched = store.get_relationship_state(created["id"])
    assert fetched is not None
    assert fetched["state_text"] == created["state_text"]

    updated = store.update_relationship_state(created["id"], "Trust frays, then strengthens.")
    assert updated["id"] == created["id"]
    assert updated["state_text"] == "Trust frays, then strengthens."
    assert updated["updated_at"] >= created["updated_at"]

    assert store.delete_relationship_state(created["id"]) is True
    assert store.get_relationship_state(created["id"]) is None
    assert store.delete_relationship_state(created["id"]) is False

    try:
        store.create_relationship_state(999, "mara-elya", "missing")
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.list_relationship_states(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.update_relationship_state(999, "stale")
    except ValueError as exc:
        assert str(exc) == "Relationship state not found"
    else:
        raise AssertionError("Expected ValueError for missing relationship state")

    try:
        store.set_project_outline(999, "text")
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.clear_project_outline(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")


def test_character_state_crud_and_missing_owner_errors(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    project = store.create_project("Character State")

    created = store.create_character_state(
        project["id"],
        "mara-ilya",
        "Trust is built on silence and hard bargains.",
    )
    assert created["project_id"] == project["id"]
    assert created["label"] == "mara-ilya"
    assert created["state_text"] == "Trust is built on silence and hard bargains."

    listed = store.list_character_states(project["id"])
    assert len(listed) == 1
    assert listed[0]["id"] == created["id"]
    assert listed[0]["label"] == created["label"]

    fetched = store.get_character_state(created["id"])
    assert fetched is not None
    assert fetched["state_text"] == created["state_text"]

    updated = store.update_character_state(created["id"], "Trust frays, then strengthens.")
    assert updated["id"] == created["id"]
    assert updated["state_text"] == "Trust frays, then strengthens."
    assert updated["label"] == created["label"]
    assert updated["updated_at"] >= created["updated_at"]

    assert store.delete_character_state(created["id"]) is True
    assert store.get_character_state(created["id"]) is None
    assert store.delete_character_state(created["id"]) is False

    try:
        store.create_character_state(999, "mara-ilya", "missing")
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.list_character_states(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.update_character_state(999, "stale")
    except ValueError as exc:
        assert str(exc) == "Character state not found"
    else:
        raise AssertionError("Expected ValueError for missing character state")


def test_character_state_blank_label_and_state_rejected(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    project = store.create_project("Character State")

    try:
        store.create_character_state(project["id"], " ", "State text")
    except ValueError as exc:
        assert str(exc) == "Character state label cannot be blank"
    else:
        raise AssertionError("Expected ValueError for blank label")

    try:
        store.create_character_state(project["id"], "mara-ilya", "   ")
    except ValueError as exc:
        assert str(exc) == "Character state text cannot be blank"
    else:
        raise AssertionError("Expected ValueError for blank state text")

    created = store.create_character_state(project["id"], "mara-ilya", "first")
    try:
        store.update_character_state(created["id"], "   ")
    except ValueError as exc:
        assert str(exc) == "Character state text cannot be blank"
    else:
        raise AssertionError("Expected ValueError for blank state text on update")


def test_project_style_guide_clear_returns_bool(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Style Memory")
    assert store.clear_project_style_guide(novel_project["id"]) is False

    store.set_project_style_guide(novel_project["id"], "tone: warm")
    assert store.clear_project_style_guide(novel_project["id"]) is True
    assert store.get_project_style_guide(novel_project["id"]) is None
    assert store.clear_project_style_guide(novel_project["id"]) is False


def test_project_brief_set_update_get_preserve_fields(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Project Briefs", "field test")

    type_set = store.set_project_brief_type(novel_project["id"], "novel")
    assert type_set["project_id"] == novel_project["id"]
    assert type_set["project_type"] == "novel"
    assert type_set["premise_text"] == ""

    fetched_after_type = store.get_project_brief(novel_project["id"])
    assert fetched_after_type is not None
    assert fetched_after_type["project_type"] == "novel"
    assert fetched_after_type["premise_text"] == ""

    premise_set = store.set_project_premise(
        novel_project["id"],
        "A detective awakens in an empty city.",
    )
    assert premise_set["project_type"] == "novel"
    assert (
        premise_set["premise_text"] == "A detective awakens in an empty city."
    )

    fetched_after_premise = store.get_project_brief(novel_project["id"])
    assert fetched_after_premise is not None
    assert fetched_after_premise["project_type"] == "novel"
    assert (
        fetched_after_premise["premise_text"] == "A detective awakens in an empty city."
    )

    updated_type = store.set_project_brief_type(novel_project["id"], "rp")
    assert updated_type["id"] == premise_set["id"]
    assert updated_type["project_type"] == "rp"
    assert (
        updated_type["premise_text"] == "A detective awakens in an empty city."
    )


def test_project_brief_clear_preserves_remaining_and_deletes_last_visible(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Project Brief Clear", "keep one")
    store.set_project_brief_type(novel_project["id"], "serial")
    store.set_project_premise(novel_project["id"], "An epic with no ending.")

    assert store.clear_project_brief_type(novel_project["id"]) is True
    only_premise = store.get_project_brief(novel_project["id"])
    assert only_premise is not None
    assert only_premise["project_type"] == ""
    assert only_premise["premise_text"] == "An epic with no ending."

    assert store.clear_project_premise(novel_project["id"]) is True
    assert store.get_project_brief(novel_project["id"]) is None


def test_project_brief_missing_project_raises(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    try:
        store.get_project_brief(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.set_project_brief_type(999, "novel")
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.set_project_premise(999, "none")
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.clear_project_brief_type(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.clear_project_premise(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")


def test_project_brief_invalid_type_does_not_mutate_existing_data(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Brief Validation", "unchanged")
    original = store.set_project_brief_type(novel_project["id"], "novel")
    original = store.set_project_premise(
        novel_project["id"],
        "A city made of mirrors.",
    )

    try:
        store.set_project_brief_type(novel_project["id"], "invalid")
    except ValueError as exc:
        assert str(exc) == "Invalid project type"
    else:
        raise AssertionError("Expected ValueError for invalid project type")

    after_invalid = store.get_project_brief(novel_project["id"])
    assert after_invalid is not None
    assert after_invalid["project_type"] == original["project_type"]
    assert after_invalid["premise_text"] == original["premise_text"]


def test_project_style_guide_missing_project_raises(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    try:
        store.set_project_style_guide(999, "anything")
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.get_project_style_guide(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")

    try:
        store.clear_project_style_guide(999)
    except ValueError as exc:
        assert str(exc) == "Project not found"
    else:
        raise AssertionError("Expected ValueError for missing project")


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


def test_chapter_summary_set_update_get_clear(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Chapter Summary Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter One")

    set_once = store.set_chapter_summary(chapter["id"], "A cold wind moves through the harbor.")
    assert set_once["id"] == chapter["id"]
    assert set_once["summary"] == "A cold wind moves through the harbor."

    summary = store.get_chapter_summary(chapter["id"])
    assert summary is not None
    assert summary["summary"] == "A cold wind moves through the harbor."
    assert summary["id"] == chapter["id"]

    set_twice = store.set_chapter_summary(chapter["id"], "The harbor still remembers the storm.")
    assert set_twice["id"] == set_once["id"]
    assert set_twice["summary"] == "The harbor still remembers the storm."
    assert set_twice["updated_at"] >= set_once["updated_at"]

    fetched = store.get_chapter_summary(chapter["id"])
    assert fetched is not None
    assert fetched["summary"] == "The harbor still remembers the storm."

    assert store.clear_chapter_summary(chapter["id"]) is True
    assert store.get_chapter_summary(chapter["id"]) is None
    assert store.get_chapter(chapter["id"]) is not None
    assert store.get_chapter(chapter["id"])["summary"] == ""
    assert store.clear_chapter_summary(chapter["id"]) is False


def test_chapter_summary_missing_chapter_errors(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    try:
        store.get_chapter_summary(9999)
    except ValueError as exc:
        assert str(exc) == "Chapter not found"
    else:
        raise AssertionError("Expected ValueError for missing chapter")

    try:
        store.set_chapter_summary(9999, "No chapter")
    except ValueError as exc:
        assert str(exc) == "Chapter not found"
    else:
        raise AssertionError("Expected ValueError for missing chapter")

    try:
        store.clear_chapter_summary(9999)
    except ValueError as exc:
        assert str(exc) == "Chapter not found"
    else:
        raise AssertionError("Expected ValueError for missing chapter")


def test_scene_summary_set_update_get_clear(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Scene Summary Project")
    chapter = store.create_chapter(novel_project["id"], "Chapter One")
    scene = store.create_scene(chapter["id"], "Opening")

    set_once = store.set_scene_summary(scene["id"], "Torchlight and fog gather above the docks.")
    assert set_once["id"] == scene["id"]
    assert set_once["summary"] == "Torchlight and fog gather above the docks."

    summary = store.get_scene_summary(scene["id"])
    assert summary is not None
    assert summary["summary"] == "Torchlight and fog gather above the docks."
    assert summary["id"] == scene["id"]

    set_twice = store.set_scene_summary(scene["id"], "Fog thins, revealing lanterns.")
    assert set_twice["id"] == set_once["id"]
    assert set_twice["summary"] == "Fog thins, revealing lanterns."
    assert set_twice["updated_at"] >= set_once["updated_at"]

    fetched = store.get_scene_summary(scene["id"])
    assert fetched is not None
    assert fetched["summary"] == "Fog thins, revealing lanterns."

    assert store.clear_scene_summary(scene["id"]) is True
    assert store.get_scene_summary(scene["id"]) is None
    assert store.get_scene(scene["id"]) is not None
    assert store.get_scene(scene["id"])["summary"] == ""
    assert store.clear_scene_summary(scene["id"]) is False


def test_scene_summary_missing_scene_errors(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    try:
        store.get_scene_summary(9999)
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")

    try:
        store.set_scene_summary(9999, "No scene")
    except ValueError as exc:
        assert str(exc) == "Scene not found"
    else:
        raise AssertionError("Expected ValueError for missing scene")

    try:
        store.clear_scene_summary(9999)
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


def test_project_style_guide_for_session_uses_linked_scene_only(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    project_with_style = store.create_project("Session Style Project", "for sessions")
    chapter = store.create_chapter(project_with_style["id"], "Chapter 1")
    styled_scene = store.create_scene(chapter["id"], "Styled Scene")
    other_scene = store.create_scene(chapter["id"], "Non styled scene")

    store.set_project_style_guide(project_with_style["id"], "voice: cinematic")

    session = store.start_session("session-style-linked")
    store.link_scene_session(styled_scene["id"], session["id"])

    linked_style = store.get_project_style_guide_for_session(session["id"])
    assert linked_style is not None
    assert linked_style["project_id"] == project_with_style["id"]
    assert linked_style["style_text"] == "voice: cinematic"
    assert linked_style["project_title"] == "Session Style Project"

    no_style_session = store.start_session("session-style-none")
    no_style_project = store.create_project("Session Style Missing")
    no_style_chapter = store.create_chapter(no_style_project["id"], "Chapter 1")
    no_style_scene = store.create_scene(no_style_chapter["id"], "Unstyled Scene")
    store.link_scene_session(no_style_scene["id"], no_style_session["id"])
    assert store.get_project_style_guide_for_session(no_style_session["id"]) is None

    other_styled_project = store.create_project("Other Style Project")
    store.set_project_style_guide(other_styled_project["id"], "voice: minimalist")
    other_project_chapter = store.create_chapter(other_styled_project["id"], "Chapter 1")
    other_project_scene = store.create_scene(other_project_chapter["id"], "Other Scene")
    other_session = store.start_session("session-style-other")
    store.link_scene_session(other_project_scene["id"], other_session["id"])

    other_styled = store.get_project_style_guide_for_session(other_session["id"])
    assert other_styled is not None
    assert other_styled["project_title"] == "Other Style Project"


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
    store.set_scene_narration_controls(
        scene["id"],
        pov_label="third-person limited: Mara",
        tense="past",
    )
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
    assert "Scene narration controls:" in markdown
    assert "POV: third-person limited: Mara" in markdown
    assert "Tense: past" in markdown
    assert "user" in markdown
    assert "assistant" in markdown
    assert (
        markdown.index("#### Scene 1: Dawn")
        < markdown.index("Goal: Locate the hidden shrine")
        < markdown.index("Scene narration controls:")
        < markdown.index("POV: third-person limited: Mara")
        < markdown.index("Tense: past")
        < markdown.index("- **user**: Hello.")
    )
    assert "## Canon" in markdown
    assert "Snow is common in the north" in markdown
    assert "## Timeline" in markdown


def test_export_project_markdown_includes_summary_lines_for_chapter_and_scene_in_order(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("Summary Project", "first light")
    chapter = store.create_chapter(novel_project["id"], "Arrival")
    scene = store.create_scene(chapter["id"], "Dock")
    store.set_chapter_summary(chapter["id"], "Opening chapter marker: dawn.")
    store.set_scene_summary(scene["id"], "Opening scene marker: rain.")
    store.set_scene_goal(scene["id"], "Find the signal fire.")
    store.set_scene_narration_controls(
        scene["id"],
        pov_label="third-person limited",
        tense="past",
    )

    markdown = store.export_project_markdown(novel_project["id"])

    chapter_heading = "### Chapter 1: Arrival"
    chapter_summary = "Summary: Opening chapter marker: dawn."
    scene_heading = "#### Scene 1: Dock"
    scene_summary = "Summary: Opening scene marker: rain."
    goal = "Goal: Find the signal fire."
    narration = "Scene narration controls:"

    assert chapter_heading in markdown
    assert chapter_summary in markdown
    assert scene_heading in markdown
    assert scene_summary in markdown
    assert goal in markdown
    assert narration in markdown
    assert (
        markdown.index(chapter_heading)
        < markdown.index(chapter_summary)
        < markdown.index(scene_heading)
        < markdown.index(scene_summary)
        < markdown.index(goal)
        < markdown.index(narration)
    )


def test_export_project_markdown_omits_empty_summary_lines_in_chapters_section(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("Omitted Summary Project")
    chapter = store.create_chapter(novel_project["id"], "Arrival")
    scene = store.create_scene(chapter["id"], "Dock")
    store.set_chapter_summary(chapter["id"], "   ")
    store.set_scene_summary(scene["id"], "\n  \t")

    markdown = store.export_project_markdown(novel_project["id"])

    chapters_section = markdown[
        markdown.index("## Chapters") : markdown.index("## Canon")
    ]
    assert "Summary:" not in chapters_section
    assert store.get_chapter(chapter["id"])["summary"] == "   "
    assert store.get_scene(scene["id"])["summary"] == "\n  \t"


def test_export_project_markdown_place_narration_controls_before_no_session_fallback(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("The Long Road")
    chapter = store.create_chapter(novel_project["id"], "Dusk")
    scene = store.create_scene(chapter["id"], "Night")
    store.set_scene_narration_controls(
        scene["id"],
        pov_label="first-person",
        tense="present",
    )

    markdown = store.export_project_markdown(novel_project["id"])

    assert "#### Scene 1: Night" in markdown
    assert "Scene narration controls:" in markdown
    assert "POV: first-person" in markdown
    assert "Tense: present" in markdown
    assert markdown.index("Scene narration controls:") < markdown.index("*No session linked.*")


def test_export_project_markdown_omits_empty_narration_controls_block(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("The Long Road")
    chapter = store.create_chapter(novel_project["id"], "Dawn")
    scene = store.create_scene(chapter["id"], "Quiet")

    markdown_without_controls = store.export_project_markdown(novel_project["id"])
    assert "Scene narration controls:" not in markdown_without_controls

    store.set_scene_narration_controls(scene["id"], tense="present")
    markdown_with_tense = store.export_project_markdown(novel_project["id"])
    assert "Scene narration controls:" in markdown_with_tense
    assert "POV:" not in markdown_with_tense
    assert "Tense: present" in markdown_with_tense

    store.set_scene_narration_controls(scene["id"], pov_label="", tense="")
    markdown_after_clear = store.export_project_markdown(novel_project["id"])
    assert "Scene narration controls:" not in markdown_after_clear


def test_export_project_markdown_includes_nonempty_style_guide_and_orders_after_summary(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    novel_project = store.create_project("Style Project", "A clean and bright arc")
    store.set_project_style_guide(
        novel_project["id"],
        "Tone: lyrical\nWorldbuilding: dense, sensory",
    )
    chapter = store.create_chapter(novel_project["id"], "Opening")
    scene = store.create_scene(chapter["id"], "Arrival")
    markdown = store.export_project_markdown(novel_project["id"])

    assert "## Summary" in markdown
    assert "## Style Guide" in markdown
    assert "## Chapters" in markdown
    assert "Tone: lyrical\nWorldbuilding: dense, sensory" in markdown
    assert (
        markdown.index("## Summary")
        < markdown.index("## Style Guide")
        < markdown.index("## Chapters")
    )
    style_section = markdown[
        markdown.index("## Style Guide") : markdown.index("## Chapters")
    ]
    assert "Tone: lyrical\nWorldbuilding: dense, sensory" in style_section


def test_export_project_markdown_includes_relationships_after_style_guide_before_chapters(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    project = store.create_project("Relationship Export", "interpersonal arc")
    store.set_project_style_guide(project["id"], "Tone: intimate")
    store.create_character_state(
        project["id"],
        "mara",
        "Confidence with a scar.",
    )
    store.create_relationship_state(
        project["id"],
        "mara-elya",
        "Trust deepens through shared danger.",
    )
    store.create_relationship_state(
        project["id"],
        "mara-kai",
        "Arguments hide an old wound.",
    )
    store.create_chapter(project["id"], "Opening")

    markdown = store.export_project_markdown(project["id"])

    assert "## Style Guide" in markdown
    assert "## Characters" in markdown
    assert "## Relationships" in markdown
    assert "## Chapters" in markdown
    assert (
        markdown.index("## Style Guide")
        < markdown.index("## Characters")
        < markdown.index("## Relationships")
        < markdown.index("## Chapters")
    )
    assert "Confidence with a scar." in markdown
    assert "Trust deepens through shared danger." in markdown
    assert "Arguments hide an old wound." in markdown


def test_export_project_markdown_omits_characters_when_empty(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    project = store.create_project("Characters Missing", "no character rows")
    markdown = store.export_project_markdown(project["id"])

    assert "## Characters" not in markdown


def test_export_project_markdown_orders_sections_with_characters(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    project = store.create_project("Character Section Order", "ordered for export")
    store.set_project_brief_type(project["id"], "novel")
    store.set_project_outline(project["id"], "Act One")
    store.set_project_style_guide(project["id"], "Tone: clean")
    store.create_character_state(
        project["id"],
        "mara",
        "Confidence with a scar.",
    )
    store.create_relationship_state(
        project["id"],
        "mara-elya",
        "Trust deepens through shared danger.",
    )
    store.create_chapter(project["id"], "Opening")

    markdown = store.export_project_markdown(project["id"])
    assert (
        markdown.index("## Summary")
        < markdown.index("## Project Brief")
        < markdown.index("## Outline")
        < markdown.index("## Style Guide")
        < markdown.index("## Characters")
        < markdown.index("## Relationships")
        < markdown.index("## Chapters")
        < markdown.index("## Canon")
        < markdown.index("## Timeline")
    )


def test_export_project_markdown_omits_relationships_when_empty(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    project = store.create_project("Relationships Missing", "no relationship rows")
    store.set_project_style_guide(project["id"], "Tone: quiet")

    markdown = store.export_project_markdown(project["id"])

    assert "## Relationships" not in markdown


def test_export_project_markdown_omits_style_guide_when_absent_or_whitespace_only(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")

    with_style_row = store.create_project("Whitespace Style Project")
    markdown_without_style = store.export_project_markdown(with_style_row["id"])
    assert "## Style Guide" not in markdown_without_style

    store.set_project_style_guide(with_style_row["id"], "   \n  ")
    markdown_after_whitespace = store.export_project_markdown(with_style_row["id"])
    assert "## Style Guide" not in markdown_after_whitespace


def test_export_project_markdown_includes_project_brief_and_orders_after_summary(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project(
        "Brief Export Project",
        "A summary that stays first.",
    )
    store.set_project_brief_type(novel_project["id"], "worldbuilding")
    store.set_project_premise(
        novel_project["id"],
        "An atlas of the fractured moon.",
    )
    store.set_project_style_guide(novel_project["id"], "Tone: measured")
    store.create_chapter(novel_project["id"], "First")

    markdown = store.export_project_markdown(novel_project["id"])
    assert "## Project Brief" in markdown
    assert "Type: worldbuilding" in markdown
    assert "Premise: An atlas of the fractured moon." in markdown
    assert "## Style Guide" in markdown
    assert (
        markdown.index("## Summary")
        < markdown.index("## Project Brief")
        < markdown.index("## Style Guide")
    )
    assert "## Project Brief" in markdown
    assert "## Style Guide" in markdown
    assert markdown.index("## Project Brief") < markdown.index("## Style Guide")


def test_export_project_markdown_includes_outline_and_orders_correctly(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project(
        "Outline Export",
        "A story with a map.",
    )
    store.set_project_brief_type(novel_project["id"], "novel")
    store.set_project_outline(
        novel_project["id"],
        "Act One: The descent.\nAct Two: The reckoning.\nAct Three: The dawn.",
    )
    store.set_project_style_guide(
        novel_project["id"],
        "Tone: cinematic",
    )

    markdown = store.export_project_markdown(novel_project["id"])
    assert "## Project Brief" in markdown
    assert "## Outline" in markdown
    assert "## Style Guide" in markdown
    assert (
        markdown.index("## Project Brief")
        < markdown.index("## Outline")
        < markdown.index("## Style Guide")
    )


def test_export_project_markdown_omits_outline_when_empty(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Outline Absent", "no outline yet")
    store.set_project_style_guide(novel_project["id"], "Tone: terse")

    markdown = store.export_project_markdown(novel_project["id"])
    assert "## Outline" not in markdown


def test_export_project_markdown_omits_project_brief_when_empty(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    novel_project = store.create_project("Empty Brief Export", "no brief yet")
    markdown = store.export_project_markdown(novel_project["id"])
    assert "## Project Brief" not in markdown


def test_export_project_markdown_project_brief_omits_blank_field_labels(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    type_only = store.create_project("Type Only", "classification")
    premise_only = store.create_project("Premise Only", "story seed")

    store.set_project_brief_type(type_only["id"], "other")
    type_markdown = store.export_project_markdown(type_only["id"])
    assert "## Project Brief" in type_markdown
    assert "Type: other" in type_markdown
    assert "Premise:" not in type_markdown

    store.set_project_premise(premise_only["id"], "A lantern guards the harbor.")
    premise_markdown = store.export_project_markdown(premise_only["id"])
    assert "## Project Brief" in premise_markdown
    assert "Premise: A lantern guards the harbor." in premise_markdown
    assert "Type:" not in premise_markdown
