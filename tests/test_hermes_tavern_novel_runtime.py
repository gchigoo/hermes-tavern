import pytest

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


def test_scene_create_list_and_start_links_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello."}))
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    runtime.store.create_scene(chapter["id"], "Opening",)

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
    store.create_canon(project["id"], "Skyline", "The sky is violet.")

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/canon:Skyline" not in prompt
    assert "The sky is violet." not in prompt
