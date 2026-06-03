import pytest
import sqlite3

from plugins.hermes_tavern.commands import TAVERN_COMMAND_TABLE
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.runtime import TavernRuntime
from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.presets import import_st_preset_json


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


def test_novel_command_table_has_five_families():
    assert "project" in TAVERN_COMMAND_TABLE
    assert "chapter" in TAVERN_COMMAND_TABLE
    assert "scene" in TAVERN_COMMAND_TABLE
    assert "canon" in TAVERN_COMMAND_TABLE
    assert "timeline" in TAVERN_COMMAND_TABLE

    for name in ("project", "chapter", "scene", "canon", "timeline"):
        entry = TAVERN_COMMAND_TABLE[name]
        assert entry.handler == f"_{name}_command"
    assert "/rp scene goal <scene-id> [text]" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene goal clear <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines


def test_project_routes_create_list_info_set(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    event = Event()

    created = runtime.handle_command_sync(
        RPCommand("project", ["create", "Skyline", "Journal"], "/rp project create Skyline Journal"),
        event,
    )
    assert "Hermes Tavern project created" in created

    project = runtime.store.get_project(1)
    assert project is not None
    assert project["title"] == "Skyline Journal"

    listed = runtime.handle_command_sync(RPCommand("project", ["list"], "/rp project list"), event)
    assert "Hermes Tavern novel projects" in listed
    assert "[1] Skyline Journal" in listed

    info = runtime.handle_command_sync(RPCommand("project", ["info", "1"], "/rp project info 1"), event)
    assert "Hermes Tavern project info" in info
    assert "id: 1" in info
    assert "title: Skyline Journal" in info

    set_ok = runtime.handle_command_sync(RPCommand("project", ["set", "1"], "/rp project set 1"), event)
    assert "Active novel project set" in set_ok

    followup_chapter = runtime.handle_command_sync(
        RPCommand("chapter", ["create", "Setup"], "/rp chapter create Setup"),
        event,
    )
    assert "Hermes Tavern chapter created" in followup_chapter


def test_project_list_includes_chapter_count_for_created_project(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    runtime.store.create_project("Atlas")
    runtime.handle_command_sync(RPCommand("chapter", ["create", "1", "Arrival"], "/rp chapter create 1 Arrival"), Event())
    listed = runtime.handle_command_sync(RPCommand("project", ["list"], "/rp project list"), Event())

    assert "Atlas" in listed
    assert "(chapters: 1, draft)" in listed


@pytest.mark.parametrize(
    "command, expected_prefix",
    [
        (RPCommand("project", ["info"], "/rp project info"), "Usage: /rp project info"),
        (RPCommand("project", ["set", "not-a-number"], "/rp project set not-a-number"), "Usage: /rp project set <id>"),
    ],
)
def test_project_routes_boundary_args(tmp_path, command, expected_prefix):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = runtime.handle_command_sync(command, Event())
    assert response.startswith(expected_prefix)


def test_chapter_routes_require_active_or_explicit_project(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    no_context = runtime.handle_command_sync(
        RPCommand("chapter", ["create", "First"], "/rp chapter create First"),
        Event(),
    )
    assert no_context == "No active novel project. Use /rp project set <id> or pass project-id."

    runtime.handle_command_sync(
        RPCommand("project", ["set", str(project["id"])], f"/rp project set {project['id']}"),
        Event(),
    )

    with_context = runtime.handle_command_sync(
        RPCommand("chapter", ["create", "First"], "/rp chapter create First"),
        Event(),
    )
    assert "Hermes Tavern chapter created" in with_context

    listed = runtime.handle_command_sync(
        RPCommand("chapter", ["list"], "/rp chapter list"),
        Event(),
    )
    assert "Hermes Tavern chapters for project [1]" in listed
    assert "Chapter 1: First" in listed


def test_chapter_routes_create_requires_existing_project(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("chapter", ["create", "9999", "Missing"], "/rp chapter create 9999 Missing"),
        Event(),
    )
    assert response == "No novel project found: 9999"


def test_project_export_returns_media_marker_and_path_under_profile_safe_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    runtime.store.create_project("Atlas", "A long voyage")
    chapter = runtime.store.create_chapter(1, "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")
    session = runtime.store.start_session("scope-epic")
    runtime.store.link_scene_session(scene["id"], session["id"])
    runtime.store.append_message(session["id"], "user", "Hello.")
    runtime.store.append_message(session["id"], "assistant", "Welcome.")
    runtime.store.create_canon(1, "Climate", "Snow is common.")
    runtime.store.create_timeline_event(1, "Day 1", "Departure", description="At dawn.")

    response = runtime.handle_command_sync(
        RPCommand("project", ["export", "1"], "/rp project export 1"),
        Event(),
    )

    assert "Project exported as Markdown." in response
    assert "file:" in response
    assert "MEDIA:" in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path

    from pathlib import Path
    from gateway.platforms.base import BasePlatformAdapter

    exported_path = Path(file_path)
    assert str(exported_path).startswith(
        str(tmp_path / "hermes home" / "plugins" / "hermes-tavern" / "exports")
    )
    assert exported_path.exists()
    exported = exported_path.read_text(encoding="utf-8")
    assert "# Atlas" in exported
    assert "## Summary" in exported
    assert "## Chapters" in exported
    assert "### Chapter 1: Arrival" in exported
    assert "#### Scene 1: Opening" in exported
    assert "user" in exported and "assistant" in exported
    assert "## Canon" in exported
    assert "## Timeline" in exported

    media_files, cleaned = BasePlatformAdapter.extract_media(response)
    assert media_files == [(file_path, False)]
    assert "MEDIA:" not in cleaned


def test_project_export_empty_project_still_exports_sections(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    project = runtime.store.create_project("Atlas", "A quiet beginning")
    response = runtime.handle_command_sync(
        RPCommand("project", ["export", str(project["id"])], f"/rp project export {project['id']}"),
        Event(),
    )

    assert "Project exported as Markdown." in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path

    exported = Path(file_path).read_text(encoding="utf-8")
    assert "No chapters yet." in exported
    assert "No canon entries." in exported
    assert "No timeline events." in exported


def test_project_export_with_active_project_and_no_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    runtime.handle_command_sync(
        RPCommand("project", ["create", "Atlas", "A long voyage"], "/rp project create Atlas A long voyage"),
        Event(),
    )
    runtime.store.create_chapter(1, "Arrival")
    scene = runtime.store.create_scene(1, "Opening")
    session = runtime.store.start_session("telegram:chat:chat-1:thread:main:user:user-1")
    runtime.store.link_scene_session(scene["id"], session["id"])
    runtime.store.append_message(session["id"], "user", "Hello.")
    runtime.store.append_message(session["id"], "assistant", "Welcome.")
    runtime.store.create_canon(1, "Climate", "Snow is common.")

    response = runtime.handle_command_sync(RPCommand("project", ["export"], "/rp project export"), Event())
    assert "Project exported as Markdown." in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path

    from pathlib import Path

    exported = Path(file_path).read_text(encoding="utf-8")
    assert "# Atlas" in exported
    assert "## Chapters" in exported


def test_scene_create_list_and_start_links_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello."}))
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    runtime.handle_command_sync(
        RPCommand("scene", ["create", str(chapter["id"]), "Opening"], "/rp scene create 1 Opening"),
        Event(),
    )

    scene = runtime.store.create_scene(chapter["id"], "Second")

    listed = runtime.handle_command_sync(
        RPCommand("scene", ["list", str(chapter["id"])], "/rp scene list 1"),
        Event(),
    )
    assert "Hermes Tavern scenes for chapter [1]" in listed
    assert "Opening" in listed
    assert "Second" in listed

    start = runtime.handle_command_sync(
        RPCommand("scene", ["start", str(scene["id"])], f"/rp scene start {scene['id']}"),
        Event(),
    )
    assert "Started Hermes Tavern session with Alice." in start
    linked_scene = runtime.store.get_scene(scene["id"])
    active = runtime.store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    assert linked_scene["session_id"] == active["id"]
    session_info = runtime.handle_command_sync(
        RPCommand("session", ["info"], "/rp session info"),
        Event(),
    )
    assert "Project: Atlas" in session_info
    assert "Chapter: Arrival" in session_info
    assert "Scene: Second" in session_info

    missing = runtime.handle_command_sync(
        RPCommand("scene", ["start"], "/rp scene start"),
        Event(),
    )
    assert missing == "Usage: /rp scene start <scene-id>"


def test_scene_list_shows_no_session_linked_flag_for_unlinked_scene(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    runtime.handle_command_sync(
        RPCommand("scene", ["create", str(chapter["id"]), "Opening"], "/rp scene create 1 Opening"),
        Event(),
    )

    listed = runtime.handle_command_sync(
        RPCommand("scene", ["list", str(chapter["id"])], "/rp scene list 1"),
        Event(),
    )
    assert "no session linked" in listed.lower()


def test_scene_goal_command_is_listed_in_help_output(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp scene goal <scene-id> [text]" in response
    assert "/rp scene goal clear <scene-id>" in response


def test_scene_goal_set_inspect_update_and_clear(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")

    set_goal = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["goal", str(scene["id"]), "Reach", "the", "gate", "before", "dawn"],
            "/rp scene goal 1 Reach the gate before dawn",
        ),
        Event(),
    )
    assert set_goal == "Scene goal set for scene [1]: Reach the gate before dawn"

    assert (
        runtime.store.get_scene_goal(scene["id"])["goal_text"]
        == "Reach the gate before dawn"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("scene", ["goal", str(scene["id"])], "/rp scene goal 1"),
            Event(),
        )
        == "Scene [1] goal: Reach the gate before dawn"
    )

    update_goal = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["goal", str(scene["id"]), "Find", "the", "hidden", "key"],
            "/rp scene goal 1 Find the hidden key",
        ),
        Event(),
    )
    assert "Scene goal set for scene [1]:" in update_goal
    assert (
        runtime.store.get_scene_goal(scene["id"])["goal_text"]
        == "Find the hidden key"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("scene", ["goal", str(scene["id"])], "/rp scene goal 1"),
            Event(),
        )
        == "Scene [1] goal: Find the hidden key"
    )

    clear_goal = runtime.handle_command_sync(
        RPCommand("scene", ["goal", "clear", str(scene["id"])], "/rp scene goal clear 1"),
        Event(),
    )
    assert clear_goal == "Scene goal cleared for scene [1]."
    assert (
        runtime.handle_command_sync(
            RPCommand("scene", ["goal", str(scene["id"])], "/rp scene goal 1"),
            Event(),
        )
        == "No scene goal set for scene [1]."
    )


@pytest.mark.parametrize(
    "command, expected_prefix",
    [
        (RPCommand("scene", ["goal"], "/rp scene goal"), "Usage: /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id>"),
        (RPCommand("scene", ["goal", "not-a-number"], "/rp scene goal not-a-number"), "Usage: /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id>"),
        (RPCommand("scene", ["goal", "clear", "not-a-number"], "/rp scene goal clear not-a-number"), "Usage: /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id>"),
        (RPCommand("scene", ["goal", "1", "   "], "/rp scene goal 1   "), "Usage: /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id>"),
    ],
)
def test_scene_goal_bad_arguments_return_usage(tmp_path, command, expected_prefix):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(command, Event())
    assert response.startswith(expected_prefix)


@pytest.mark.parametrize(
    "command, expected_message",
    [
        (RPCommand("scene", ["goal", "9999", "Reach"], "/rp scene goal 9999 Reach"), "No novel scene found: 9999"),
        (RPCommand("scene", ["goal", "9999"], "/rp scene goal 9999"), "No novel scene found: 9999"),
        (RPCommand("scene", ["goal", "clear", "9999"], "/rp scene goal clear 9999"), "No novel scene found: 9999"),
    ],
)
def test_scene_goal_missing_scene_returns_not_found(tmp_path, command, expected_message):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(command, Event())
    assert response == expected_message


def test_scene_start_nonexistent_returns_error(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    missing = runtime.handle_command_sync(
        RPCommand("scene", ["start", "9999"], "/rp scene start 9999"),
        Event(),
    )
    assert missing == "No novel scene found: 9999"


def test_scene_start_requires_available_card(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Only Scene")

    start = runtime.handle_command_sync(
        RPCommand("scene", ["start", str(scene["id"])], f"/rp scene start {scene['id']}"),
        Event(),
    )
    assert start == "No card has been imported yet. Import a card first: /rp card import <file>"
    assert runtime.store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1") is None
    assert runtime.store.get_scene(scene["id"]).get("session_id") is None


def test_canon_and_timeline_routes_use_active_project(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    runtime.store.create_canon(project["id"], "Lore", "Skyline is cold")

    runtime.handle_command_sync(
        RPCommand("project", ["set", str(project["id"])], f"/rp project set {project['id']}"),
        Event(),
    )

    added = runtime.handle_command_sync(
        RPCommand("canon", ["add", str(project["id"]), "Rule", "A hard rule exists."], "/rp canon add"),
        Event(),
    )
    assert "Hermes Tavern canon added" in added
    assert "(general)" in added

    grouped_add = runtime.handle_command_sync(
        RPCommand(
            "canon",
            ["add", str(project["id"]), "Culture", "Skyline citizens remember winter.", "--group", "world"],
            "/rp canon add 1 Culture Skyline citizens remember winter. --group world",
        ),
        Event(),
    )
    assert "Hermes Tavern canon added" in grouped_add
    assert "(world)" in grouped_add

    listed = runtime.handle_command_sync(RPCommand("canon", ["list"], "/rp canon list"), Event())
    assert "Hermes Tavern canon for project [1]:" in listed
    assert "Lore" in listed
    assert "Rule" in listed
    assert "Culture" in listed

    active_group = runtime.handle_command_sync(RPCommand("canon", ["list", "world"], "/rp canon list world"), Event())
    assert "Hermes Tavern canon for project [1]:" in active_group
    assert "Culture" in active_group
    assert "Rule" not in active_group

    grouped = runtime.handle_command_sync(
        RPCommand("canon", ["group", str(project["id"]), "general"], "/rp canon group 1 general"),
        Event(),
    )
    assert "Hermes Tavern canon group 'general'" in grouped
    assert "Rule" in grouped

    added_timeline = runtime.handle_command_sync(
        RPCommand("timeline", ["add", str(project["id"]), "1", "Start", "first"],
                   "/rp timeline add 1 1 Start first"),
        Event(),
    )
    assert "Hermes Tavern timeline event added" in added_timeline

    timeline = runtime.handle_command_sync(
        RPCommand("timeline", ["list"], "/rp timeline list"),
        Event(),
    )
    assert "Hermes Tavern timeline for project [1]" in timeline
    assert "Start" in timeline


def test_canon_modules_show_in_debug_prompt_for_project_linked_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    preset_id = store.save_preset(
        import_st_preset_json(
            {"name": "Writer", "prompts": [{"name": "style", "content": "Preset marker."}]}
        )
    )
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    store.set_session_preset(session["session_key"], preset_id)
    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    store.create_scene(chapter["id"], "Opening", session_id=session["id"])
    store.create_canon(project["id"], "Skyline", "The sky is violet.")

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/canon:Skyline" in prompt
    assert "The sky is violet." in prompt
    assert prompt.index("system/canon:Skyline") < prompt.index("system/preset:style")


def test_canon_modules_do_not_show_in_debug_prompt_for_unlinked_session(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    store.create_scene(chapter["id"], "Opening", session_id=store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["id"])

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/canon:Skyline" not in prompt
    assert "The sky is violet." not in prompt


def test_canon_modules_skip_prompt_injection_on_db_error(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    monkeypatch.setattr(
        runtime.store,
        "get_project_id_for_session",
        lambda _session_id: (_ for _ in ()).throw(sqlite3.OperationalError("DB unavailable")),
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/canon:" not in prompt


def test_scene_goal_module_shows_in_debug_prompt_for_linked_scene(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening", session_id=session["id"])
    store.set_scene_goal(scene["id"], "Reach the watchtower before sunrise.")
    runtime.handle_command_sync(
        RPCommand("note", ["set", "Keep the tone focused and concise."], "/rp note set Keep the tone focused and concise."),
        Event(),
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/scene_goal:Opening" in prompt
    assert "Scene goal: Reach the watchtower before sunrise." in prompt
    assert "system/note:author" in prompt
    assert prompt.index("system/scene_goal:Opening") < prompt.index("system/note:author")


def test_scene_goal_module_not_shown_for_unlinked_scene(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    other_scene = store.create_scene(chapter["id"], "Opening")
    store.set_scene_goal(other_scene["id"], "Reach the watchtower before sunrise.")

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/scene_goal" not in prompt
    assert "Scene goal: Reach the watchtower before sunrise." not in prompt


def test_scene_goal_module_skips_on_db_error(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    monkeypatch.setattr(
        runtime.store,
        "get_scene_goal_for_session",
        lambda _session_id: (_ for _ in ()).throw(sqlite3.OperationalError("DB unavailable")),
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "Hermes Tavern prompt debug" in prompt
    assert "system/scene_goal:" not in prompt


def test_novel_help_does_not_list_import_commands(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "project import" not in response
    assert "novel import" not in response
