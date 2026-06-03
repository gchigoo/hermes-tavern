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


def test_scene_create_list_and_start_is_deferred(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
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
    assert "Scene start is deferred to phase 121 S4" in start

    missing = runtime.handle_command_sync(
        RPCommand("scene", ["start"], "/rp scene start"),
        Event(),
    )
    assert missing == "Usage: /rp scene start <scene-id>"


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
