import pytest
import sqlite3

from plugins.hermes_tavern.commands import TAVERN_COMMAND_TABLE
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.runtime import TavernRuntime
from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.presets import import_st_preset_json
from plugins.hermes_tavern.runtime_utils import mobile_preview as _mobile_preview
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.prompt import PromptModule
from hermes_tavern import runtime_prompt_modules


class Source:
    platform = "telegram"
    chat_id = "chat-1"
    thread_id = None
    user_id = "user-1"


class Event:
    source = Source()
    text = ""


PROJECT_BRIEF_USAGE = (
    "Usage: /rp project brief [project-id] | /rp project brief inspect [project-id] | "
    "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other> | "
    "/rp project brief type clear <project-id> | /rp project brief premise set <project-id> <text> | "
    "/rp project brief premise clear <project-id>"
)
PROJECT_OUTLINE_USAGE = (
    "Usage: /rp project outline [project-id] | /rp project outline inspect [project-id] | "
    "/rp project outline set [project-id] <text> | /rp project outline clear [project-id]"
)


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
    assert "/rp scene narration <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene narration clear <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene narration pov <scene-id> <label>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene narration tense <scene-id> <past|present>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp project style" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project style inspect [project-id]" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project style set [project-id] <text>" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project style clear [project-id]" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project brief [project-id]" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project brief inspect [project-id]" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project brief type clear <project-id>" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project brief premise set <project-id> <text>" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project brief premise clear <project-id>" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project outline [project-id]" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project outline inspect [project-id]" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project outline set [project-id] <text>" in TAVERN_COMMAND_TABLE["project"].help_lines
    assert "/rp project outline clear [project-id]" in TAVERN_COMMAND_TABLE["project"].help_lines


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


def test_project_style_routes_explicit_id_set_inspect_update_clear(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    set_first = runtime.handle_command_sync(
        RPCommand("project", ["style", "set", str(project["id"]), "voice:", "first-person"], "/rp project style set 1 voice first-person"),
        Event(),
    )
    assert set_first == f"Project style guide set for project [{project['id']}]: {_mobile_preview('voice: first-person', 180)}"
    assert runtime.store.get_project_style_guide(project["id"])["style_text"] == "voice: first-person"

    inspect = runtime.handle_command_sync(
        RPCommand("project", ["style", str(project["id"])], "/rp project style 1"),
        Event(),
    )
    assert inspect == f"Project style guide for project [{project['id']}]: {_mobile_preview('voice: first-person', 220)}"

    set_update = runtime.handle_command_sync(
        RPCommand("project", ["style", "set", str(project["id"]), "tone:", "warm"], "/rp project style set 1 tone warm"),
        Event(),
    )
    assert set_update == f"Project style guide set for project [{project['id']}]: {_mobile_preview('tone: warm', 180)}"
    assert runtime.store.get_project_style_guide(project["id"])["style_text"] == "tone: warm"

    cleared = runtime.handle_command_sync(
        RPCommand("project", ["style", "clear", str(project["id"])], "/rp project style clear 1"),
        Event(),
    )
    assert cleared == f"Project style guide cleared for project [{project['id']}]."
    assert runtime.store.get_project_style_guide(project["id"]) is None


def test_project_style_routes_active_project_fallback_forms(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    runtime.handle_command_sync(RPCommand("project", ["set", "1"], "/rp project set 1"), Event())

    set_fallback = runtime.handle_command_sync(
        RPCommand("project", ["style", "set", "voice:", "grounded"], "/rp project style set voice: grounded"),
        Event(),
    )
    assert set_fallback == f"Project style guide set for project [1]: {_mobile_preview('voice: grounded', 180)}"

    inspect_fallback = runtime.handle_command_sync(RPCommand("project", ["style"], "/rp project style"), Event())
    assert inspect_fallback == f"Project style guide for project [1]: {_mobile_preview('voice: grounded', 220)}"

    clear_fallback = runtime.handle_command_sync(RPCommand("project", ["style", "clear"], "/rp project style clear"), Event())
    assert clear_fallback == "Project style guide cleared for project [1]."


def test_project_style_active_project_fallback_without_active_project(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    fallback_message = "No active novel project. Use /rp project set <id> or pass project-id."

    assert (
        runtime.handle_command_sync(RPCommand("project", ["style"], "/rp project style"), Event())
        == fallback_message
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["style", "set", "voice:", "first-person"], "/rp project style set voice: first-person"),
            Event(),
        )
        == fallback_message
    )
    assert (
        runtime.handle_command_sync(RPCommand("project", ["style", "clear"], "/rp project style clear"), Event())
        == fallback_message
    )


def test_project_command_help_includes_brief_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp project brief [project-id]" in help_output
    assert "/rp project brief inspect [project-id]" in help_output
    assert "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>" in help_output
    assert "/rp project brief type clear <project-id>" in help_output
    assert "/rp project brief premise set <project-id> <text>" in help_output
    assert "/rp project brief premise clear <project-id>" in help_output


def test_project_command_help_includes_outline_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp project outline [project-id]" in help_output
    assert "/rp project outline inspect [project-id]" in help_output
    assert "/rp project outline set [project-id] <text>" in help_output
    assert "/rp project outline clear [project-id]" in help_output


def test_project_brief_routes_explicit_id_flow(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    set_type = runtime.handle_command_sync(
        RPCommand("project", ["brief", "type", "set", str(project["id"]), "novel"], "/rp project brief type set 1 novel"),
        Event(),
    )
    assert set_type == f"Project type set for project [{project['id']}]: novel"
    assert runtime.store.get_project_brief(project["id"])["project_type"] == "novel"

    set_premise_text = (
        "A courier arrives in a city with a hidden language under the pavement, then discovers a buried archive."
    )
    set_premise = runtime.handle_command_sync(
        RPCommand(
            "project",
            ["brief", "premise", "set", str(project["id"]), "A", "courier", "arrives", "in", "a", "city", "with", "a", "hidden", "language", "under", "the", "pavement,", "then", "discovers", "a", "buried", "archive."],
            "/rp project brief premise set 1 A courier arrives in a city with a hidden language under the pavement, then discovers a buried archive.",
        ),
        Event(),
    )
    assert set_premise == (
        f"Project premise set for project [{project['id']}]: "
        f"{_mobile_preview(set_premise_text, 180)}"
    )
    assert runtime.store.get_project_brief(project["id"])["premise_text"] == set_premise_text

    inspect = runtime.handle_command_sync(
        RPCommand("project", ["brief", str(project["id"])], "/rp project brief 1"),
        Event(),
    )
    assert inspect == (
        f"Project brief for project [{project['id']}]:\n"
        "Type: novel\n"
        f"Premise: {_mobile_preview(set_premise_text, 220)}"
    )

    update_type = runtime.handle_command_sync(
        RPCommand("project", ["brief", "type", "set", str(project["id"]), "rp"], "/rp project brief type set 1 rp"),
        Event(),
    )
    assert update_type == f"Project type set for project [{project['id']}]: rp"

    clear_type = runtime.handle_command_sync(
        RPCommand("project", ["brief", "type", "clear", str(project["id"])], "/rp project brief type clear 1"),
        Event(),
    )
    assert clear_type == f"Project type cleared for project [{project['id']}]."

    clear_premise = runtime.handle_command_sync(
        RPCommand("project", ["brief", "premise", "clear", str(project["id"])], "/rp project brief premise clear 1"),
        Event(),
    )
    assert clear_premise == f"Project premise cleared for project [{project['id']}]."

    inspect_no_content = runtime.handle_command_sync(
        RPCommand("project", ["brief", str(project["id"])], "/rp project brief 1"),
        Event(),
    )
    assert inspect_no_content == f"No project brief set for project [{project['id']}]."


def test_project_brief_active_inspect_fallback(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    runtime.handle_command_sync(RPCommand("project", ["set", str(project["id"])], "/rp project set 1"), Event())

    runtime.handle_command_sync(
        RPCommand(
            "project",
            ["brief", "type", "set", str(project["id"]), "worldbuilding"],
            "/rp project brief type set 1 worldbuilding",
        ),
        Event(),
    )
    runtime.handle_command_sync(
        RPCommand(
            "project",
            ["brief", "premise", "set", str(project["id"]), "A city built from memory."],
            "/rp project brief premise set 1 A city built from memory.",
        ),
        Event(),
    )

    brief = runtime.handle_command_sync(RPCommand("project", ["brief"], "/rp project brief"), Event())
    inspect_text = (
        f"Project brief for project [{project['id']}]:\n"
        "Type: worldbuilding\n"
        f"Premise: {_mobile_preview('A city built from memory.', 220)}"
    )
    assert brief == inspect_text

    inspect_with_keyword = runtime.handle_command_sync(
        RPCommand("project", ["brief", "inspect"], "/rp project brief inspect"),
        Event(),
    )
    assert inspect_with_keyword == inspect_text


def test_project_brief_active_inspect_without_active_project_returns_guidance(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    fallback_message = "No active novel project. Use /rp project set <id> or pass project-id."

    assert runtime.handle_command_sync(RPCommand("project", ["brief"], "/rp project brief"), Event()) == fallback_message
    assert (
        runtime.handle_command_sync(RPCommand("project", ["brief", "inspect"], "/rp project brief inspect"), Event())
        == fallback_message
    )


def test_project_brief_mutating_commands_require_explicit_id(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    runtime.handle_command_sync(RPCommand("project", ["set", str(project["id"])], "/rp project set 1"), Event())

    assert (
        runtime.handle_command_sync(RPCommand("project", ["brief", "type", "set", "novel"], "/rp project brief type set novel"), Event())
        == PROJECT_BRIEF_USAGE
    )
    assert (
        runtime.handle_command_sync(RPCommand("project", ["brief", "premise", "set", "A", "story", "starts", "here"], "/rp project brief premise set A story starts here"), Event())
        == PROJECT_BRIEF_USAGE
    )
    assert (
        runtime.handle_command_sync(RPCommand("project", ["brief", "type", "clear"], "/rp project brief type clear"), Event())
        == PROJECT_BRIEF_USAGE
    )
    assert (
        runtime.handle_command_sync(RPCommand("project", ["brief", "premise", "clear"], "/rp project brief premise clear"), Event())
        == PROJECT_BRIEF_USAGE
    )


def test_project_brief_boundary_args_return_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    invalids = [
        RPCommand("project", ["brief", "inspect", "1", "extra"], "/rp project brief inspect 1 extra"),
        RPCommand("project", ["brief", "type", "set", str(1)], "/rp project brief type set 1"),
        RPCommand("project", ["brief", "type", "set", str(1), "novel", "extra"], "/rp project brief type set 1 novel extra"),
        RPCommand("project", ["brief", "premise", "set", str(1)], "/rp project brief premise set 1"),
        RPCommand("project", ["brief", "premise", "set", str(1), ""], "/rp project brief premise set 1"),
    ]
    for command in invalids:
        assert runtime.handle_command_sync(command, Event()) == PROJECT_BRIEF_USAGE


def test_project_brief_missing_or_non_numeric_id_cases(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    command_ids = [
        RPCommand("project", ["brief", "inspect", "not-a-number"], "/rp project brief inspect not-a-number"),
        RPCommand("project", ["brief", "type", "set", "not-a-number", "novel"], "/rp project brief type set not-a-number novel"),
        RPCommand("project", ["brief", "type", "clear", "not-a-number"], "/rp project brief type clear not-a-number"),
        RPCommand("project", ["brief", "premise", "set", "not-a-number", "text"], "/rp project brief premise set not-a-number text"),
        RPCommand("project", ["brief", "premise", "clear", "not-a-number"], "/rp project brief premise clear not-a-number"),
    ]
    for command in command_ids:
        assert runtime.handle_command_sync(command, Event()) == PROJECT_BRIEF_USAGE


@pytest.mark.parametrize(
    "command, expected",
    [
        (RPCommand("project", ["brief", str(9999)], "/rp project brief 9999"), "No novel project found: 9999"),
        (RPCommand("project", ["brief", "inspect", str(9999)], "/rp project brief inspect 9999"), "No novel project found: 9999"),
        (RPCommand("project", ["brief", "type", "set", str(9999), "rp"], "/rp project brief type set 9999 rp"), "No novel project found: 9999"),
        (RPCommand("project", ["brief", "type", "clear", str(9999)], "/rp project brief type clear 9999"), "No novel project found: 9999"),
        (RPCommand("project", ["brief", "premise", "set", str(9999), "A", "line"], "/rp project brief premise set 9999 A line"), "No novel project found: 9999"),
        (RPCommand("project", ["brief", "premise", "clear", str(9999)], "/rp project brief premise clear 9999"), "No novel project found: 9999"),
    ],
)
def test_project_brief_missing_project_returns_not_found(tmp_path, command, expected):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    assert runtime.handle_command_sync(command, Event()) == expected


def test_project_brief_invalid_type_message(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    response = runtime.handle_command_sync(
        RPCommand("project", ["brief", "type", "set", str(project["id"]), "bad-value"], "/rp project brief type set 1 bad-value"),
        Event(),
    )
    assert response == "Invalid project type. Use novel, serial, rp, worldbuilding, or other."


def test_project_brief_and_info_includes_fields_only_when_present(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    outline_text = "An old city where maps forget."

    info_without_brief = runtime.handle_command_sync(
        RPCommand("project", ["info", str(project["id"])], "/rp project info 1"),
        Event(),
    )
    assert "project_type:" not in info_without_brief
    assert "premise:" not in info_without_brief
    assert "outline:" not in info_without_brief

    runtime.handle_command_sync(RPCommand("project", ["brief", "type", "set", str(project["id"]), "other"], "/rp project brief type set 1 other"), Event())
    runtime.handle_command_sync(
        RPCommand("project", ["brief", "premise", "set", str(project["id"]), "A city hears every whisper."], "/rp project brief premise set 1 A city hears every whisper."),
        Event(),
    )

    info_with_brief = runtime.handle_command_sync(
        RPCommand("project", ["info", str(project["id"])], "/rp project info 1"),
        Event(),
    )
    assert "project_type: other" in info_with_brief
    assert f"premise: {_mobile_preview('A city hears every whisper.', 220)}" in info_with_brief

    runtime.store.set_project_outline(project["id"], outline_text)
    info_with_outline = runtime.handle_command_sync(
        RPCommand("project", ["info", str(project["id"])], "/rp project info 1"),
        Event(),
    )
    assert f"outline: {_mobile_preview(outline_text, 220)}" in info_with_outline

    runtime.store.clear_project_outline(project["id"])
    info_without_outline = runtime.handle_command_sync(
        RPCommand("project", ["info", str(project["id"])], "/rp project info 1"),
        Event(),
    )
    assert "outline:" not in info_without_outline


def test_project_brief_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello."}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening")
    store.link_scene_session(
        scene["id"],
        store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["id"],
    )

    store.set_project_brief_type(project["id"], "rp")
    store.set_project_premise(project["id"], "marker: distinctive premise token")
    store.set_project_outline(project["id"], "marker: distinct outline token")

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    for output in (prompt, context):
        lowered = output.lower()
        assert "project_brief" not in lowered
        assert "project_type" not in lowered
        assert "marker: distinctive premise token" not in lowered
        assert "project_outline" not in lowered
        assert "outline_text" not in lowered
        assert "marker: distinct outline token" not in lowered


def test_project_style_bad_arguments_return_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.handle_command_sync(RPCommand("project", ["set", "1"], "/rp project set 1"), Event())
    usage = (
        "Usage: /rp project style [project-id] | /rp project style inspect [project-id] | "
        "/rp project style set [project-id] <text> | /rp project style clear [project-id]"
    )

    command_ids = [
        RPCommand("project", ["style", "bad-id"], "/rp project style bad-id"),
        RPCommand("project", ["style", "1", "extra"], "/rp project style 1 extra"),
        RPCommand("project", ["style", "inspect", "1", "extra"], "/rp project style inspect 1 extra"),
        RPCommand("project", ["style", "clear", "1", "extra"], "/rp project style clear 1 extra"),
        RPCommand("project", ["style", "set"], "/rp project style set"),
        RPCommand("project", ["style", "set", "1"], "/rp project style set 1"),
        RPCommand("project", ["style", "set", ""], "/rp project style set"),
    ]
    for command in command_ids:
        assert runtime.handle_command_sync(command, Event()) == usage


def test_project_style_missing_project_returns_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    tests = [
        (RPCommand("project", ["style", "9999"], "/rp project style 9999"), "No novel project found: 9999"),
        (RPCommand("project", ["style", "inspect", "9999"], "/rp project style inspect 9999"), "No novel project found: 9999"),
        (RPCommand("project", ["style", "set", "9999", "tone:", "warm"], "/rp project style set 9999 tone: warm"), "No novel project found: 9999"),
        (RPCommand("project", ["style", "clear", "9999"], "/rp project style clear 9999"), "No novel project found: 9999"),
    ]

    for command, expected in tests:
        assert runtime.handle_command_sync(command, Event()) == expected


def test_project_style_set_stores_full_text_and_returns_mobile_preview(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    long_text = (
        "Write cinematic prose with layered emotional transitions and vivid sensory "
        "detail, while staying grounded in character voice and careful pacing. " * 6
    ).strip()

    response = runtime.handle_command_sync(
        RPCommand("project", ["style", "set", "1", long_text], f"/rp project style set 1 {long_text}"),
        Event(),
    )

    assert response == f"Project style guide set for project [1]: {_mobile_preview(long_text, 180)}"
    assert long_text not in response
    assert runtime.store.get_project_style_guide(1)["style_text"] == long_text


def test_project_outline_routes_explicit_id_set_inspect_update_clear(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    set_first = runtime.handle_command_sync(
        RPCommand("project", ["outline", "set", str(project["id"]), "Act", "one"], "/rp project outline set 1 Act one"),
        Event(),
    )
    assert set_first == f"Project outline set for project [{project['id']}]: {_mobile_preview('Act one', 180)}"
    assert runtime.store.get_project_outline(project["id"])["outline_text"] == "Act one"

    inspect = runtime.handle_command_sync(
        RPCommand("project", ["outline", str(project["id"])], "/rp project outline 1"),
        Event(),
    )
    assert inspect == f"Project outline for project [{project['id']}]: {_mobile_preview('Act one', 220)}"

    inspect_explicit = runtime.handle_command_sync(
        RPCommand("project", ["outline", "inspect", str(project["id"])], "/rp project outline inspect 1"),
        Event(),
    )
    assert inspect_explicit == f"Project outline for project [{project['id']}]: {_mobile_preview('Act one', 220)}"

    set_update = runtime.handle_command_sync(
        RPCommand("project", ["outline", "set", str(project["id"]), "Act", "two"], "/rp project outline set 1 Act two"),
        Event(),
    )
    assert set_update == f"Project outline set for project [{project['id']}]: {_mobile_preview('Act two', 180)}"
    assert runtime.store.get_project_outline(project["id"])["outline_text"] == "Act two"

    cleared = runtime.handle_command_sync(
        RPCommand("project", ["outline", "clear", str(project["id"])], "/rp project outline clear 1"),
        Event(),
    )
    assert cleared == f"Project outline cleared for project [{project['id']}]."
    assert runtime.store.get_project_outline(project["id"]) is None


def test_project_outline_routes_active_project_fallback_forms(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    runtime.handle_command_sync(RPCommand("project", ["set", "1"], "/rp project set 1"), Event())

    set_fallback = runtime.handle_command_sync(
        RPCommand("project", ["outline", "set", "Act", "one"], "/rp project outline set Act one"),
        Event(),
    )
    assert set_fallback == f"Project outline set for project [1]: {_mobile_preview('Act one', 180)}"

    inspect_fallback = runtime.handle_command_sync(
        RPCommand("project", ["outline"], "/rp project outline"),
        Event(),
    )
    assert inspect_fallback == f"Project outline for project [1]: {_mobile_preview('Act one', 220)}"

    inspect_subcommand_fallback = runtime.handle_command_sync(
        RPCommand("project", ["outline", "inspect"], "/rp project outline inspect"),
        Event(),
    )
    assert inspect_subcommand_fallback == f"Project outline for project [1]: {_mobile_preview('Act one', 220)}"

    clear_fallback = runtime.handle_command_sync(
        RPCommand("project", ["outline", "clear"], "/rp project outline clear"),
        Event(),
    )
    assert clear_fallback == "Project outline cleared for project [1]."


def test_project_outline_active_project_fallback_without_active_project(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    fallback_message = "No active novel project. Use /rp project set <id> or pass project-id."

    assert runtime.handle_command_sync(RPCommand("project", ["outline"], "/rp project outline"), Event()) == fallback_message
    assert runtime.handle_command_sync(RPCommand("project", ["outline", "inspect"], "/rp project outline inspect"), Event()) == fallback_message
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["outline", "set", "Act", "one"], "/rp project outline set Act one"),
            Event(),
        )
        == fallback_message
    )
    assert runtime.handle_command_sync(RPCommand("project", ["outline", "clear"], "/rp project outline clear"), Event()) == fallback_message


def test_project_outline_bad_arguments_return_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.handle_command_sync(RPCommand("project", ["set", "1"], "/rp project set 1"), Event())

    command_ids = [
        RPCommand("project", ["outline", "bad-id"], "/rp project outline bad-id"),
        RPCommand("project", ["outline", "inspect", "1", "extra"], "/rp project outline inspect 1 extra"),
        RPCommand("project", ["outline", "clear", "1", "extra"], "/rp project outline clear 1 extra"),
        RPCommand("project", ["outline", "set"], "/rp project outline set"),
        RPCommand("project", ["outline", "set", "1"], "/rp project outline set 1"),
        RPCommand("project", ["outline", "set", ""], "/rp project outline set"),
    ]
    for command in command_ids:
        assert runtime.handle_command_sync(command, Event()) == PROJECT_OUTLINE_USAGE


def test_project_outline_missing_project_returns_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    tests = [
        (RPCommand("project", ["outline", "9999"], "/rp project outline 9999"), "No novel project found: 9999"),
        (
            RPCommand("project", ["outline", "inspect", "9999"], "/rp project outline inspect 9999"),
            "No novel project found: 9999",
        ),
        (
            RPCommand("project", ["outline", "set", "9999", "Act", "one"], "/rp project outline set 9999 Act one"),
            "No novel project found: 9999",
        ),
        (
            RPCommand("project", ["outline", "clear", "9999"], "/rp project outline clear 9999"),
            "No novel project found: 9999",
        ),
    ]
    for command, expected in tests:
        assert runtime.handle_command_sync(command, Event()) == expected


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
    runtime.store.set_scene_goal(scene["id"], "Secure the harbor")
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
    assert "Goal: Secure the harbor" in exported
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
    assert "/rp scene narration <scene-id>" in response
    assert "/rp scene narration clear <scene-id>" in response
    assert "/rp scene narration pov <scene-id> <label>" in response
    assert "/rp scene narration tense <scene-id> <past|present>" in response


def test_scene_narration_set_inspect_update_clear_preserves_other_fields(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")

    set_pov = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["narration", "pov", str(scene["id"]), "third-person", "limited:", "Mara"],
            "/rp scene narration pov 1 third-person limited: Mara",
        ),
        Event(),
    )
    assert set_pov == "Scene narration POV set for scene [1]: third-person limited: Mara"
    inspect_pov_only = runtime.handle_command_sync(
        RPCommand("scene", ["narration", str(scene["id"])], "/rp scene narration 1"),
        Event(),
    )
    assert inspect_pov_only == (
        "Scene narration controls for scene [1]:\n"
        "POV: third-person limited: Mara\n"
        "Tense: (not set)"
    )

    set_tense = runtime.handle_command_sync(
        RPCommand("scene", ["narration", "tense", str(scene["id"]), "Past"], "/rp scene narration tense 1 Past"),
        Event(),
    )
    assert set_tense == "Scene narration tense set for scene [1]: past"

    inspect_full = runtime.handle_command_sync(
        RPCommand("scene", ["narration", str(scene["id"])], "/rp scene narration 1"),
        Event(),
    )
    assert inspect_full == (
        "Scene narration controls for scene [1]:\n"
        "POV: third-person limited: Mara\n"
        "Tense: past"
    )

    update_pov = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["narration", "pov", str(scene["id"]), "second-person", "omniscient"],
            "/rp scene narration pov 1 second-person omniscient",
        ),
        Event(),
    )
    assert update_pov == "Scene narration POV set for scene [1]: second-person omniscient"
    inspect_after_update = runtime.handle_command_sync(
        RPCommand("scene", ["narration", str(scene["id"])], "/rp scene narration 1"),
        Event(),
    )
    assert inspect_after_update == (
        "Scene narration controls for scene [1]:\n"
        "POV: second-person omniscient\n"
        "Tense: past"
    )

    clear = runtime.handle_command_sync(
        RPCommand("scene", ["narration", "clear", str(scene["id"])], "/rp scene narration clear 1"),
        Event(),
    )
    assert clear == "Scene narration controls cleared for scene [1]."
    assert (
        runtime.handle_command_sync(
            RPCommand("scene", ["narration", str(scene["id"])], "/rp scene narration 1"),
            Event(),
        )
        == "No scene narration controls set for scene [1]."
    )


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


@pytest.mark.parametrize(
    "command",
    [
        RPCommand("scene", ["narration"], "/rp scene narration"),
        RPCommand("scene", ["narration", "clear"], "/rp scene narration clear"),
        RPCommand("scene", ["narration", "clear", "1", "extra"], "/rp scene narration clear 1 extra"),
        RPCommand("scene", ["narration", "pov"], "/rp scene narration pov"),
        RPCommand("scene", ["narration", "pov", "1"], "/rp scene narration pov 1"),
        RPCommand("scene", ["narration", "pov", "1", "   "], "/rp scene narration pov 1   "),
        RPCommand("scene", ["narration", "tense"], "/rp scene narration tense"),
        RPCommand("scene", ["narration", "tense", "1"], "/rp scene narration tense 1"),
        RPCommand("scene", ["narration", "tense", "1", "past", "too", "many"], "/rp scene narration tense 1 past too many"),
        RPCommand("scene", ["narration", "1", "extra"], "/rp scene narration 1 extra"),
    ],
)
def test_scene_narration_malformed_arguments_return_usage(tmp_path, command):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(command, Event())
    assert response.startswith(
        "Usage: /rp scene narration <scene-id> | /rp scene narration clear <scene-id> | "
        "/rp scene narration pov <scene-id> <label> | /rp scene narration tense <scene-id> <past|present>"
    )


@pytest.mark.parametrize(
    "command, expected_message",
    [
        (RPCommand("scene", ["narration", "9999"], "/rp scene narration 9999"), "No novel scene found: 9999"),
        (RPCommand("scene", ["narration", "clear", "9999"], "/rp scene narration clear 9999"), "No novel scene found: 9999"),
        (RPCommand("scene", ["narration", "pov", "9999", "third-person", "limited:"], "/rp scene narration pov 9999 third-person limited:"), "No novel scene found: 9999"),
        (RPCommand("scene", ["narration", "tense", "9999", "past"], "/rp scene narration tense 9999 past"), "No novel scene found: 9999"),
    ],
)
def test_scene_narration_missing_scene_returns_not_found(tmp_path, command, expected_message):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(command, Event())
    assert response == expected_message


def test_scene_narration_invalid_tense_is_reported(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")

    response = runtime.handle_command_sync(
        RPCommand("scene", ["narration", "tense", str(scene["id"]), "future"], "/rp scene narration tense 1 future"),
        Event(),
    )
    assert response == "Invalid tense. Use past or present."


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


def test_scene_narration_module_shows_in_debug_prompt_for_linked_scene(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening", session_id=session["id"])
    store.set_scene_narration_controls(
        scene["id"],
        pov_label="third-person limited: Mara",
        tense="present",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/scene_narration:Opening" in prompt
    assert "Scene narration controls:" in prompt
    assert "POV: third-person limited: Mara" in prompt
    assert "Tense: present" in prompt


def test_scene_narration_module_not_shown_for_unlinked_scene(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening")
    store.set_scene_narration_controls(
        scene["id"],
        pov_label="first-person",
        tense="past",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/scene_narration:" not in prompt


def test_scene_narration_module_skips_blank_controls_row(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening", session_id=session["id"])

    with store.connect() as conn:
        conn.execute(
            """
            INSERT INTO novel_scene_narration_controls (
                scene_id, pov_label, tense, created_at, updated_at
            ) VALUES (?, '', '', '2025-01-01 00:00:00', '2025-01-01 00:00:00')
            """,
            (scene["id"],),
        )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "system/scene_narration:Opening" not in prompt


def test_scene_narration_module_orders_before_scene_goal_and_note(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening", session_id=session["id"])
    store.set_scene_narration_controls(
        scene["id"],
        pov_label="first-person",
        tense="present",
    )
    store.set_scene_goal(scene["id"], "Reach the watchtower before sunrise.")
    runtime.handle_command_sync(
        RPCommand("note", ["set", "Keep the tone focused and concise."], "/rp note set Keep the tone focused and concise."),
        Event(),
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert prompt.index("system/scene_narration:Opening") < prompt.index("system/scene_goal:Opening")
    assert prompt.index("system/scene_narration:Opening") < prompt.index("system/note:author")


def test_scene_narration_module_skips_on_db_error(tmp_path, monkeypatch):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar"}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    session = store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")
    project = store.create_project("Skyline")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening", session_id=session["id"])
    store.set_scene_narration_controls(scene["id"], pov_label="first-person")
    store.set_scene_goal(scene["id"], "Reach the watchtower before sunrise.")

    monkeypatch.setattr(
        runtime.store,
        "get_scene_narration_controls_for_session",
        lambda _session_id: (_ for _ in ()).throw(sqlite3.OperationalError("DB unavailable")),
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())

    assert "Hermes Tavern prompt debug" in prompt
    assert "system/scene_narration:Opening" not in prompt


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


def test_project_style_module_shows_in_debug_prompt_for_linked_scene(tmp_path, monkeypatch):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    card = runtime.store.save_card(
        parse_character_card(
            {
                "name": "Alice",
                "description": "Scholar",
                "first_mes": "Hello.",
            }
        )
    )
    session = runtime.store.start_session(session_key_from_event(Event()), card_id=card)

    project = runtime.store.create_project("Skyline")
    chapter = runtime.store.create_chapter(project["id"], "Opening")
    scene = runtime.store.create_scene(chapter["id"], "Dawn")
    runtime.store.link_scene_session(scene["id"], session["id"])

    runtime.store.set_project_style_guide(project["id"], "Use close third-person prose.")
    runtime.store.create_canon(project["id"], "World", "Rain taps windowpanes.")

    monkeypatch.setattr(
        runtime_prompt_modules,
        "session_preset_modules",
        lambda _runtime, _session: [
            PromptModule(
                name="preset:Tone",
                role="system",
                content="Preset: keep suspense.",
                position="before_char",
                insertion_order=10,
                enabled=True,
            )
        ],
    )

    modules = runtime._session_prompt_modules(session, "", [])
    style_module = next(m for m in modules if m.name == "project_style:Skyline")
    assert style_module.role == "system"
    assert style_module.content == "Project style guide:\nUse close third-person prose."
    assert style_module.position == "before_char"
    assert style_module.insertion_order == -30
    assert style_module.enabled is True

    names = [m.name for m in modules]
    assert names.index("project_style:Skyline") < names.index("canon:World")

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    assert "Hermes Tavern prompt debug" in prompt
    assert "system/project_style:Skyline" in prompt
    assert "Project style guide:" in prompt
    assert "Use close third-person prose." in prompt
    assert (
        prompt.find("system/project_style:Skyline")
        < prompt.find("system/canon:World")
        < prompt.find("system/preset:Tone")
    )


def test_project_style_module_not_shown_for_unlinked_session(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    card = runtime.store.save_card(
        parse_character_card(
            {
                "name": "Alice",
                "description": "Scholar",
                "first_mes": "Hello.",
            }
        )
    )
    session = runtime.store.start_session(session_key_from_event(Event()), card_id=card)

    project = runtime.store.create_project("Skyline")
    runtime.store.set_project_style_guide(project["id"], "Use close third-person prose.")
    runtime.store.create_canon(project["id"], "World", "Rain taps windowpanes.")

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    assert "Hermes Tavern prompt debug" in prompt
    assert "system/project_style:Skyline" not in prompt
    assert "Project style guide:" not in prompt
    assert "Use close third-person prose." not in prompt


def test_project_style_module_skips_missing_or_blank_style_text(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    card = runtime.store.save_card(
        parse_character_card(
            {
                "name": "Alice",
                "description": "Scholar",
                "first_mes": "Hello.",
            }
        )
    )
    session = runtime.store.start_session("scope-blank", card_id=card)

    project = runtime.store.create_project("Skyline")
    chapter = runtime.store.create_chapter(project["id"], "Opening")
    scene = runtime.store.create_scene(chapter["id"], "Dawn")
    runtime.store.link_scene_session(scene["id"], session["id"])

    assert not any(
        m.name == "project_style:Skyline" for m in runtime._session_prompt_modules(session, "", [])
    )

    runtime.store.set_project_style_guide(project["id"], "   ")
    assert not any(
        m.name == "project_style:Skyline" for m in runtime._session_prompt_modules(session, "", [])
    )


def test_project_style_module_skips_only_style_on_db_error(tmp_path, monkeypatch):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    card = runtime.store.save_card(
        parse_character_card(
            {
                "name": "Alice",
                "description": "Scholar",
                "first_mes": "Hello.",
            }
        )
    )
    session = runtime.store.start_session(session_key_from_event(Event()), card_id=card)

    project = runtime.store.create_project("Skyline")
    chapter = runtime.store.create_chapter(project["id"], "Opening")
    scene = runtime.store.create_scene(chapter["id"], "Dawn")
    runtime.store.link_scene_session(scene["id"], session["id"])
    runtime.store.set_project_style_guide(project["id"], "Use close third-person prose.")
    runtime.store.create_canon(project["id"], "World", "Rain taps windowpanes.")

    def _raise_db_error(_session_id: str) -> None:
        raise sqlite3.OperationalError("simulated db fault")

    monkeypatch.setattr(runtime.store, "get_project_style_guide_for_session", _raise_db_error)

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    assert "Hermes Tavern prompt debug" in prompt
    assert "system/project_style:" not in prompt
    assert "system/canon:World" in prompt
