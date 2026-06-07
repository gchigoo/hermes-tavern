import json
from dataclasses import replace
from types import SimpleNamespace
import pytest
import sqlite3

from plugins.hermes_tavern.commands import TAVERN_COMMAND_TABLE
from plugins.hermes_tavern.db import TavernStore
from plugins.hermes_tavern.runtime import TavernRuntime
from plugins.hermes_tavern.commands import RPCommand
from plugins.hermes_tavern.importers.cards import parse_character_card
from plugins.hermes_tavern.importers.lorebooks import import_st_lorebook_json
from plugins.hermes_tavern.importers.presets import import_st_preset_json
from plugins.hermes_tavern.importers.personas import import_raw_persona_text
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
PROJECT_REVISION_USAGE = (
    "Usage: /rp project revision add <project-id> <label> <note...> | "
    "/rp project revision list [project-id] | /rp project revision inspect <note-id> | "
    "/rp project revision update <note-id> <note...> | /rp project revision delete <note-id>"
)
RELATIONSHIP_USAGE = (
    "Usage: /rp relationship add <project-id> <label> <state...> | "
    "/rp relationship list [project-id] | /rp relationship inspect <relationship-id> | "
    "/rp relationship rename <relationship-id> <label> | "
    "/rp relationship update <relationship-id> <state...> | "
    "/rp relationship delete <relationship-id> | /rp relationship export <relationship-id>"
)
CHARACTER_STATE_USAGE = (
    "Usage: /rp character state add <project-id> <label> <state...> | "
    "/rp character state list [project-id] | /rp character state inspect <character-state-id> | "
    "/rp character state update <character-state-id> <state...> | "
    "/rp character state delete <character-state-id> | /rp character state export <character-state-id>"
)
LOCATION_USAGE = (
    "Usage: /rp location add <project-id> <label> <description...> | "
    "/rp location list [project-id] | /rp location inspect <location-id> | "
    "/rp location update <location-id> <description...> | "
    "/rp location delete <location-id> | "
    "/rp location export <location-id>"
)
ORGANIZATION_USAGE = (
    "Usage: /rp organization add <project-id> <label> <description...> | "
    "/rp organization list [project-id] | /rp organization inspect <organization-id> | "
    "/rp organization update <organization-id> <description...> | "
    "/rp organization delete <organization-id>"
)
PLOT_THREAD_USAGE = (
    "Usage: /rp plot thread add <project-id> <label> <description...> | "
    "/rp plot thread list [project-id] | /rp plot thread inspect <plot-thread-id> | "
    "/rp plot thread update <plot-thread-id> <description...> | "
    "/rp plot thread delete <plot-thread-id>"
)
STYLE_SAMPLE_USAGE = (
    "Usage: /rp style sample add <project-id> <label> <sample...> | "
    "/rp style sample list [project-id] | /rp style sample inspect <style-sample-id> | "
    "/rp style sample update <style-sample-id> <sample...> | "
    "/rp style sample delete <style-sample-id>"
)

BINDING_USAGE = (
    "Usage: /rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id> | "
    "/rp binding list <project|chapter|scene> <scope-id> | "
    "/rp binding inspect <binding-id> | /rp binding clear <binding-id>. "
    "Default bindings are metadata-only/inert and are not auto-applied."
)


def _card_with_id(store: TavernStore, card_id: str) -> str:
    card = replace(
        parse_character_card(
            {"name": "Mara Lark", "description": "A watchful archivist", "first_mes": "Let's begin."}
        ),
        id=card_id,
    )
    return store.save_card(card)


def _preset_with_id(store: TavernStore, preset_id: str) -> str:
    imported = import_st_preset_json(
        {
            "name": "Harbor Setting",
            "prompts": [{"name": "style", "content": "Tone: measured."}],
        },
    )
    preset = SimpleNamespace(
        id=preset_id,
        name=imported.name,
        source=imported.source,
        raw=imported.raw,
        modules=imported.modules,
    )
    return store.save_preset(preset)


def _lorebook_with_id(store: TavernStore, lorebook_id: str) -> str:
    imported = import_st_lorebook_json(
        {"name": "Harbor Maps", "entries": [{"content": "A bell at fog edge."}]}
    )
    lorebook = SimpleNamespace(
        id=lorebook_id,
        name=imported.name,
        source=imported.source,
        raw=imported.raw,
        entries=imported.entries,
    )
    return store.save_lorebook(lorebook)


def _persona_with_id(store: TavernStore, persona_id: str) -> str:
    imported = import_raw_persona_text(
        "I offer quiet counsel and sharp details.",
        name="Harbor Persona",
        source_path="mock-persona.txt",
    )
    persona = SimpleNamespace(
        id=persona_id,
        name=imported.name,
        content=imported.content,
        raw_json=imported.raw_json,
        source_path=imported.source_path,
    )
    return store.save_persona(persona)


def test_novel_command_table_has_expected_families():
    assert "character" in TAVERN_COMMAND_TABLE
    assert "relationship" in TAVERN_COMMAND_TABLE
    assert "project" in TAVERN_COMMAND_TABLE
    assert "chapter" in TAVERN_COMMAND_TABLE
    assert "scene" in TAVERN_COMMAND_TABLE
    assert "canon" in TAVERN_COMMAND_TABLE
    assert "timeline" in TAVERN_COMMAND_TABLE
    assert "location" in TAVERN_COMMAND_TABLE
    assert "organization" in TAVERN_COMMAND_TABLE
    assert "plot" in TAVERN_COMMAND_TABLE
    assert "style" in TAVERN_COMMAND_TABLE
    assert "binding" in TAVERN_COMMAND_TABLE

    for name in (
        "character",
        "relationship",
        "project",
        "chapter",
        "scene",
        "canon",
        "timeline",
        "location",
        "organization",
        "plot",
        "style",
        "binding",
    ):
        entry = TAVERN_COMMAND_TABLE[name]
        if name == "character":
            assert entry.handler == "_character_command"
            continue
        if name == "style":
            assert entry.handler == "_style_command"
            continue
        assert entry.handler == f"_{name}_command"
    assert TAVERN_COMMAND_TABLE["binding"].handler == "_binding_command"
    assert "/rp scene goal <scene-id> [text]" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene goal clear <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene narration <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene narration clear <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene narration pov <scene-id> <label>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene narration tense <scene-id> <past|present>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene beat add <scene-id> <label> <beat...>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene beat list <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene beat inspect <beat-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene beat update <beat-id> <beat...>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene beat delete <beat-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
    assert "/rp scene inspect <scene-id>" in TAVERN_COMMAND_TABLE["scene"].help_lines
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
    assert "/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>" in TAVERN_COMMAND_TABLE["binding"].help_lines
    assert "/rp binding list <project|chapter|scene> <scope-id>" in TAVERN_COMMAND_TABLE["binding"].help_lines
    assert "/rp binding inspect <binding-id>" in TAVERN_COMMAND_TABLE["binding"].help_lines
    assert "/rp binding clear <binding-id>" in TAVERN_COMMAND_TABLE["binding"].help_lines
    assert "/rp binding rows are metadata-only/inert; not auto-applied" in TAVERN_COMMAND_TABLE["binding"].help_lines
    assert "/rp relationship add <project-id> <label> <state...>" in TAVERN_COMMAND_TABLE["relationship"].help_lines
    assert "/rp relationship list [project-id]" in TAVERN_COMMAND_TABLE["relationship"].help_lines
    assert "/rp relationship inspect <relationship-id>" in TAVERN_COMMAND_TABLE["relationship"].help_lines
    assert "/rp relationship rename <relationship-id> <label>" in TAVERN_COMMAND_TABLE["relationship"].help_lines
    assert "/rp relationship update <relationship-id> <state...>" in TAVERN_COMMAND_TABLE["relationship"].help_lines
    assert "/rp relationship delete <relationship-id>" in TAVERN_COMMAND_TABLE["relationship"].help_lines
    assert "/rp relationship export <relationship-id>" in TAVERN_COMMAND_TABLE["relationship"].help_lines
    assert "/rp character state add <project-id> <label> <state...>" in TAVERN_COMMAND_TABLE["character"].help_lines
    assert "/rp character state list [project-id]" in TAVERN_COMMAND_TABLE["character"].help_lines
    assert "/rp character state inspect <character-state-id>" in TAVERN_COMMAND_TABLE["character"].help_lines
    assert "/rp character state update <character-state-id> <state...>" in TAVERN_COMMAND_TABLE["character"].help_lines
    assert "/rp character state delete <character-state-id>" in TAVERN_COMMAND_TABLE["character"].help_lines
    assert "/rp character state export <character-state-id>" in TAVERN_COMMAND_TABLE["character"].help_lines
    assert "/rp location add <project-id> <label> <description...>" in TAVERN_COMMAND_TABLE["location"].help_lines
    assert "/rp location list [project-id]" in TAVERN_COMMAND_TABLE["location"].help_lines
    assert "/rp location inspect <location-id>" in TAVERN_COMMAND_TABLE["location"].help_lines
    assert "/rp location update <location-id> <description...>" in TAVERN_COMMAND_TABLE["location"].help_lines
    assert "/rp location delete <location-id>" in TAVERN_COMMAND_TABLE["location"].help_lines
    assert "/rp location export <location-id>" in TAVERN_COMMAND_TABLE["location"].help_lines
    assert "/rp organization add <project-id> <label> <description...>" in TAVERN_COMMAND_TABLE["organization"].help_lines
    assert "/rp organization list [project-id]" in TAVERN_COMMAND_TABLE["organization"].help_lines
    assert "/rp organization inspect <organization-id>" in TAVERN_COMMAND_TABLE["organization"].help_lines
    assert "/rp organization update <organization-id> <description...>" in TAVERN_COMMAND_TABLE["organization"].help_lines
    assert "/rp organization delete <organization-id>" in TAVERN_COMMAND_TABLE["organization"].help_lines
    assert "/rp plot thread add <project-id> <label> <description...>" in TAVERN_COMMAND_TABLE["plot"].help_lines
    assert "/rp plot thread list [project-id]" in TAVERN_COMMAND_TABLE["plot"].help_lines
    assert "/rp plot thread inspect <plot-thread-id>" in TAVERN_COMMAND_TABLE["plot"].help_lines
    assert "/rp plot thread update <plot-thread-id> <description...>" in TAVERN_COMMAND_TABLE["plot"].help_lines
    assert "/rp plot thread delete <plot-thread-id>" in TAVERN_COMMAND_TABLE["plot"].help_lines
    assert "/rp style sample add <project-id> <label> <sample...>" in TAVERN_COMMAND_TABLE["style"].help_lines
    assert "/rp style sample list [project-id]" in TAVERN_COMMAND_TABLE["style"].help_lines
    assert "/rp style sample inspect <style-sample-id>" in TAVERN_COMMAND_TABLE["style"].help_lines
    assert "/rp style sample update <style-sample-id> <sample...>" in TAVERN_COMMAND_TABLE["style"].help_lines
    assert "/rp style sample delete <style-sample-id>" in TAVERN_COMMAND_TABLE["style"].help_lines
    assert "/rp timeline add <project-id> <date> <title> [description...]" in TAVERN_COMMAND_TABLE["timeline"].help_lines
    assert "/rp timeline list [project-id]" in TAVERN_COMMAND_TABLE["timeline"].help_lines
    assert "/rp timeline inspect <timeline-id>" in TAVERN_COMMAND_TABLE["timeline"].help_lines
    assert "/rp timeline export <timeline-id>" in TAVERN_COMMAND_TABLE["timeline"].help_lines


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


def test_project_info_and_inspect_show_same_output(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    runtime.handle_command_sync(
        RPCommand("project", ["brief", "type", "set", str(project["id"]), "novel"], "/rp project brief type set 1 novel"),
        Event(),
    )
    runtime.handle_command_sync(
        RPCommand(
            "project",
            ["brief", "premise", "set", str(project["id"]), "A city wakes at dawn."],
            "/rp project brief premise set 1 A city wakes at dawn.",
        ),
        Event(),
    )
    runtime.store.set_project_outline(project["id"], "An old lighthouse guards the bay.")

    info_output = runtime.handle_command_sync(
        RPCommand("project", ["info", str(project["id"])], f"/rp project info {project['id']}"),
        Event(),
    )
    inspect_output = runtime.handle_command_sync(
        RPCommand("project", ["inspect", str(project["id"])], f"/rp project inspect {project['id']}"),
        Event(),
    )
    assert inspect_output == info_output


@pytest.mark.parametrize(
    "command",
    [
        RPCommand("project", ["inspect"], "/rp project inspect"),
        RPCommand("project", ["inspect", "not-a-number"], "/rp project inspect not-a-number"),
        RPCommand("project", ["inspect", "0"], "/rp project inspect 0"),
        RPCommand("project", ["inspect", "-1"], "/rp project inspect -1"),
        RPCommand("project", ["inspect", "1", "extra"], "/rp project inspect 1 extra"),
    ],
)
def test_project_inspect_invalid_args_return_usage(tmp_path, command):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = runtime.handle_command_sync(command, Event())

    assert response.startswith("Usage: /rp project")
    assert "/rp project inspect <project-id>" in response


def test_project_inspect_missing_project_returns_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = runtime.handle_command_sync(
        RPCommand("project", ["inspect", "9999"], "/rp project inspect 9999"),
        Event(),
    )
    assert response == "No novel project found: 9999"


@pytest.mark.parametrize(
    "command, expected_prefix",
    [
        (RPCommand("project", ["info"], "/rp project info"), "Usage: /rp project info"),
        (RPCommand("project", ["set", "not-a-number"], "/rp project set not-a-number"), "Usage: /rp project set <id>"),
            (
                RPCommand(
                    "project",
                    ["revision", "add", "abc", "draft", "Noisy harbor bell."],
                    "/rp project revision add abc draft Noisy harbor bell.",
                ),
                PROJECT_REVISION_USAGE,
            ),
        (
            RPCommand(
                "project",
                ["revision", "list", "abc"],
                "/rp project revision list abc",
            ),
            "Usage: /rp project revision list [project-id]",
        ),
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


def test_project_command_help_includes_inspect_line(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp project inspect <project-id>" in help_output


def test_project_command_help_includes_outline_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp project outline [project-id]" in help_output
    assert "/rp project outline inspect [project-id]" in help_output
    assert "/rp project outline set [project-id] <text>" in help_output
    assert "/rp project outline clear [project-id]" in help_output


def test_project_command_help_includes_revision_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp project revision add <project-id> <label> <note...>" in help_output
    assert "/rp project revision list [project-id]" in help_output
    assert "/rp project revision inspect <note-id>" in help_output
    assert "/rp project revision update <note-id> <note...>" in help_output
    assert "/rp project revision delete <note-id>" in help_output


def test_project_command_help_includes_binding_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>" in help_output
    assert "/rp binding list <project|chapter|scene> <scope-id>" in help_output
    assert "/rp binding inspect <binding-id>" in help_output
    assert "/rp binding clear <binding-id>" in help_output
    assert "/rp binding rows are metadata-only/inert; not auto-applied" in help_output


def test_project_command_help_includes_relationship_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp relationship add <project-id> <label> <state...>" in help_output
    assert "/rp relationship list [project-id]" in help_output
    assert "/rp relationship inspect <relationship-id>" in help_output
    assert "/rp relationship rename <relationship-id> <label>" in help_output
    assert "/rp relationship update <relationship-id> <state...>" in help_output
    assert "/rp relationship delete <relationship-id>" in help_output
    assert "/rp relationship export <relationship-id>" in help_output


def test_project_command_help_includes_character_state_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp character state add <project-id> <label> <state...>" in help_output
    assert "/rp character state list [project-id]" in help_output
    assert "/rp character state inspect <character-state-id>" in help_output
    assert "/rp character state update <character-state-id> <state...>" in help_output
    assert "/rp character state delete <character-state-id>" in help_output
    assert "/rp character state export <character-state-id>" in help_output


def test_project_command_help_includes_timeline_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp timeline add <project-id> <date> <title> [description...]" in help_output
    assert "/rp timeline list [project-id]" in help_output
    assert "/rp timeline inspect <timeline-id>" in help_output
    assert "/rp timeline export <timeline-id>" in help_output


def test_project_command_help_includes_location_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp location add <project-id> <label> <description...>" in help_output
    assert "/rp location list [project-id]" in help_output
    assert "/rp location inspect <location-id>" in help_output
    assert "/rp location update <location-id> <description...>" in help_output
    assert "/rp location delete <location-id>" in help_output
    assert "/rp location export <location-id>" in help_output


def test_project_command_help_includes_organization_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp organization add <project-id> <label> <description...>" in help_output
    assert "/rp organization list [project-id]" in help_output
    assert "/rp organization inspect <organization-id>" in help_output
    assert "/rp organization update <organization-id> <description...>" in help_output
    assert "/rp organization delete <organization-id>" in help_output


def test_project_command_help_includes_plot_thread_lines(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    help_output = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp plot thread add <project-id> <label> <description...>" in help_output
    assert "/rp plot thread list [project-id]" in help_output
    assert "/rp plot thread inspect <plot-thread-id>" in help_output
    assert "/rp plot thread update <plot-thread-id> <description...>" in help_output
    assert "/rp plot thread delete <plot-thread-id>" in help_output


def test_binding_routes_set_list_inspect_and_clear(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    store = runtime.store
    project = store.create_project("Atlas")
    chapter = store.create_chapter(project["id"], "Opening")
    scene = store.create_scene(chapter["id"], "First Light")

    card_id = _card_with_id(store, "card-alpha")
    card_id_2 = _card_with_id(store, "card-beta")
    preset_id = _preset_with_id(store, "preset-alpha")
    lorebook_id = _lorebook_with_id(store, "lore-alpha")
    _ = _persona_with_id(store, "persona-alpha")

    project_set = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["set", "project", str(project["id"]), "card", str(card_id)],
            f"/rp binding set project {project['id']} card {card_id}",
        ),
        Event(),
    )
    assert "(metadata-only/inert)" in project_set
    assert f"project[{project['id']}] -> card:{card_id}" in project_set
    project_binding_id = int(project_set.split("[", 1)[1].split("]", 1)[0])

    project_set_override = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["set", "project", str(project["id"]), "card", str(card_id_2)],
            f"/rp binding set project {project['id']} card {card_id_2}",
        ),
        Event(),
    )
    override_id = int(project_set_override.split("[", 1)[1].split("]", 1)[0])
    assert override_id == project_binding_id
    assert f"project[{project['id']}] -> card:{card_id_2}" in project_set_override

    chapter_set_output = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["set", "chapter", str(chapter["id"]), "preset", str(preset_id)],
            f"/rp binding set chapter {chapter['id']} preset {preset_id}",
        ),
        Event(),
    )
    chapter_binding_id = int(chapter_set_output.split("[", 1)[1].split("]", 1)[0])

    scene_set_output = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["set", "scene", str(scene["id"]), "lorebook", str(lorebook_id)],
            f"/rp binding set scene {scene['id']} lorebook {lorebook_id}",
        ),
        Event(),
    )
    scene_binding_id = int(scene_set_output.split("[", 1)[1].split("]", 1)[0])

    list_output = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["list", "project", str(project["id"])],
            "/rp binding list project 1",
        ),
        Event(),
    )
    assert list_output == (
        f"Default bindings for project[{project['id']}] (metadata-only/inert):\n"
        f"- [{project_binding_id}] card:{card_id_2}"
    )

    chapter_list = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["list", "chapter", str(chapter["id"])],
            f"/rp binding list chapter {chapter['id']}",
        ),
        Event(),
    )
    assert (
        chapter_list
        == f"Default bindings for chapter[{chapter['id']}] (metadata-only/inert):\n- [{chapter_binding_id}] preset:{preset_id}"
    )

    scene_list = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["list", "scene", str(scene["id"])],
            f"/rp binding list scene {scene['id']}",
        ),
        Event(),
    )
    assert (
        scene_list
        == f"Default bindings for scene[{scene['id']}] (metadata-only/inert):\n- [{scene_binding_id}] lorebook:{lorebook_id}"
    )

    inspect = runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["inspect", str(project_binding_id)],
            f"/rp binding inspect {project_binding_id}",
        ),
        Event(),
    )
    assert (
        inspect
        == f"Default binding [{project_binding_id}] project[{project['id']}] -> card:{card_id_2} (metadata-only/inert)"
    )

    clear = runtime.handle_command_sync(
        RPCommand("binding", ["clear", str(project_binding_id)], f"/rp binding clear {project_binding_id}"),
        Event(),
    )
    assert clear == f"Default binding [{project_binding_id}] cleared. (metadata-only/inert)"

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "binding",
                ["inspect", str(project_binding_id)],
                f"/rp binding inspect {project_binding_id}",
            ),
            Event(),
        )
        == f"No default binding found: {project_binding_id}"
    )


def test_binding_command_validation_and_lookup_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    store = runtime.store
    project = store.create_project("Atlas")
    card_id = _card_with_id(store, "card-validation-alpha")

    assert (
        runtime.handle_command_sync(
            RPCommand("binding", ["set", "project", "1", "card"], "/rp binding set project 1 card"),
            Event(),
        )
        == BINDING_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "binding",
                ["set", "novel", "1", "card", str(card_id)],
                f"/rp binding set novel 1 card {card_id}",
            ),
            Event(),
        )
        == BINDING_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "binding",
                ["set", "project", str(project["id"]), "unknown", str(card_id)],
                f"/rp binding set project {project['id']} unknown {card_id}",
            ),
            Event(),
        )
        == BINDING_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "binding",
                ["set", str(card_id), str(card_id), "card", "missing-card"],
                f"/rp binding set {card_id} {card_id} card missing-card",
            ),
            Event(),
        )
        == BINDING_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "binding",
                ["set", "project", str(project["id"]), "card", "missing-card"],
                f"/rp binding set project {project['id']} card missing-card",
            ),
            Event(),
        )
        == "No card found: missing-card"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "binding",
                ["set", "project", "9999", "card", str(card_id)],
                f"/rp binding set project 9999 card {card_id}",
            ),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("binding", ["list", "project", "9999"], "/rp binding list project 9999"),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("binding", ["inspect", "9999"], "/rp binding inspect 9999"),
            Event(),
        )
        == "No default binding found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("binding", ["clear", "9999"], "/rp binding clear 9999"),
            Event(),
        )
        == "No default binding found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("binding", ["list", "invalid", "1"], "/rp binding list invalid 1"),
            Event(),
        )
        == BINDING_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("binding", ["inspect"], "/rp binding inspect"),
            Event(),
        )
        == BINDING_USAGE
    )


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


def test_all_current_inert_metadata_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(
        parse_character_card(
            {
                "name": "Mara",
                "description": "Watchful archivist",
                "first_mes": "The records begin before dawn.",
            }
        )
    )
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Mara"], "/rp start Mara"), Event())

    project = store.create_project("Harbor Ledger")
    chapter = store.create_chapter(project["id"], "Opening Night")
    scene = store.create_scene(chapter["id"], "Dockside")
    store.link_scene_session(
        scene["id"],
        store.get_active_session(session_key_from_event(Event()))["id"],
    )

    set_goal = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["goal", str(scene["id"]), "secure", "the", "lighthouse", "key", "before", "midnight."],
            "/rp scene goal 1 secure the lighthouse key before midnight.",
        ),
        Event(),
    )
    assert "Scene goal set for scene [1]: secure the lighthouse key before midnight." in set_goal

    project_premise_marker = "marker: inert: concealed archive beneath the pier."
    project_outline_marker = "marker: inert: route map with weathered margins."
    chapter_summary_marker = "marker: inert: chapter remembers the last bell toll."
    scene_summary_marker = "marker: inert: scene holds a low tide vigil."
    relationship_state_marker = "marker: inert: cautious trust grows between cartographer and sailor."
    relationship_label_marker = "marker: inert: label: tidebound compact"
    character_state_marker = "marker: inert: both keep to formal speech around elders."
    location_marker = "marker: inert: basalt watchtower overlooking the estuary."
    organization_marker = "marker: inert: guild of night lantern keepers."
    plot_thread_marker = "marker: inert: hidden map points to a sealed archive."
    style_sample_marker = "marker: inert: keep dialogue sparse and reflective."
    revision_note_marker = "marker: inert: continuity note for lantern color."
    scene_beat_marker = "marker: inert: inspect the broken chain at the pier."
    default_binding_marker = "marker: inert: default binding style sample."

    store.set_project_premise(project["id"], project_premise_marker)
    store.set_project_outline(project["id"], project_outline_marker)
    store.set_chapter_summary(chapter["id"], chapter_summary_marker)
    store.set_scene_summary(scene["id"], scene_summary_marker)

    relationship = store.create_relationship_state(
        project["id"],
        "harbor-compass",
        relationship_state_marker,
    )
    store.rename_relationship_state(relationship["id"], relationship_label_marker)
    store.create_character_state(project["id"], "mara", character_state_marker)
    store.create_location(project["id"], "lighthouse", location_marker)
    store.create_organization(project["id"], "Lighthouse Guild", organization_marker)
    store.create_plot_thread(project["id"], "archive-route", plot_thread_marker)
    store.create_style_sample(project["id"], "tide-speech", style_sample_marker)
    store.create_revision_note(project["id"], "continuity", revision_note_marker)
    store.create_scene_beat(scene["id"], "inspection", scene_beat_marker)

    preset_payload = import_st_preset_json(
        {"name": "No-Lock Binding", "prompts": [{"name": "style", "content": default_binding_marker}]}
    )
    default_binding_preset = SimpleNamespace(
        id="default-no-leak-preset",
        name=preset_payload.name,
        source=preset_payload.source,
        raw=preset_payload.raw,
        modules=preset_payload.modules,
    )
    default_binding_preset_id = store.save_preset(default_binding_preset)
    runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["set", "project", str(project["id"]), "preset", str(default_binding_preset_id)],
            f"/rp binding set project {project['id']} preset {default_binding_preset_id}",
        ),
        Event(),
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "Scene goal: secure the lighthouse key before midnight." in prompt
    for output in (prompt, context):
        assert project_premise_marker not in output
        assert project_outline_marker not in output
        assert chapter_summary_marker not in output
        assert scene_summary_marker not in output
        assert relationship_state_marker not in output
        assert relationship_label_marker not in output
        assert character_state_marker not in output
        assert location_marker not in output
        assert organization_marker not in output
        assert plot_thread_marker not in output
        assert style_sample_marker not in output
        assert revision_note_marker not in output
        assert scene_beat_marker not in output
        assert default_binding_marker not in output


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


def test_chapter_and_scene_summary_tokens_do_not_leak_to_debug_prompt_or_context(tmp_path):
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

    store.set_chapter_summary(chapter["id"], "marker: distinctive chapter summary token")
    store.set_scene_summary(scene["id"], "marker: distinctive scene summary token")

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "marker: distinctive chapter summary token" not in prompt
    assert "marker: distinctive scene summary token" not in prompt
    assert "marker: distinctive chapter summary token" not in context
    assert "marker: distinctive scene summary token" not in context


def test_scene_beats_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
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
    store.create_scene_beat(
        scene["id"],
        "arrival",
        "marker: distinctive scene beat token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "marker: distinctive scene beat token" not in prompt
    assert "marker: distinctive scene beat token" not in context


def test_relationship_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
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

    store.create_relationship_state(
        project["id"],
        "mara-elya",
        "marker: distinctive relationship token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "marker: distinctive relationship token" not in prompt
    assert "marker: distinctive relationship token" not in context


def test_character_state_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
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

    store.create_character_state(
        project["id"],
        "mara-elya",
        "marker: distinctive character token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "marker: distinctive character token" not in prompt
    assert "marker: distinctive character token" not in context


def test_binding_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(
        replace(
            parse_character_card(
                {"name": "Alice", "description": "Scholar", "first_mes": "Hello."}
            ),
            id="1",
        )
    )
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Atlas")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening")
    store.link_scene_session(
        scene["id"],
        store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["id"],
    )

    marker_preset_id = _preset_with_id(store, "preset-no-leak-alpha")
    runtime.handle_command_sync(
        RPCommand(
            "binding",
            ["set", "project", str(project["id"]), "preset", str(marker_preset_id)],
            f"/rp binding set project {project['id']} preset {marker_preset_id}",
        ),
        Event(),
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "Tone: measured." not in prompt
    assert "Tone: measured." not in context
    assert "Default binding" not in prompt
    assert "Default binding" not in context


def test_location_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
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

    store.create_location(
        project["id"],
        "watchtower",
        "marker: distinctive location token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "marker: distinctive location token" not in prompt
    assert "marker: distinctive location token" not in context


def test_character_state_routes_add_list_inspect_update_delete(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    add = runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "add", str(project["id"]), "mara-elya", "Trust has grown through shared victories."],
            "/rp character state add 1 mara-elya Trust has grown through shared victories.",
        ),
        Event(),
    )
    assert add == "Character state added: [1] mara-elya -> Trust has grown through shared victories."

    added_state = runtime.store.get_character_state(1)
    assert added_state is not None
    assert added_state["label"] == "mara-elya"
    assert added_state["state_text"] == "Trust has grown through shared victories."

    list_output = runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "list", str(project["id"])],
            "/rp character state list 1",
        ),
        Event(),
    )
    assert list_output == (
        "Hermes Tavern characters for project [1]:\n"
        "  - [1] mara-elya: Trust has grown through shared victories."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("character", ["state", "inspect", "1"], "/rp character state inspect 1"),
        Event(),
    )
    assert inspect == "Character state for [1] (project [1]): mara-elya: Trust has grown through shared victories."

    update = runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "update", "1", "Trust remains fragile.", ""],
            "/rp character state update 1 Trust remains fragile.",
        ),
        Event(),
    )
    assert update == "Character state updated for character [1]: Trust remains fragile."
    assert runtime.store.get_character_state(1)["state_text"] == "Trust remains fragile."

    delete = runtime.handle_command_sync(
        RPCommand("character", ["state", "delete", "1"], "/rp character state delete 1"),
        Event(),
    )
    assert delete == "Character state deleted for character [1]."
    assert runtime.store.get_character_state(1) is None

    list_after_delete = runtime.handle_command_sync(
        RPCommand("character", ["state", "list", str(project["id"])], "/rp character state list 1"),
        Event(),
    )
    assert list_after_delete == "No character states for project [1]."


def test_character_state_list_uses_active_project_fallback(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.store.create_project("Boreal")
    runtime.handle_command_sync(
        RPCommand("project", ["set", "2"], "/rp project set 2"),
        Event(),
    )

    runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "add", "2", "mara-elya", "A pact forms."],
            "/rp character state add 2 mara-elya A pact forms.",
        ),
        Event(),
    )

    listed = runtime.handle_command_sync(RPCommand("character", ["state", "list"], "/rp character state list"), Event())
    assert listed == (
        "Hermes Tavern characters for project [2]:\n"
        "  - [1] mara-elya: A pact forms."
    )


def test_character_state_routes_require_explicit_project_for_add_and_non_blank_values(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "add", "mara-elya", "Trust"], "/rp character state add mara-ilya Trust"),
            Event(),
        )
        == CHARACTER_STATE_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "add", "1", "", "Trust"], "/rp character state add 1  Trust"),
            Event(),
        )
        == CHARACTER_STATE_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "add", "1", "mara-elya", "   "], "/rp character state add 1 mara-elya   "),
            Event(),
        )
        == CHARACTER_STATE_USAGE
    )


def test_character_state_not_found_and_missing_project_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(RPCommand("character", ["state", "add", "9999", "mara-elya", "Trust"], "/rp character state add 9999 mara-elya Trust"), Event())
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(RPCommand("character", ["state", "list", "9999"], "/rp character state list 9999"), Event())
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "inspect", "9999"], "/rp character state inspect 9999"),
            Event(),
        )
        == "No character state found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "update", "9999", "Trust recovers"], "/rp character state update 9999 Trust recovers"),
            Event(),
        )
        == "No character state found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "delete", "9999"], "/rp character state delete 9999"),
            Event(),
        )
        == "No character state found: 9999"
    )


def test_character_state_no_active_project_and_list_falls_back_to_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "list"], "/rp character state list"),
            Event(),
        )
        == "Usage: /rp character state list [project-id]"
    )


def test_location_routes_add_list_inspect_update_delete(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    add = runtime.handle_command_sync(
        RPCommand(
            "location",
            ["add", str(project["id"]), "harbor", "Foghorn sounds every hour."],
            "/rp location add 1 harbor Foghorn sounds every hour.",
        ),
        Event(),
    )
    assert add == "Location added: [1] harbor -> Foghorn sounds every hour."
    added_location = runtime.store.get_location(1)
    assert added_location is not None
    assert added_location["label"] == "harbor"
    assert added_location["description_text"] == "Foghorn sounds every hour."

    list_output = runtime.handle_command_sync(
        RPCommand("location", ["list", str(project["id"])], "/rp location list 1"),
        Event(),
    )
    assert list_output == (
        "Hermes Tavern locations for project [1]:\n"
        "  - [1] harbor: Foghorn sounds every hour."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("location", ["inspect", "1"], "/rp location inspect 1"),
        Event(),
    )
    assert inspect == "Location for [1] (project [1]): harbor: Foghorn sounds every hour."

    update = runtime.handle_command_sync(
        RPCommand(
            "location",
            ["update", "1", "The bell pier remains silent."],
            "/rp location update 1 The bell pier remains silent.",
        ),
        Event(),
    )
    assert update == "Location updated for location [1]: The bell pier remains silent."
    assert runtime.store.get_location(1)["description_text"] == "The bell pier remains silent."

    delete = runtime.handle_command_sync(
        RPCommand("location", ["delete", "1"], "/rp location delete 1"),
        Event(),
    )
    assert delete == "Location deleted for location [1]."
    assert runtime.store.get_location(1) is None

    list_after_delete = runtime.handle_command_sync(
        RPCommand("location", ["list", str(project["id"])], "/rp location list 1"),
        Event(),
    )
    assert list_after_delete == "No locations for project 1."


def test_location_list_uses_active_project_fallback(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.store.create_project("Boreal")
    runtime.handle_command_sync(
        RPCommand("project", ["set", "2"], "/rp project set 2"),
        Event(),
    )

    runtime.handle_command_sync(
        RPCommand(
            "location",
            ["add", "2", "harbor", "A pact forms."],
            "/rp location add 2 harbor A pact forms.",
        ),
        Event(),
    )

    listed = runtime.handle_command_sync(
        RPCommand("location", ["list"], "/rp location list"),
        Event(),
    )
    assert listed == (
        "Hermes Tavern locations for project [2]:\n"
        "  - [1] harbor: A pact forms."
    )


def test_location_routes_require_explicit_project_for_add_and_non_blank_values(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["add", "harbor", "A", "marker"], "/rp location add harbor A marker"),
            Event(),
        )
        == LOCATION_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["add", "1", "", "A"], "/rp location add 1  A"),
            Event(),
        )
        == LOCATION_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["add", "1", "harbor", "   "], "/rp location add 1 harbor    "),
            Event(),
        )
        == LOCATION_USAGE
    )


def test_location_not_found_and_missing_project_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["add", "9999", "harbor", "Foghorn"], "/rp location add 9999 harbor Foghorn"),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["list", "9999"], "/rp location list 9999"),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["inspect", "9999"], "/rp location inspect 9999"),
            Event(),
        )
        == "No location found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["update", "9999", "Bell tolls"], "/rp location update 9999 Bell tolls"),
            Event(),
        )
        == "No location found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["delete", "9999"], "/rp location delete 9999"),
            Event(),
        )
        == "No location found: 9999"
    )


def test_location_export_by_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    location = runtime.store.create_location(
        project["id"],
        "watchtower",
        "A bell signals weather changes over the harbor.",
    )

    response = runtime.handle_command_sync(
        RPCommand(
            "location",
            ["export", str(location["id"])],
            f"/rp location export {location['id']}",
        ),
        Event(),
    )

    assert response.startswith("Location exported as JSON.")
    assert "file:" in response
    assert "MEDIA:" in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path

    from pathlib import Path

    export_path = Path(file_path)
    assert str(export_path) == str(
        tmp_path
        / "hermes home"
        / "plugins"
        / "hermes-tavern"
        / "exports"
        / "locations"
        / f"location_{location['id']}.json"
    )
    assert export_path.exists()


def test_location_export_payload_contains_fields(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    location = runtime.store.create_location(project["id"], "reef", "Signal fires glow at dusk.")

    response = runtime.handle_command_sync(
        RPCommand("location", ["export", str(location["id"])], f"/rp location export {location['id']}"),
        Event(),
    )
    assert response.startswith("Location exported as JSON.")

    from pathlib import Path

    export_path = Path(response.split("file: ", 1)[1].splitlines()[0].strip())
    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["hermes_tavern_export"] is True
    assert payload["exported_at"]
    assert payload["location_id"] == location["id"]
    assert payload["project_id"] == project["id"]
    assert payload["label"] == location["label"]
    assert payload["description_text"] == location["description_text"]
    assert payload["created_at"] == location["created_at"]
    assert payload["updated_at"] == location["updated_at"]


def test_location_export_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("location", ["export", "9999"], "/rp location export 9999"),
        Event(),
    )
    assert response == "No location found: 9999"


@pytest.mark.parametrize("location_id", ["0", "-1"])
def test_location_export_non_positive_id(tmp_path, location_id):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("location", ["export", location_id], f"/rp location export {location_id}"),
        Event(),
    )
    assert response == LOCATION_USAGE


def test_location_export_missing_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["export"], "/rp location export"),
            Event(),
        )
        == LOCATION_USAGE
    )


def test_location_export_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    location = runtime.store.create_location(project["id"], "wharf", "Foghorns echo with each tide.")

    before = runtime.store.get_location(location["id"])
    runtime.handle_command_sync(
        RPCommand("location", ["export", str(location["id"])], f"/rp location export {location['id']}"),
        Event(),
    )
    after = runtime.store.get_location(location["id"])
    assert after == before


def test_location_no_active_project_and_list_falls_back_to_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("location", ["list"], "/rp location list"),
            Event(),
        )
        == "Usage: /rp location list [project-id]"
    )


def test_organization_routes_add_list_inspect_update_delete(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    add = runtime.handle_command_sync(
        RPCommand(
            "organization",
            ["add", str(project["id"]), "lighthouse", "Monitors storms and keeps peace beacons."],
            "/rp organization add 1 lighthouse Monitors storms and keeps peace beacons.",
        ),
        Event(),
    )
    assert add == "Organization added: [1] lighthouse -> Monitors storms and keeps peace beacons."
    added_organization = runtime.store.get_organization(1)
    assert added_organization is not None
    assert added_organization["label"] == "lighthouse"
    assert (
        added_organization["description_text"] == "Monitors storms and keeps peace beacons."
    )

    list_output = runtime.handle_command_sync(
        RPCommand(
            "organization",
            ["list", str(project["id"])],
            "/rp organization list 1",
        ),
        Event(),
    )
    assert list_output == (
        "Hermes Tavern organizations for project [1]:\n"
        "  - [1] lighthouse: Monitors storms and keeps peace beacons."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("organization", ["inspect", "1"], "/rp organization inspect 1"),
        Event(),
    )
    assert inspect == "Organization for [1] (project [1]): lighthouse: Monitors storms and keeps peace beacons."

    update = runtime.handle_command_sync(
        RPCommand(
            "organization",
            ["update", "1", "Signals storms through bells and colored fire."],
            "/rp organization update 1 Signals storms through bells and colored fire.",
        ),
        Event(),
    )
    assert (
        update
        == "Organization updated for organization [1]: "
        "Signals storms through bells and colored fire."
    )
    assert runtime.store.get_organization(1)["description_text"] == "Signals storms through bells and colored fire."

    delete = runtime.handle_command_sync(
        RPCommand("organization", ["delete", "1"], "/rp organization delete 1"),
        Event(),
    )
    assert delete == "Organization deleted for organization [1]."
    assert runtime.store.get_organization(1) is None

    list_after_delete = runtime.handle_command_sync(
        RPCommand("organization", ["list", str(project["id"])], "/rp organization list 1"),
        Event(),
    )
    assert list_after_delete == "No organizations for project 1."


def test_organization_list_uses_active_project_fallback(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.store.create_project("Boreal")
    runtime.handle_command_sync(
        RPCommand("project", ["set", "2"], "/rp project set 2"),
        Event(),
    )

    runtime.handle_command_sync(
        RPCommand(
            "organization",
            ["add", "2", "lighthouse", "Signals storms through bells."],
            "/rp organization add 2 lighthouse Signals storms through bells.",
        ),
        Event(),
    )

    listed = runtime.handle_command_sync(
        RPCommand("organization", ["list"], "/rp organization list"),
        Event(),
    )
    assert listed == (
        "Hermes Tavern organizations for project [2]:\n"
        "  - [1] lighthouse: Signals storms through bells."
    )


def test_organization_routes_require_explicit_project_for_add_and_non_blank_values(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "organization",
                ["add", "lighthouse", "Signals", "storms"],
                "/rp organization add lighthouse Signals storms",
            ),
            Event(),
        )
        == ORGANIZATION_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "organization",
                ["add", "1", "", "Signals"],
                "/rp organization add 1  Signals",
            ),
            Event(),
        )
        == ORGANIZATION_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "organization",
                ["add", "1", "lighthouse", "   "],
                "/rp organization add 1 lighthouse   ",
            ),
            Event(),
        )
        == ORGANIZATION_USAGE
    )


def test_organization_not_found_and_missing_project_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "organization",
                ["add", "9999", "lighthouse", "Monitors storms."],
                "/rp organization add 9999 lighthouse Monitors storms.",
            ),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("organization", ["list", "9999"], "/rp organization list 9999"),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("organization", ["inspect", "9999"], "/rp organization inspect 9999"),
            Event(),
        )
        == "No organization found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("organization", ["update", "9999", "Signals"], "/rp organization update 9999 Signals"),
            Event(),
        )
        == "No organization found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("organization", ["delete", "9999"], "/rp organization delete 9999"),
            Event(),
        )
        == "No organization found: 9999"
    )


def test_organization_no_active_project_and_list_falls_back_to_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("organization", ["list"], "/rp organization list"),
            Event(),
        )
        == "Usage: /rp organization list [project-id]"
    )


def test_organization_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
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

    store.create_organization(
        project["id"],
        "watchtower",
        "marker: distinctive organization token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "marker: distinctive organization token" not in prompt
    assert "marker: distinctive organization token" not in context


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


def test_project_revision_routes_explicit_id_flow(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    add_first = runtime.handle_command_sync(
        RPCommand(
            "project",
            ["revision", "add", str(project["id"]), "continuity", "Keep dialogue tight."],
            "/rp project revision add 1 continuity Keep dialogue tight.",
        ),
        Event(),
    )
    assert (
        add_first
        == f"Revision note added for project [{project['id']}]: continuity -> {_mobile_preview('Keep dialogue tight.', 180)}"
    )

    add_second = runtime.handle_command_sync(
        RPCommand(
            "project",
            [
                "revision",
                "add",
                str(project["id"]),
                "tone",
                "Use restrained, sensory language.",
            ],
            "/rp project revision add 1 tone Use restrained, sensory language.",
        ),
        Event(),
    )
    assert (
        add_second
        == f"Revision note added for project [{project['id']}]: tone -> {_mobile_preview('Use restrained, sensory language.', 180)}"
    )

    list_output = runtime.handle_command_sync(
        RPCommand("project", ["revision", "list", str(project["id"])], "/rp project revision list 1"),
        Event(),
    )
    assert (
        list_output
        == (
            "Hermes Tavern revision notes for project [1]:\n"
            "  - [1] continuity: Keep dialogue tight.\n"
            "  - [2] tone: Use restrained, sensory language."
        )
    )

    inspect = runtime.handle_command_sync(
        RPCommand("project", ["revision", "inspect", "1"], "/rp project revision inspect 1"),
        Event(),
    )
    assert (
        inspect
        == (
            "Revision note for [1] (project [1]): "
            "continuity: "
            f"{_mobile_preview('Keep dialogue tight.', 220)}"
        )
    )

    update = runtime.handle_command_sync(
        RPCommand(
            "project",
            ["revision", "update", "1", "Keep dialogue grounded, then deliberate."],
            "/rp project revision update 1 Keep dialogue grounded, then deliberate.",
        ),
        Event(),
    )
    assert (
        update
        == (
            "Revision note updated for revision note [1]: "
            f"{_mobile_preview('Keep dialogue grounded, then deliberate.', 180)}"
        )
    )
    assert (
        runtime.store.get_revision_note(1)["note_text"]
        == "Keep dialogue grounded, then deliberate."
    )

    delete = runtime.handle_command_sync(
        RPCommand("project", ["revision", "delete", "2"], "/rp project revision delete 2"),
        Event(),
    )
    assert delete == "Revision note deleted for revision note [2]."
    assert runtime.store.get_revision_note(2) is None

    list_after_delete = runtime.handle_command_sync(
        RPCommand("project", ["revision", "list", str(project["id"])], "/rp project revision list 1"),
        Event(),
    )
    assert (
        list_after_delete
        == (
            "Hermes Tavern revision notes for project [1]:\n"
            "  - [1] continuity: Keep dialogue grounded, then deliberate."
        )
    )


def test_project_revision_routes_list_active_project_fallback_and_add_requires_project_id(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["revision", "list"], "/rp project revision list"),
            Event(),
        )
        == "Usage: /rp project revision list [project-id]"
    )

    runtime.handle_command_sync(RPCommand("project", ["set", str(project["id"])], "/rp project set 1"), Event())

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "project",
                ["revision", "add", "continuity", "Keep the harbor scenes measured."],
                "/rp project revision add continuity Keep the harbor scenes measured.",
            ),
            Event(),
        )
        == PROJECT_REVISION_USAGE
    )

    add_explicit = runtime.handle_command_sync(
        RPCommand(
            "project",
            ["revision", "add", str(project["id"]), "continuity", "Keep the harbor scenes measured."],
            "/rp project revision add 1 continuity Keep the harbor scenes measured.",
        ),
        Event(),
    )
    assert (
        add_explicit
        == f"Revision note added for project [{project['id']}]: continuity -> {_mobile_preview('Keep the harbor scenes measured.', 180)}"
    )

    list_fallback = runtime.handle_command_sync(
        RPCommand("project", ["revision", "list"], "/rp project revision list"),
        Event(),
    )
    assert (
        list_fallback
        == "Hermes Tavern revision notes for project [1]:\n  - [1] continuity: Keep the harbor scenes measured."
    )

    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["revision", "add", "continuity", "Should fail"], "/rp project revision add continuity Should fail"),
            Event(),
        )
        == PROJECT_REVISION_USAGE
    )


def test_project_revision_missing_project_and_note_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    note = runtime.store.create_revision_note(1, "continuity", "Keep this in the notes.")

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "project",
                ["revision", "add", str(9999), "continuity", "No"],
                "/rp project revision add 9999 continuity No",
            ),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["revision", "list", str(9999)], "/rp project revision list 9999"),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["revision", "inspect", str(note["id"])], "/rp project revision inspect 1"),
            Event(),
        )
        == "Revision note for [1] (project [1]): continuity: Keep this in the notes."
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["revision", "inspect", "9999"], "/rp project revision inspect 9999"),
            Event(),
        )
        == "No revision note found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["revision", "update", str(note["id"]), "Rephrased."], "/rp project revision update 1 Rephrased."),
            Event(),
        )
        == "Revision note updated for revision note [1]: Rephrased."
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "project",
                ["revision", "delete", "9999"],
                "/rp project revision delete 9999",
            ),
            Event(),
        )
        == "No revision note found: 9999"
    )


def test_project_revision_not_found_message_uses_not_found_text(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    assert (
        runtime.handle_command_sync(
            RPCommand("project", ["revision", "inspect", "9999"], "/rp project revision inspect 9999"),
            Event(),
        )
        == "No revision note found: 9999"
    )


def test_project_revision_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
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
    store.create_revision_note(
        project["id"],
        "continuity",
        "marker: distinctive revision note token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())

    assert "marker: distinctive revision note token" not in prompt
    assert "marker: distinctive revision note token" not in context


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


def test_relationship_routes_add_list_inspect_update_delete(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    add = runtime.handle_command_sync(
        RPCommand(
            "relationship",
            [
                "add",
                str(project["id"]),
                "mara-ilya",
                "Trust has grown through shared victories.",
            ],
            "/rp relationship add 1 mara-ilya Trust has grown through shared victories.",
        ),
        Event(),
    )
    assert add == "Relationship state added: [1] mara-ilya -> Trust has grown through shared victories."

    added_state = runtime.store.get_relationship_state(1)
    assert added_state is not None
    assert added_state["label"] == "mara-ilya"
    assert added_state["state_text"] == "Trust has grown through shared victories."

    list_output = runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["list", str(project["id"])],
            "/rp relationship list 1",
        ),
        Event(),
    )
    assert list_output == (
        "Hermes Tavern relationships for project [1]:\n"
        "  - [1] mara-ilya: Trust has grown through shared victories."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("relationship", ["inspect", "1"], "/rp relationship inspect 1"),
        Event(),
    )
    assert inspect == "Relationship state for [1] (project [1]): mara-ilya: Trust has grown through shared victories."

    rename = runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["rename", "1", "mara-calder", "companion"],
            "/rp relationship rename 1 mara-calder companion",
        ),
        Event(),
    )
    assert rename == "Relationship label updated for relationship [1]: mara-calder companion"
    renamed_state = runtime.store.get_relationship_state(1)
    assert renamed_state is not None
    assert renamed_state["label"] == "mara-calder companion"
    assert renamed_state["state_text"] == "Trust has grown through shared victories."

    inspect_after_rename = runtime.handle_command_sync(
        RPCommand("relationship", ["inspect", "1"], "/rp relationship inspect 1"),
        Event(),
    )
    assert (
        inspect_after_rename
        == "Relationship state for [1] (project [1]): mara-calder companion: Trust has grown through shared victories."
    )

    list_output_after_rename = runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["list", str(project["id"])],
            "/rp relationship list 1",
        ),
        Event(),
    )
    assert "mara-calder companion" in list_output_after_rename
    assert "mara-ilya" not in list_output_after_rename

    update = runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["update", "1", "Trust remains fragile.", ""],
            "/rp relationship update 1 Trust remains fragile.",
        ),
        Event(),
    )
    assert update == "Relationship state updated for relationship [1]: Trust remains fragile."
    assert runtime.store.get_relationship_state(1)["state_text"] == "Trust remains fragile."

    delete = runtime.handle_command_sync(
        RPCommand("relationship", ["delete", "1"], "/rp relationship delete 1"),
        Event(),
    )
    assert delete == "Relationship state deleted for relationship [1]."
    assert runtime.store.get_relationship_state(1) is None

    list_after_delete = runtime.handle_command_sync(
        RPCommand("relationship", ["list", str(project["id"])], "/rp relationship list 1"),
        Event(),
    )
    assert list_after_delete == "No relationship states for project [1]."


def test_relationship_routes_rename_boundary_cases(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "relationship",
                ["rename", "not-a-number", "mara-calder", "friend"],
                "/rp relationship rename not-a-number mara-calder friend",
            ),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["rename", "1"], "/rp relationship rename 1"),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["rename", "1", ""], "/rp relationship rename 1"),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["rename", "1", "", ""], "/rp relationship rename 1"),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["rename", "9999", "mara"], "/rp relationship rename 9999 mara"),
            Event(),
        )
        == "No relationship state found: 9999"
    )


def test_relationship_list_uses_active_project_fallback(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.store.create_project("Boreal")
    runtime.handle_command_sync(
        RPCommand("project", ["set", "2"], "/rp project set 2"),
        Event(),
    )

    runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["add", "2", "mara-elya", "A pact forms."],
            "/rp relationship add 2 mara-elya A pact forms.",
        ),
        Event(),
    )

    listed = runtime.handle_command_sync(RPCommand("relationship", ["list"], "/rp relationship list"), Event())
    assert listed == (
        "Hermes Tavern relationships for project [2]:\n"
        "  - [1] mara-elya: A pact forms."
    )


def test_relationship_routes_require_explicit_project_for_add_and_non_blank_values(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["add", "mara-ilya", "Trust"] , "/rp relationship add mara-ilya Trust"),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["add", "1", "", "Trust"] , "/rp relationship add 1  Trust"),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["add", "1", "mara-ilya", "   "] , "/rp relationship add 1 mara-ilya   "),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )


def test_relationship_not_found_and_missing_project_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(RPCommand("relationship", ["add", "9999", "mara-ilya", "Trust"], "/rp relationship add 9999 mara-ilya Trust"), Event())
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(RPCommand("relationship", ["list", "9999"], "/rp relationship list 9999"), Event())
        == "No novel project found: 9999"
    )
    assert runtime.handle_command_sync(
        RPCommand("relationship", ["inspect", "9999"], "/rp relationship inspect 9999"),
        Event(),
    ) == "No relationship state found: 9999"
    assert runtime.handle_command_sync(
        RPCommand("relationship", ["update", "9999", "Trust recovers"], "/rp relationship update 9999 Trust recovers"),
        Event(),
    ) == "No relationship state found: 9999"
    assert runtime.handle_command_sync(
        RPCommand("relationship", ["rename", "9999", "mara"], "/rp relationship rename 9999 mara"),
        Event(),
    ) == "No relationship state found: 9999"
    assert runtime.handle_command_sync(
        RPCommand("relationship", ["delete", "9999"], "/rp relationship delete 9999"),
        Event(),
    ) == "No relationship state found: 9999"


def test_relationship_no_active_project_and_list_falls_back_to_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["list"], "/rp relationship list"),
            Event(),
        )
        == "Usage: /rp relationship list [project-id]"
    )


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


def test_chapter_list_order_and_summary_behavior_remains_stable(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.handle_command_sync(
        RPCommand("project", ["set", "1"], "/rp project set 1"),
        Event(),
    )

    runtime.handle_command_sync(
        RPCommand("chapter", ["create", "Arrival"], "/rp chapter create Arrival"),
        Event(),
    )
    runtime.handle_command_sync(
        RPCommand("chapter", ["create", "Departure"], "/rp chapter create Departure"),
        Event(),
    )

    listed = runtime.handle_command_sync(
        RPCommand("chapter", ["list"], "/rp chapter list"),
        Event(),
    )
    lines = listed.splitlines()
    assert lines[0] == "Hermes Tavern chapters for project [1]:"
    assert lines[1].startswith("  - [1] Chapter 1: Arrival")
    assert lines[2].startswith("  - [2] Chapter 2: Departure")

    assert runtime.handle_command_sync(
        RPCommand("chapter", ["summary", "1", "Fog", "hides", "the", "market."], "/rp chapter summary 1 Fog hides the market."),
        Event(),
    ) == (
        "Chapter summary set for chapter [1]: "
        f"{_mobile_preview('Fog hides the market.', 180)}"
    )
    assert runtime.handle_command_sync(
        RPCommand("chapter", ["summary", "1"], "/rp chapter summary 1"),
        Event(),
    ) == (
        f"Chapter [1] summary: {_mobile_preview('Fog hides the market.', 220)}"
    )


def test_chapter_inspect_returns_compact_metadata_and_summary_preview(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    runtime.store.set_chapter_summary(chapter["id"], "Fog hides the market.")

    inspect = runtime.handle_command_sync(
        RPCommand(
            "chapter",
            ["inspect", str(chapter["id"])],
            f"/rp chapter inspect {chapter['id']}",
        ),
        Event(),
    )
    assert inspect == (
        f"Chapter [{chapter['id']}] for project [{chapter['project_id']}]: "
        f"Chapter {chapter['chapter_number']} {chapter['title']} ({chapter['status']}) | "
        f"summary: {_mobile_preview('Fog hides the market.', 180)}"
    )


def test_chapter_inspect_with_blank_summary_returns_not_set(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    runtime.store.set_chapter_summary(chapter["id"], "   ")

    inspect = runtime.handle_command_sync(
        RPCommand(
            "chapter",
            ["inspect", str(chapter["id"])],
            f"/rp chapter inspect {chapter['id']}",
        ),
        Event(),
    )
    assert inspect == (
        f"Chapter [{chapter['id']}] for project [{chapter['project_id']}]: "
        f"Chapter {chapter['chapter_number']} {chapter['title']} ({chapter['status']}) | "
        f"summary: (not set)"
    )


def test_chapter_inspect_bad_arguments_return_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    usage = (
        "Usage: /rp chapter create [project-id] <title> | /rp chapter list [project-id] | "
        "/rp chapter inspect <chapter-id> | /rp chapter summary <chapter-id> [text] | "
        "/rp chapter summary clear <chapter-id> | /rp chapter export <chapter-id>"
    )
    cases = [
        (RPCommand("chapter", ["inspect"], "/rp chapter inspect"), usage),
        (RPCommand("chapter", ["inspect", "-1"], "/rp chapter inspect -1"), usage),
        (RPCommand("chapter", ["inspect", "not-a-number"], "/rp chapter inspect not-a-number"), usage),
        (RPCommand("chapter", ["inspect", "0"], "/rp chapter inspect 0"), usage),
        (RPCommand("chapter", ["inspect", "1", "extra"], "/rp chapter inspect 1 extra"), usage),
    ]
    for command, expected in cases:
        assert runtime.handle_command_sync(command, Event()) == expected


def test_chapter_inspect_missing_chapter_returns_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    assert (
        runtime.handle_command_sync(
            RPCommand("chapter", ["inspect", "9999"], "/rp chapter inspect 9999"),
            Event(),
        )
        == "No novel chapter found: 9999"
    )


def test_chapter_export_with_scenes_and_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    project = runtime.store.create_project("Atlas", "A long voyage")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    runtime.store.set_chapter_summary(chapter["id"], "Fog drifts past the harbor.")
    scene_one = runtime.store.create_scene(chapter["id"], "Opening")
    runtime.store.set_scene_summary(scene_one["id"], "Bells ring over the water.")
    scene_two = runtime.store.create_scene(chapter["id"], "Crossing")

    previous_chapter = runtime.store.get_chapter(chapter["id"])
    previous_scene_one = runtime.store.get_scene(scene_one["id"])
    previous_scene_two = runtime.store.get_scene(scene_two["id"])

    response = runtime.handle_command_sync(
        RPCommand("chapter", ["export", str(chapter["id"])], f"/rp chapter export {chapter['id']}"),
        Event(),
    )

    assert response.startswith("Chapter exported as JSON.")
    assert "file:" in response
    assert "MEDIA:" in response

    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path

    from pathlib import Path
    export_path = Path(file_path)
    assert str(export_path) == str(
        tmp_path
        / "hermes home"
        / "plugins"
        / "hermes-tavern"
        / "exports"
        / "chapters"
        / f"chapter_{chapter['id']}.json"
    )
    assert export_path.exists()

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["hermes_tavern_export"] is True
    assert payload["exported_at"]
    assert payload["chapter_id"] == chapter["id"]
    assert payload["project_id"] == project["id"]
    assert payload["title"] == "Arrival"
    assert payload["chapter_number"] == chapter["chapter_number"]
    assert payload["status"] == chapter["status"]
    assert payload["summary"] == "Fog drifts past the harbor."
    assert payload["scenes"][0]["scene_id"] == scene_one["id"]
    assert payload["scenes"][0]["title"] == "Opening"
    assert payload["scenes"][0]["scene_number"] == scene_one["scene_number"]
    assert payload["scenes"][0]["summary"] == "Bells ring over the water."
    assert payload["scenes"][0]["status"] == "draft"
    assert payload["scenes"][0]["session_id"] is None
    assert payload["scenes"][1]["summary"] == ""

    assert runtime.store.get_chapter(chapter["id"]) == previous_chapter
    assert runtime.store.get_scene(scene_one["id"]) == previous_scene_one
    assert runtime.store.get_scene(scene_two["id"]) == previous_scene_two


def test_chapter_export_without_scenes_yields_empty_scenes_array(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")

    response = runtime.handle_command_sync(
        RPCommand("chapter", ["export", str(chapter["id"])], f"/rp chapter export {chapter['id']}"),
        Event(),
    )

    assert response.startswith("Chapter exported as JSON.")
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path

    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
    assert payload["scenes"] == []


def test_chapter_export_not_found_returns_error(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    response = runtime.handle_command_sync(
        RPCommand("chapter", ["export", "9999"], "/rp chapter export 9999"),
        Event(),
    )
    assert response == "No novel chapter found: 9999"


# --- Phase 155: scene export by ID ---


def test_scene_export_by_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    runtime.store.set_chapter_summary(chapter["id"], "Fog drifts past the harbor.")
    scene = runtime.store.create_scene(chapter["id"], "Opening")
    runtime.store.set_scene_summary(scene["id"], "Bells ring over the water.")

    response = runtime.handle_command_sync(
        RPCommand("scene", ["export", str(scene["id"])], f"/rp scene export {scene['id']}"),
        Event(),
    )
    assert response.startswith("Scene exported as JSON.")
    assert "file:" in response
    assert "MEDIA:" in response

    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path

    from pathlib import Path

    export_path = Path(file_path)
    assert str(export_path) == str(
        tmp_path
        / "hermes home"
        / "plugins"
        / "hermes-tavern"
        / "exports"
        / "scenes"
        / f"scene_{scene['id']}.json"
    )
    assert export_path.exists()

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["hermes_tavern_export"] is True
    assert payload["exported_at"]
    assert payload["scene_id"] == scene["id"]
    assert payload["chapter_id"] == chapter["id"]
    assert payload["title"] == "Opening"
    assert payload["scene_number"] == scene["scene_number"]
    assert payload["summary"] == "Bells ring over the water."
    assert payload["status"] == "draft"
    assert payload.get("session_id") is None
    assert payload.get("created_at") is not None
    assert payload.get("updated_at") is not None


def test_scene_export_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("scene", ["export", "9999"], "/rp scene export 9999"),
        Event(),
    )
    assert response == "No novel scene found: 9999"


def test_scene_export_non_positive_id(tmp_path, monkeypatch):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("scene", ["export", "0"], "/rp scene export 0"),
        Event(),
    )
    assert response.startswith("Usage:")


def test_scene_export_missing_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("scene", ["export"], "/rp scene export"),
        Event(),
    )
    assert response.startswith("Usage:")


def test_scene_export_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Prologue")
    runtime.store.set_scene_summary(scene["id"], "Original summary")

    previous = runtime.store.get_scene(scene["id"])
    runtime.handle_command_sync(
        RPCommand("scene", ["export", str(scene["id"])], f"/rp scene export {scene['id']}"),
        Event(),
    )
    current = runtime.store.get_scene(scene["id"])
    assert current == previous


def test_scene_export_with_session(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Linked")
    session = runtime.store.start_session("test-session-abc")
    runtime.store.link_scene_session(scene["id"], session["id"])

    response = runtime.handle_command_sync(
        RPCommand("scene", ["export", str(scene["id"])], f"/rp scene export {scene['id']}"),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path

    payload = json.loads(Path(file_path).read_text(encoding="utf-8"))
    assert payload["session_id"] == session["id"]


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


def test_chapter_summary_set_update_clear(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")

    set_first = runtime.handle_command_sync(
        RPCommand(
            "chapter",
            ["summary", str(chapter["id"]), "Fog", "hides", "the", "market."],
            "/rp chapter summary 1 Fog hides the market.",
        ),
        Event(),
    )
    assert set_first == (
        f"Chapter summary set for chapter [{chapter['id']}]: "
        f"{_mobile_preview('Fog hides the market.', 180)}"
    )
    assert (
        runtime.store.get_chapter_summary(chapter["id"])["summary"]
        == "Fog hides the market."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("chapter", ["summary", str(chapter["id"])], "/rp chapter summary 1"),
        Event(),
    )
    assert inspect == f"Chapter [{chapter['id']}] summary: {_mobile_preview('Fog hides the market.', 220)}"

    update = runtime.handle_command_sync(
        RPCommand(
            "chapter",
            ["summary", str(chapter["id"]), "Bells", "ring", "at", "dawn."],
            "/rp chapter summary 1 Bells ring at dawn.",
        ),
        Event(),
    )
    assert update == (
        f"Chapter summary set for chapter [{chapter['id']}]: "
        f"{_mobile_preview('Bells ring at dawn.', 180)}"
    )
    assert (
        runtime.store.get_chapter_summary(chapter["id"])["summary"]
        == "Bells ring at dawn."
    )

    clear = runtime.handle_command_sync(
        RPCommand("chapter", ["summary", "clear", str(chapter["id"])], "/rp chapter summary clear 1"),
        Event(),
    )
    assert clear == f"Chapter summary cleared for chapter [{chapter['id']}]."
    assert runtime.store.get_chapter_summary(chapter["id"]) is None

    assert (
        runtime.handle_command_sync(
            RPCommand("chapter", ["summary", str(chapter["id"])], "/rp chapter summary 1"),
            Event(),
        )
        == f"Chapter [{chapter['id']}] summary: (not set)"
    )


def test_chapter_summary_bad_arguments_return_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    cases = [
        (RPCommand("chapter", ["summary"], "/rp chapter summary"), "Usage: /rp chapter summary <chapter-id> [text] | /rp chapter summary clear <chapter-id>"),
        (RPCommand("chapter", ["summary", "clear", "not-a-number"], "/rp chapter summary clear not-a-number"), "Usage: /rp chapter summary <chapter-id> [text] | /rp chapter summary clear <chapter-id>"),
        (RPCommand("chapter", ["summary", "1", "   "], "/rp chapter summary 1   "), "Usage: /rp chapter summary <chapter-id> [text] | /rp chapter summary clear <chapter-id>"),
        (RPCommand("chapter", ["summary", "clear", "1", "extra"], "/rp chapter summary clear 1 extra"), "Usage: /rp chapter summary <chapter-id> [text] | /rp chapter summary clear <chapter-id>"),
    ]
    for command, expected_prefix in cases:
        assert runtime.handle_command_sync(command, Event()) == expected_prefix


def test_chapter_summary_missing_chapter_returns_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    command = RPCommand("chapter", ["summary", "9999"], "/rp chapter summary 9999")
    assert (
        runtime.handle_command_sync(command, Event())
        == "No novel chapter found: 9999"
    )
    update = RPCommand("chapter", ["summary", "9999", "No", "signal."], "/rp chapter summary 9999 No signal.")
    assert (
        runtime.handle_command_sync(update, Event())
        == "No novel chapter found: 9999"
    )
    clear = RPCommand("chapter", ["summary", "clear", "9999"], "/rp chapter summary clear 9999")
    assert (
        runtime.handle_command_sync(clear, Event())
        == "No novel chapter found: 9999"
    )


def test_scene_summary_set_update_clear(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")

    set_first = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["summary", str(scene["id"]), "Clouds", "crowd", "the", "street."],
            "/rp scene summary 1 Clouds crowd the street.",
        ),
        Event(),
    )
    assert set_first == (
        f"Scene summary set for scene [{scene['id']}]: "
        f"{_mobile_preview('Clouds crowd the street.', 180)}"
    )
    assert runtime.store.get_scene_summary(scene["id"])["summary"] == "Clouds crowd the street."

    inspect = runtime.handle_command_sync(
        RPCommand("scene", ["summary", str(scene["id"])], "/rp scene summary 1"),
        Event(),
    )
    assert inspect == f"Scene [{scene['id']}] summary: {_mobile_preview('Clouds crowd the street.', 220)}"

    update = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["summary", str(scene["id"]), "Lanterns", "flare", "through", "the", "rain."],
            "/rp scene summary 1 Lanterns flare through the rain.",
        ),
        Event(),
    )
    assert update == (
        f"Scene summary set for scene [{scene['id']}]: "
        f"{_mobile_preview('Lanterns flare through the rain.', 180)}"
    )
    assert runtime.store.get_scene_summary(scene["id"])["summary"] == "Lanterns flare through the rain."

    clear = runtime.handle_command_sync(
        RPCommand("scene", ["summary", "clear", str(scene["id"])], "/rp scene summary clear 1"),
        Event(),
    )
    assert clear == f"Scene summary cleared for scene [{scene['id']}]."
    assert runtime.store.get_scene_summary(scene["id"]) is None


def test_scene_summary_bad_arguments_return_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    usage = "Usage: /rp scene summary <scene-id> [text] | /rp scene summary clear <scene-id>"
    command_ids = [
        RPCommand("scene", ["summary"], "/rp scene summary"),
        RPCommand("scene", ["summary", "clear", "not-a-number"], "/rp scene summary clear not-a-number"),
        RPCommand("scene", ["summary", "clear", "1", "extra"], "/rp scene summary clear 1 extra"),
        RPCommand("scene", ["summary", "1", "   "], "/rp scene summary 1   "),
    ]
    for command in command_ids:
        assert runtime.handle_command_sync(command, Event()) == usage


def test_scene_summary_missing_scene_returns_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    check = [
        RPCommand("scene", ["summary", "9999"], "/rp scene summary 9999"),
        RPCommand("scene", ["summary", "9999", "Fog", "on", "the", "road."], "/rp scene summary 9999 Fog on the road."),
        RPCommand("scene", ["summary", "clear", "9999"], "/rp scene summary clear 9999"),
    ]
    for command in check:
        assert runtime.handle_command_sync(command, Event()) == "No novel scene found: 9999"


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

    response = runtime.handle_command_sync(RPCommand("project", ["export", "1"], "/rp project export 1"), Event())
    assert "Project exported as Markdown." in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path

    from pathlib import Path

    exported = Path(file_path).read_text(encoding="utf-8")
    assert "# Atlas" in exported
    assert "## Chapters" in exported


def test_project_export_includes_locations_only_when_present_and_in_order(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    runtime.store.create_project("Atlas", "A quiet beginning")
    runtime.store.set_project_style_guide(1, "Tone: grounded")
    runtime.store.create_style_sample(1, "sea-song", "Bells and gulls in low light.")
    runtime.store.create_location(1, "Harbor", "A lamp posts the river mouth.")
    runtime.store.create_organization(1, "Harbor Office", "Tracks trade by bell schedule and fog signal.")
    runtime.store.create_character_state(1, "mara", "Always curious.")
    runtime.store.create_relationship_state(
        1,
        "mara-elya",
        "Trust is a habit, then a promise.",
    )
    runtime.store.create_chapter(1, "Opening")

    response = runtime.handle_command_sync(RPCommand("project", ["export", "1"], "/rp project export 1"), Event())
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()

    from pathlib import Path
    exported = Path(file_path).read_text(encoding="utf-8")
    assert "## Style Guide" in exported
    assert "## Style Samples" in exported
    assert "## Locations" in exported
    assert "## Organizations" in exported
    assert "## Characters" in exported
    assert "## Relationships" in exported
    assert "## Chapters" in exported
    assert "### sea-song" in exported
    assert (
        exported.index("## Style Guide")
        < exported.index("## Style Samples")
        < exported.index("## Locations")
        < exported.index("## Organizations")
        < exported.index("## Characters")
        < exported.index("## Relationships")
        < exported.index("## Chapters")
    )
    assert "- Harbor: A lamp posts the river mouth." in exported
    assert "- Harbor Office: Tracks trade by bell schedule and fog signal." in exported

    runtime.store.create_project("Boreal")
    runtime.store.create_organization(2, "Dock Keepers", "Maintains tide gates and signal flags.")
    response_locations_absent = runtime.handle_command_sync(
        RPCommand("project", ["export", "2"], "/rp project export 2"),
        Event(),
    )
    file_path_locations_absent = response_locations_absent.split("file: ", 1)[1].splitlines()[0].strip()
    exported_locations_absent = Path(file_path_locations_absent).read_text(encoding="utf-8")
    assert "## Organizations" in exported_locations_absent
    assert "## Locations" not in exported_locations_absent
    assert exported_locations_absent.index("## Organizations") < exported_locations_absent.index("## Chapters")
    assert "- Dock Keepers: Maintains tide gates and signal flags." in exported_locations_absent

    runtime.store.create_project("Boreal Empty")
    response_no_locations = runtime.handle_command_sync(
        RPCommand("project", ["export", "3"], "/rp project export 3"),
        Event(),
    )
    file_path_no_locations = response_no_locations.split("file: ", 1)[1].splitlines()[0].strip()
    exported_no_locations = Path(file_path_no_locations).read_text(encoding="utf-8")
    assert "## Locations" not in exported_no_locations
    assert "## Organizations" not in exported_no_locations


def test_project_export_includes_renamed_relationship_label(tmp_path, monkeypatch):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))

    runtime.store.create_project("Atlas")
    runtime.store.create_relationship_state(
        1,
        "mara-elya",
        "Trust remains fragile.",
    )
    rename = runtime.handle_command_sync(
        RPCommand("relationship", ["rename", "1", "mara-calder"], "/rp relationship rename 1 mara-calder"),
        Event(),
    )
    assert rename == "Relationship label updated for relationship [1]: mara-calder"

    response = runtime.handle_command_sync(
        RPCommand("project", ["export", "1"], "/rp project export 1"),
        Event(),
    )
    assert "Project exported as Markdown." in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path
    exported = Path(file_path).read_text(encoding="utf-8")
    assert "## Relationships" in exported
    assert "mara-calder" in exported
    assert "mara-elya" not in exported


def test_project_export_includes_style_samples_after_outline_without_style_guide(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    runtime.store.create_project("Atlas", "A quiet harbor")
    runtime.store.set_project_outline(1, "Act one opens at the harbor with the bell.")
    runtime.store.create_style_sample(
        1,
        "sea-song",
        "Low bells and foghorns shape every exchange.",
    )
    runtime.store.create_character_state(1, "mara", "Calm under pressure.")

    response = runtime.handle_command_sync(
        RPCommand("project", ["export", "1"], "/rp project export 1"),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()

    from pathlib import Path

    exported = Path(file_path).read_text(encoding="utf-8")
    assert "## Style Guide" not in exported
    assert "## Style Samples" in exported
    assert exported.index("## Style Samples") < exported.index("## Characters")
    assert "## Outline" in exported
    assert exported.index("## Outline") < exported.index("## Style Samples")


def test_project_export_includes_revision_notes_and_orders_before_chapters(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    runtime.store.create_project("Atlas", "Quiet harbor")
    runtime.store.create_revision_note(1, "continuity", "Foreshadow the missing bell once.")
    runtime.store.create_revision_note(1, "tone", "Keep the sentences tactile and restrained.")
    runtime.store.create_chapter(1, "Opening")

    response = runtime.handle_command_sync(
        RPCommand("project", ["export", "1"], "/rp project export 1"),
        Event(),
    )
    assert "Project exported as Markdown." in response
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()

    from pathlib import Path
    exported = Path(file_path).read_text(encoding="utf-8")
    assert "## Revision Notes" in exported
    assert "- continuity: Foreshadow the missing bell once." in exported
    assert "- tone: Keep the sentences tactile and restrained." in exported
    assert exported.index("## Revision Notes") < exported.index("## Chapters")
    assert exported.index("tone: Keep the sentences tactile and restrained.") > exported.index("- continuity: Foreshadow the missing bell once.")


def test_project_export_omits_revision_notes_when_empty(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    runtime.store.create_project("Atlas", "Quiet harbor")

    response = runtime.handle_command_sync(
        RPCommand("project", ["export", "1"], "/rp project export 1"),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()

    from pathlib import Path
    exported = Path(file_path).read_text(encoding="utf-8")

    assert "## Revision Notes" not in exported


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
    assert "/rp scene inspect <scene-id>" in response
    assert "/rp scene narration <scene-id>" in response
    assert "/rp scene narration clear <scene-id>" in response
    assert "/rp scene narration pov <scene-id> <label>" in response
    assert "/rp scene narration tense <scene-id> <past|present>" in response


def test_scene_beat_command_is_listed_in_help_output(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp scene beat add <scene-id> <label> <beat...>" in response
    assert "/rp scene beat list <scene-id>" in response
    assert "/rp scene beat inspect <beat-id>" in response
    assert "/rp scene beat update <beat-id> <beat...>" in response
    assert "/rp scene beat delete <beat-id>" in response


def test_summary_command_is_listed_in_help_output(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(RPCommand("help", [], "/rp"), Event())

    assert "/rp chapter summary <chapter-id> [text]" in response
    assert "/rp chapter export <chapter-id>" in response
    assert "/rp chapter inspect <chapter-id>" in response
    assert "/rp chapter summary clear <chapter-id>" in response
    assert "/rp scene summary <scene-id> [text]" in response
    assert "/rp scene summary clear <scene-id>" in response


def test_scene_beat_set_list_inspect_update_and_delete(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")

    add_first = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["beat", "add", str(scene["id"]), "arrival", "A bell sounds at dawn."],
            "/rp scene beat add 1 arrival A bell sounds at dawn.",
        ),
        Event(),
    )
    assert add_first == "Scene beat added: [1] arrival -> A bell sounds at dawn."

    add_second = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["beat", "add", str(scene["id"]), "shift", "The watch changes."],
            "/rp scene beat add 1 shift The watch changes.",
        ),
        Event(),
    )
    assert add_second == "Scene beat added: [2] shift -> The watch changes."

    list_output = runtime.handle_command_sync(
        RPCommand("scene", ["beat", "list", str(scene["id"])], "/rp scene beat list 1"),
        Event(),
    )
    assert list_output == (
        "Hermes Tavern scene beats for scene [1]:\n"
        "  - [1] arrival: A bell sounds at dawn.\n"
        "  - [2] shift: The watch changes."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("scene", ["beat", "inspect", "2"], "/rp scene beat inspect 2"),
        Event(),
    )
    assert inspect == "Scene beat for [2] (scene [1]): shift: The watch changes."

    update = runtime.handle_command_sync(
        RPCommand(
            "scene",
            ["beat", "update", "1", "The bell sounds once more."],
            "/rp scene beat update 1 The bell sounds once more.",
        ),
        Event(),
    )
    assert update == "Scene beat updated for scene beat [1]: The bell sounds once more."

    delete = runtime.handle_command_sync(
        RPCommand("scene", ["beat", "delete", "2"], "/rp scene beat delete 2"),
        Event(),
    )
    assert delete == "Scene beat deleted for scene beat [2]."

    final_list = runtime.handle_command_sync(
        RPCommand("scene", ["beat", "list", str(scene["id"])], "/rp scene beat list 1"),
        Event(),
    )
    assert final_list == (
        "Hermes Tavern scene beats for scene [1]:\n"
        "  - [1] arrival: The bell sounds once more."
    )


def test_scene_beat_set_and_list_omit_empty_result(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")

    empty_list = runtime.handle_command_sync(
        RPCommand("scene", ["beat", "list", str(scene["id"])], "/rp scene beat list 1"),
        Event(),
    )
    assert empty_list == "No scene beats for scene [1]."


@pytest.mark.parametrize(
    "command, expected_prefix",
    [
        (RPCommand("scene", ["beat"], "/rp scene beat"), "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id>"),
        (RPCommand("scene", ["beat", "add"], "/rp scene beat add"), "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id>"),
        (RPCommand("scene", ["beat", "add", "1", "label"], "/rp scene beat add 1 label"), "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id>"),
        (RPCommand("scene", ["beat", "list"], "/rp scene beat list"), "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id>"),
        (RPCommand("scene", ["beat", "inspect"], "/rp scene beat inspect"), "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id>"),
        (RPCommand("scene", ["beat", "update", "1"], "/rp scene beat update 1"), "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id>"),
        (RPCommand("scene", ["beat", "delete"], "/rp scene beat delete"), "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id>"),
    ],
)
def test_scene_beat_bad_arguments_return_usage(tmp_path, command, expected_prefix):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(command, Event())
    assert response.startswith(expected_prefix)


@pytest.mark.parametrize(
    "command, expected_message",
    [
        (RPCommand("scene", ["beat", "add", "9999", "arrival", "No scene"], "/rp scene beat add 9999 arrival No scene"), "No novel scene found: 9999"),
        (RPCommand("scene", ["beat", "list", "9999"], "/rp scene beat list 9999"), "No novel scene found: 9999"),
        (RPCommand("scene", ["beat", "inspect", "9999"], "/rp scene beat inspect 9999"), "No scene beat found: 9999"),
        (RPCommand("scene", ["beat", "update", "9999", "no"], "/rp scene beat update 9999 no"), "No scene beat found: 9999"),
        (RPCommand("scene", ["beat", "delete", "9999"], "/rp scene beat delete 9999"), "No scene beat found: 9999"),
    ],
)
def test_scene_beat_missing_entity_returns_not_found(tmp_path, command, expected_message):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(command, Event())
    assert response == expected_message


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


def test_scene_inspect_route_returns_compact_bound_preview_and_not_linked_marker(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Opening")
    runtime.store.set_scene_summary(
        scene["id"],
        "Fog wraps the harbor and never seems to lift until noon. " * 7,
    )

    response = runtime.handle_command_sync(
        RPCommand("scene", ["inspect", str(scene["id"])], f"/rp scene inspect {scene['id']}"),
        Event(),
    )
    summary_preview = _mobile_preview(
        "Fog wraps the harbor and never seems to lift until noon. " * 7,
        180,
    )
    assert response == (
        f"Scene [{scene['id']}] for chapter [{chapter['id']}]: "
        f"Scene {scene['scene_number']} {scene['title']} ({scene['status']}) | "
        f"session: (not linked) | summary: {summary_preview}"
    )

    runtime.store.save_card(
        parse_character_card(
            {"name": "Alice", "description": "Scholar", "first_mes": "Hello."}
        )
    )
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())
    session_id = runtime.store.get_active_session(session_key_from_event(Event()))["id"]
    runtime.store.link_scene_session(scene["id"], session_id)

    linked_response = runtime.handle_command_sync(
        RPCommand("scene", ["inspect", str(scene["id"])], f"/rp scene inspect {scene['id']}"),
        Event(),
    )
    assert f"session: [{session_id}]" in linked_response
    assert f"summary: {summary_preview}" in linked_response


@pytest.mark.parametrize(
    "command, expected_prefix",
    [
        (RPCommand("scene", ["inspect"], "/rp scene inspect"), "Usage: /rp scene create <chapter-id> <title> | /rp scene list <chapter-id> | /rp scene inspect <scene-id> | /rp scene start <scene-id> | /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id> | /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id> | /rp scene summary <scene-id> [text] | /rp scene summary clear <scene-id> | /rp scene narration <scene-id> | /rp scene narration clear <scene-id> | /rp scene narration pov <scene-id> <label> | /rp scene narration tense <scene-id> <past|present>"),
        (RPCommand("scene", ["inspect", "not-a-number"], "/rp scene inspect not-a-number"), "Usage: /rp scene create <chapter-id> <title> | /rp scene list <chapter-id> | /rp scene inspect <scene-id> | /rp scene start <scene-id> | /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id> | /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id> | /rp scene summary <scene-id> [text] | /rp scene summary clear <scene-id> | /rp scene narration <scene-id> | /rp scene narration clear <scene-id> | /rp scene narration pov <scene-id> <label> | /rp scene narration tense <scene-id> <past|present>"),
        (RPCommand("scene", ["inspect", "0"], "/rp scene inspect 0"), "Usage: /rp scene create <chapter-id> <title> | /rp scene list <chapter-id> | /rp scene inspect <scene-id> | /rp scene start <scene-id> | /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id> | /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id> | /rp scene summary <scene-id> [text] | /rp scene summary clear <scene-id> | /rp scene narration <scene-id> | /rp scene narration clear <scene-id> | /rp scene narration pov <scene-id> <label> | /rp scene narration tense <scene-id> <past|present>"),
        (RPCommand("scene", ["inspect", "1", "extra"], "/rp scene inspect 1 extra"), "Usage: /rp scene create <chapter-id> <title> | /rp scene list <chapter-id> | /rp scene inspect <scene-id> | /rp scene start <scene-id> | /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id> | /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | /rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id> | /rp scene summary <scene-id> [text] | /rp scene summary clear <scene-id> | /rp scene narration <scene-id> | /rp scene narration clear <scene-id> | /rp scene narration pov <scene-id> <label> | /rp scene narration tense <scene-id> <past|present>"),
    ],
)
def test_scene_inspect_bad_arguments_return_usage(tmp_path, command, expected_prefix):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(command, Event())
    assert response.startswith(expected_prefix)


def test_scene_inspect_missing_scene_returns_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("scene", ["inspect", "9999"], "/rp scene inspect 9999"),
        Event(),
    )
    assert response == "No novel scene found: 9999"


def test_scene_inspect_returns_not_set_summary_marker(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    chapter = runtime.store.create_chapter(project["id"], "Arrival")
    scene = runtime.store.create_scene(chapter["id"], "Arrival Notes")

    response = runtime.handle_command_sync(
        RPCommand("scene", ["inspect", str(scene["id"])], f"/rp scene inspect {scene['id']}"),
        Event(),
    )
    assert response == (
        f"Scene [{scene['id']}] for chapter [{chapter['id']}]: "
        f"Scene {scene['scene_number']} {scene['title']} ({scene['status']}) | "
        f"session: (not linked) | summary: (not set)"
    )


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


def test_canon_inspect_route_returns_compact_bound_preview(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    canon = runtime.store.create_canon(
        project["id"],
        "Weather",
        "Fog wraps the harbor. " * 12,
        group="world",
    )

    response = runtime.handle_command_sync(
        RPCommand("canon", ["inspect", str(canon["id"])], f"/rp canon inspect {canon['id']}"),
        Event(),
    )

    assert (
        response
        == f"Canon [{canon['id']}] for project [{project['id']}]: "
        f"title: Weather | group: world | content: {_mobile_preview(canon['content'], 180)}"
    )


def test_canon_inspect_route_rejects_malformed_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    malformed_usage = (
        "Usage: /rp canon add <project-id> <title> <content...> [--group <group>] | "
        "/rp canon list [project-id] [group] | /rp canon inspect <canon-id> | "
        "/rp canon group [project-id] <group> | /rp canon export <canon-id>"
    )

    assert (
        runtime.handle_command_sync(
            RPCommand("canon", ["inspect"], "/rp canon inspect"), Event()
        )
        == malformed_usage
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("canon", ["inspect", "abc"], "/rp canon inspect abc"),
            Event(),
        )
        == malformed_usage
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("canon", ["inspect", str(1), "extra"], "/rp canon inspect 1 extra"),
            Event(),
        )
        == malformed_usage
    )


def test_canon_inspect_route_not_found_is_bounded(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("canon", ["inspect", "9999"], "/rp canon inspect 9999"),
            Event(),
        )
        == "No canon fact found for id [9999]."
    )


def test_canon_export_by_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    canon = runtime.store.create_canon(project["id"], "Weather", "Fog is common.", group="world")

    response = runtime.handle_command_sync(
        RPCommand("canon", ["export", str(canon["id"])], f"/rp canon export {canon['id']}"),
        Event(),
    )

    assert response.startswith("Canon fact exported as JSON.")
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path

    export_path = Path(file_path)
    assert export_path.exists()

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["hermes_tavern_export"] is True
    assert payload["exported_at"]
    assert payload["canon_id"] == canon["id"]
    assert payload["project_id"] == project["id"]
    assert payload["title"] == "Weather"
    assert payload["content"] == "Fog is common."
    assert payload["canon_group"] == "world"
    assert payload["importance"] == canon["importance"]
    assert payload["created_at"] == canon["created_at"]
    assert payload["updated_at"] == canon["updated_at"]


def test_canon_export_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("canon", ["export", "9999"], "/rp canon export 9999"),
            Event(),
        )
        == "No canon fact found: 9999"
    )


def test_canon_export_missing_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("canon", ["export"], "/rp canon export"),
        Event(),
    )
    assert response == (
        "Usage: /rp canon add <project-id> <title> <content...> [--group <group>] | "
        "/rp canon list [project-id] [group] | /rp canon inspect <canon-id> | "
        "/rp canon group [project-id] <group> | /rp canon export <canon-id>"
    )


@pytest.mark.parametrize("canon_id", ["0", "-1"])
def test_canon_export_non_positive_id(tmp_path, canon_id):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("canon", ["export", canon_id], f"/rp canon export {canon_id}"),
        Event(),
    )
    assert response == (
        "Usage: /rp canon add <project-id> <title> <content...> [--group <group>] | "
        "/rp canon list [project-id] [group] | /rp canon inspect <canon-id> | "
        "/rp canon group [project-id] <group> | /rp canon export <canon-id>"
    )


def test_canon_export_media_output(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    canon = runtime.store.create_canon(project["id"], "Weather", "Fog is common.", group="world")

    response = runtime.handle_command_sync(
        RPCommand("canon", ["export", str(canon["id"])], f"/rp canon export {canon['id']}"),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path


def test_canon_export_path_containment(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    canon = runtime.store.create_canon(project["id"], "Weather", "Fog is common.")

    response = runtime.handle_command_sync(
        RPCommand("canon", ["export", str(canon["id"])], f"/rp canon export {canon['id']}"),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    assert file_path.startswith(
        str(
            tmp_path
            / "hermes home"
            / "plugins"
            / "hermes-tavern"
            / "exports"
            / "canon"
        )
    )


def test_canon_export_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    canon = runtime.store.create_canon(project["id"], "Weather", "Fog is common.")

    before = runtime.store.get_canon(canon["id"])
    runtime.handle_command_sync(
        RPCommand("canon", ["export", str(canon["id"])], f"/rp canon export {canon['id']}"),
        Event(),
    )
    after = runtime.store.get_canon(canon["id"])
    assert after == before


def test_timeline_inspect_route_returns_compact_bound_preview(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    timeline = runtime.store.create_timeline_event(
        project["id"],
        "2450-01-01",
        "Arrival",
        description="Fog wraps the harbor. " * 12,
        sort_key="2450.01",
    )

    response = runtime.handle_command_sync(
        RPCommand("timeline", ["inspect", str(timeline["id"])], f"/rp timeline inspect {timeline['id']}"),
        Event(),
    )

    assert (
        response
        == (
            f"Timeline [{timeline['id']}] for project [{project['id']}]: "
            f"event date: {timeline['event_date']} | title: Arrival | sort key: 2450.01 | "
            f"description: {_mobile_preview(timeline['description'], 180)}"
        )
    )


def test_timeline_inspect_route_rejects_malformed_or_non_positive_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    malformed_usage = (
        "Usage: /rp timeline add <project-id> <date> <title> [description...] | "
        "/rp timeline list [project-id] | /rp timeline inspect <timeline-id> | "
        "/rp timeline export <timeline-id>"
    )

    assert (
        runtime.handle_command_sync(
            RPCommand("timeline", ["inspect"], "/rp timeline inspect"),
            Event(),
        )
        == malformed_usage
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("timeline", ["inspect", "abc"], "/rp timeline inspect abc"),
            Event(),
        )
        == malformed_usage
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("timeline", ["inspect", "0"], "/rp timeline inspect 0"),
            Event(),
        )
        == malformed_usage
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("timeline", ["inspect", "1", "extra"], "/rp timeline inspect 1 extra"),
            Event(),
        )
        == malformed_usage
    )


def test_timeline_inspect_route_not_found_is_bounded(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("timeline", ["inspect", "9999"], "/rp timeline inspect 9999"),
            Event(),
        )
        == "No timeline event found for id [9999]."
    )


def test_timeline_export_by_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    timeline = runtime.store.create_timeline_event(
        project["id"],
        "2450-01-01",
        "Arrival",
        description="Fog wraps the harbor.",
        sort_key="2450.01",
    )

    response = runtime.handle_command_sync(
        RPCommand("timeline", ["export", str(timeline["id"])], f"/rp timeline export {timeline['id']}"),
        Event(),
    )

    assert response.startswith("Timeline event exported as JSON.")
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path

    export_path = Path(file_path)
    assert export_path.exists()

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["hermes_tavern_export"] is True
    assert payload["exported_at"]
    assert payload["timeline_id"] == timeline["id"]
    assert payload["project_id"] == project["id"]
    assert payload["event_date"] == timeline["event_date"]
    assert payload["title"] == "Arrival"
    assert payload["description"] == "Fog wraps the harbor."
    assert payload["chapter_id"] == timeline["chapter_id"]
    assert payload["sort_key"] == timeline["sort_key"]
    assert payload["created_at"] == timeline["created_at"]


def test_timeline_export_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("timeline", ["export", "9999"], "/rp timeline export 9999"),
            Event(),
        )
        == "No timeline event found: 9999"
    )


def test_timeline_export_missing_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    assert (
        runtime.handle_command_sync(
            RPCommand("timeline", ["export"], "/rp timeline export"),
            Event(),
        )
        == (
            "Usage: /rp timeline add <project-id> <date> <title> [description...] | "
            "/rp timeline list [project-id] | /rp timeline inspect <timeline-id> | "
            "/rp timeline export <timeline-id>"
        )
    )


@pytest.mark.parametrize("timeline_id", ["0", "-1"])
def test_timeline_export_non_positive_id(tmp_path, timeline_id):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("timeline", ["export", timeline_id], f"/rp timeline export {timeline_id}"),
        Event(),
    )
    assert response == (
        "Usage: /rp timeline add <project-id> <date> <title> [description...] | "
        "/rp timeline list [project-id] | /rp timeline inspect <timeline-id> | "
        "/rp timeline export <timeline-id>"
    )


def test_timeline_export_media_output(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    timeline = runtime.store.create_timeline_event(
        project["id"],
        "2450-01-01",
        "Arrival",
        description="Fog wraps the harbor.",
        sort_key="2450.01",
    )

    response = runtime.handle_command_sync(
        RPCommand("timeline", ["export", str(timeline["id"])], f"/rp timeline export {timeline['id']}"),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path


def test_timeline_export_path_containment(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    timeline = runtime.store.create_timeline_event(
        project["id"],
        "2450-01-01",
        "Arrival",
        description="Fog wraps the harbor.",
    )

    response = runtime.handle_command_sync(
        RPCommand("timeline", ["export", str(timeline["id"])], f"/rp timeline export {timeline['id']}"),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    assert file_path.startswith(
        str(
            tmp_path
            / "hermes home"
            / "plugins"
            / "hermes-tavern"
            / "exports"
            / "timeline"
        )
    )


def test_timeline_export_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    timeline = runtime.store.create_timeline_event(
        project["id"],
        "2450-01-01",
        "Arrival",
        description="Fog wraps the harbor.",
    )

    before = runtime.store.get_timeline_event(timeline["id"])
    runtime.handle_command_sync(
        RPCommand("timeline", ["export", str(timeline["id"])], f"/rp timeline export {timeline['id']}"),
        Event(),
    )
    after = runtime.store.get_timeline_event(timeline["id"])
    assert after == before


def test_character_state_export_by_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    character_state = runtime.store.create_character_state(
        project["id"],
        "mara-elya",
        "Trust deepens as fog lifts over harbor plans.",
    )

    response = runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "export", str(character_state["id"])],
            f"/rp character state export {character_state['id']}",
        ),
        Event(),
    )

    assert response.startswith("Character state exported as JSON.")
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path

    export_path = Path(file_path)
    assert export_path.exists()

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["hermes_tavern_export"] is True
    assert payload["exported_at"]
    assert payload["character_state_id"] == character_state["id"]
    assert payload["project_id"] == project["id"]
    assert payload["label"] == character_state["label"]
    assert payload["state_text"] == character_state["state_text"]
    assert payload["created_at"] == character_state["created_at"]
    assert payload["updated_at"] == character_state["updated_at"]


def test_character_state_export_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "character",
                ["state", "export", "9999"],
                "/rp character state export 9999",
            ),
            Event(),
        )
        == "No character state found: 9999"
    )


@pytest.mark.parametrize("character_state_id", ["0", "-1"])
def test_character_state_export_non_positive_id(tmp_path, character_state_id):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("character", ["state", "export", character_state_id], f"/rp character state export {character_state_id}"),
        Event(),
    )
    assert response == CHARACTER_STATE_USAGE


def test_character_state_export_missing_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("character", ["state", "export"], "/rp character state export"),
            Event(),
        )
        == CHARACTER_STATE_USAGE
    )


def test_character_state_export_media_output(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    character_state = runtime.store.create_character_state(
        project["id"],
        "mara-elya",
        "Trust deepens as fog lifts over harbor plans.",
    )

    response = runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "export", str(character_state["id"])],
            f"/rp character state export {character_state['id']}",
        ),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path


def test_character_state_export_path_containment(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    character_state = runtime.store.create_character_state(
        project["id"],
        "mara-elya",
        "Trust deepens as fog lifts over harbor plans.",
    )

    response = runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "export", str(character_state["id"])],
            f"/rp character state export {character_state['id']}",
        ),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    assert file_path.startswith(
        str(
            tmp_path
            / "hermes home"
            / "plugins"
            / "hermes-tavern"
            / "exports"
            / "character-states"
        )
    )


def test_character_state_export_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    character_state = runtime.store.create_character_state(
        project["id"],
        "mara-elya",
        "Trust deepens as fog lifts over harbor plans.",
    )

    before = runtime.store.get_character_state(character_state["id"])
    runtime.handle_command_sync(
        RPCommand(
            "character",
            ["state", "export", str(character_state["id"])],
            f"/rp character state export {character_state['id']}",
        ),
        Event(),
    )
    after = runtime.store.get_character_state(character_state["id"])
    assert after == before


def test_relationship_export_by_id(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    relationship = runtime.store.create_relationship_state(
        project["id"],
        "mara-elya",
        "Trust deepens as fog lifts over harbor plans.",
    )

    response = runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["export", str(relationship["id"])],
            f"/rp relationship export {relationship['id']}",
        ),
        Event(),
    )

    assert response.startswith("Relationship state exported as JSON.")
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    from pathlib import Path

    export_path = Path(file_path)
    assert export_path.exists()

    payload = json.loads(export_path.read_text(encoding="utf-8"))
    assert payload["hermes_tavern_export"] is True
    assert payload["exported_at"]
    assert payload["relationship_id"] == relationship["id"]
    assert payload["project_id"] == project["id"]
    assert payload["label"] == relationship["label"]
    assert payload["state_text"] == relationship["state_text"]
    assert payload["created_at"] == relationship["created_at"]
    assert payload["updated_at"] == relationship["updated_at"]


def test_relationship_export_not_found(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["export", "9999"], "/rp relationship export 9999"),
            Event(),
        )
        == "No relationship state found: 9999"
    )


@pytest.mark.parametrize("relationship_id", ["0", "-1"])
def test_relationship_export_non_positive_id(tmp_path, relationship_id):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    response = runtime.handle_command_sync(
        RPCommand("relationship", ["export", relationship_id], f"/rp relationship export {relationship_id}"),
        Event(),
    )
    assert response == RELATIONSHIP_USAGE


def test_relationship_export_missing_args(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    assert (
        runtime.handle_command_sync(
            RPCommand("relationship", ["export"], "/rp relationship export"),
            Event(),
        )
        == RELATIONSHIP_USAGE
    )


def test_relationship_export_media_output(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    relationship = runtime.store.create_relationship_state(
        project["id"],
        "mara-elya",
        "Trust deepens as fog lifts over harbor plans.",
    )

    response = runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["export", str(relationship["id"])],
            f"/rp relationship export {relationship['id']}",
        ),
        Event(),
    )
    file_path = response.split("file: ", 1)[1].splitlines()[0].strip()
    media_path = response.split("MEDIA:", 1)[1].strip().strip('"')
    assert media_path == file_path


def test_relationship_export_no_mutation(tmp_path, monkeypatch):
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")
    relationship = runtime.store.create_relationship_state(
        project["id"],
        "mara-elya",
        "Trust deepens as fog lifts over harbor plans.",
    )

    before = runtime.store.get_relationship_state(relationship["id"])
    runtime.handle_command_sync(
        RPCommand(
            "relationship",
            ["export", str(relationship["id"])],
            f"/rp relationship export {relationship['id']}",
        ),
        Event(),
    )
    after = runtime.store.get_relationship_state(relationship["id"])
    assert after == before


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


def test_plot_thread_routes_add_list_inspect_update_delete(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    add = runtime.handle_command_sync(
        RPCommand(
            "plot",
            ["thread", "add", str(project["id"]), "missing-heir", "The heir has vanished."],
            "/rp plot thread add 1 missing-heir The heir has vanished.",
        ),
        Event(),
    )
    assert add == (
        "Plot thread added: [1] missing-heir -> "
        "The heir has vanished."
    )

    runtime.handle_command_sync(
        RPCommand(
            "plot",
            [
                "thread",
                "add",
                str(project["id"]),
                "rising-tension",
                "A debt ledger is missing pages.",
            ],
            "/rp plot thread add 1 rising-tension A debt ledger is missing pages.",
        ),
        Event(),
    )

    list_output = runtime.handle_command_sync(
        RPCommand("plot", ["thread", "list", str(project["id"])], "/rp plot thread list 1"),
        Event(),
    )
    assert (
        list_output
        == "Hermes Tavern plot threads for project [1]:\n"
        "  - [1] missing-heir: The heir has vanished.\n"
        "  - [2] rising-tension: A debt ledger is missing pages."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("plot", ["thread", "inspect", "1"], "/rp plot thread inspect 1"),
        Event(),
    )
    assert inspect == "Plot thread for [1] (project [1]): missing-heir: The heir has vanished."

    update = runtime.handle_command_sync(
        RPCommand(
            "plot",
            ["thread", "update", "1", "Clue appears in", "an", "old", "ledger."],
            "/rp plot thread update 1 Clue appears in an old ledger.",
        ),
        Event(),
    )
    assert update == "Plot thread updated for plot thread [1]: Clue appears in an old ledger."
    assert runtime.store.get_plot_thread(1)["description_text"] == "Clue appears in an old ledger."

    delete = runtime.handle_command_sync(
        RPCommand("plot", ["thread", "delete", "1"], "/rp plot thread delete 1"),
        Event(),
    )
    assert delete == "Plot thread deleted for plot thread [1]."
    assert runtime.store.get_plot_thread(1) is None

    list_after_delete = runtime.handle_command_sync(
        RPCommand("plot", ["thread", "list", str(project["id"])], "/rp plot thread list 1"),
        Event(),
    )
    assert (
        list_after_delete
        == "Hermes Tavern plot threads for project [1]:\n"
        "  - [2] rising-tension: A debt ledger is missing pages."
    )


def test_plot_thread_list_uses_active_project_fallback(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.store.create_project("Boreal")
    runtime.handle_command_sync(
        RPCommand("project", ["set", "2"], "/rp project set 2"),
        Event(),
    )

    runtime.handle_command_sync(
        RPCommand(
            "plot",
            ["thread", "add", "2", "harbor", "A ledger marks unresolved debt."],
            "/rp plot thread add 2 harbor A ledger marks unresolved debt.",
        ),
        Event(),
    )

    listed = runtime.handle_command_sync(
        RPCommand("plot", ["thread", "list"], "/rp plot thread list"),
        Event(),
    )
    assert (
        listed
        == "Hermes Tavern plot threads for project [2]:\n"
        "  - [1] harbor: A ledger marks unresolved debt."
    )


def test_plot_thread_routes_require_explicit_project_for_add_and_non_blank_values(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand("plot", ["thread", "add", "missing-heir", "A", "first"], "/rp plot thread add missing-heir A first"),
            Event(),
        )
        == PLOT_THREAD_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("plot", ["thread", "add", "1", "", "A"], "/rp plot thread add 1  A"),
            Event(),
        )
        == PLOT_THREAD_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("plot", ["thread", "add", "1", "missing-heir", "   "], "/rp plot thread add 1 missing-heir   "),
            Event(),
        )
        == PLOT_THREAD_USAGE
    )


def test_plot_thread_not_found_and_missing_project_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "plot",
                ["thread", "add", "9999", "missing-heir", "A", "clue"],
                "/rp plot thread add 9999 missing-heir A clue",
            ),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("plot", ["thread", "list", "9999"], "/rp plot thread list 9999"),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "plot",
                ["thread", "inspect", "9999"],
                "/rp plot thread inspect 9999",
            ),
            Event(),
        )
        == "No plot thread found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "plot",
                ["thread", "update", "9999", "New", "clue"],
                "/rp plot thread update 9999 New clue",
            ),
            Event(),
        )
        == "No plot thread found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("plot", ["thread", "delete", "9999"], "/rp plot thread delete 9999"),
            Event(),
        )
        == "No plot thread found: 9999"
    )


def test_plot_thread_no_active_project_and_list_falls_back_to_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("plot", ["thread", "list"], "/rp plot thread list"),
            Event(),
        )
        == "Usage: /rp plot thread list [project-id]"
    )


def test_style_sample_routes_add_list_inspect_update_delete(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    project = runtime.store.create_project("Atlas")

    add = runtime.handle_command_sync(
        RPCommand(
            "style",
            [
                "sample",
                "add",
                str(project["id"]),
                "sea-letters",
                "Short, salt-rough prose with rope metaphors.",
            ],
            "/rp style sample add 1 sea-letters Short, salt-rough prose with rope metaphors.",
        ),
        Event(),
    )
    assert add == (
        "Style sample added: [1] sea-letters -> "
        "Short, salt-rough prose with rope metaphors."
    )

    runtime.handle_command_sync(
        RPCommand(
            "style",
            [
                "sample",
                "add",
                str(project["id"]),
                "harbor-call",
                "Tides roll through every scene, then pull away.",
            ],
            "/rp style sample add 1 harbor-call Tides roll through every scene, then pull away.",
        ),
        Event(),
    )

    list_output = runtime.handle_command_sync(
        RPCommand("style", ["sample", "list", str(project["id"])], "/rp style sample list 1"),
        Event(),
    )
    assert (
        list_output
        == "Hermes Tavern style samples for project [1]:\n"
        "  - [1] sea-letters: Short, salt-rough prose with rope metaphors.\n"
        "  - [2] harbor-call: Tides roll through every scene, then pull away."
    )

    inspect = runtime.handle_command_sync(
        RPCommand("style", ["sample", "inspect", "1"], "/rp style sample inspect 1"),
        Event(),
    )
    assert inspect == "Style sample for [1] (project [1]): sea-letters: Short, salt-rough prose with rope metaphors."

    update = runtime.handle_command_sync(
        RPCommand(
            "style",
            ["sample", "update", "1", "Shorter, saltier prose with knots and oaths."],
            "/rp style sample update 1 Shorter, saltier prose with knots and oaths.",
        ),
        Event(),
    )
    assert update == "Style sample updated for style sample [1]: Shorter, saltier prose with knots and oaths."
    assert runtime.store.get_style_sample(1)["sample_text"] == "Shorter, saltier prose with knots and oaths."

    delete = runtime.handle_command_sync(
        RPCommand("style", ["sample", "delete", "1"], "/rp style sample delete 1"),
        Event(),
    )
    assert delete == "Style sample deleted for style sample [1]."
    assert runtime.store.get_style_sample(1) is None

    list_after_delete = runtime.handle_command_sync(
        RPCommand("style", ["sample", "list", str(project["id"])], "/rp style sample list 1"),
        Event(),
    )
    assert list_after_delete == "Hermes Tavern style samples for project [1]:\n  - [2] harbor-call: Tides roll through every scene, then pull away."


def test_style_sample_list_uses_active_project_fallback(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")
    runtime.store.create_project("Boreal")
    runtime.handle_command_sync(
        RPCommand("project", ["set", "2"], "/rp project set 2"),
        Event(),
    )

    runtime.handle_command_sync(
        RPCommand(
            "style",
            [
                "sample",
                "add",
                "2",
                "fog-lore",
                "A heavy fog tells truth only to those with sharp hearing.",
            ],
            "/rp style sample add 2 fog-lore A heavy fog tells truth only to those with sharp hearing.",
        ),
        Event(),
    )

    listed = runtime.handle_command_sync(
        RPCommand("style", ["sample", "list"], "/rp style sample list"),
        Event(),
    )
    assert listed == "Hermes Tavern style samples for project [2]:\n  - [1] fog-lore: A heavy fog tells truth only to those with sharp hearing."


def test_style_sample_routes_require_explicit_project_for_add_and_non_blank_values(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "style",
                ["sample", "add", "missing-id", "sea-letters", "Sample text"],
                "/rp style sample add missing-id sea-letters Sample text",
            ),
            Event(),
        )
        == STYLE_SAMPLE_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "style",
                ["sample", "add", "1", "", "Sample text"],
                "/rp style sample add 1  Sea sample text",
            ),
            Event(),
        )
        == STYLE_SAMPLE_USAGE
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "style",
                ["sample", "add", "1", "sea-letters", "   "],
                "/rp style sample add 1 sea-letters   ",
            ),
            Event(),
        )
        == STYLE_SAMPLE_USAGE
    )


def test_style_sample_not_found_and_missing_project_errors(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    runtime.store.create_project("Atlas")

    assert (
        runtime.handle_command_sync(
            RPCommand(
                "style",
                [
                    "sample",
                    "add",
                    "9999",
                    "sea-letters",
                    "No project.",
                ],
                "/rp style sample add 9999 sea-letters No project.",
            ),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("style", ["sample", "list", "9999"], "/rp style sample list 9999"),
            Event(),
        )
        == "No novel project found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("style", ["sample", "inspect", "9999"], "/rp style sample inspect 9999"),
            Event(),
        )
        == "No style sample found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand(
                "style",
                ["sample", "update", "9999", "Revision text"],
                "/rp style sample update 9999 Revision text",
            ),
            Event(),
        )
        == "No style sample found: 9999"
    )
    assert (
        runtime.handle_command_sync(
            RPCommand("style", ["sample", "delete", "9999"], "/rp style sample delete 9999"),
            Event(),
        )
        == "No style sample found: 9999"
    )


def test_style_sample_no_active_project_and_list_falls_back_to_usage(tmp_path):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))

    assert (
        runtime.handle_command_sync(
            RPCommand("style", ["sample", "list"], "/rp style sample list"),
            Event(),
        )
        == "Usage: /rp style sample list [project-id]"
    )


def test_plot_thread_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello."}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Atlas")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening")
    store.link_scene_session(
        scene["id"],
        store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["id"],
    )
    store.create_plot_thread(
        project["id"],
        "ominous",
        "marker: distinctive plot thread token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())
    assert "marker: distinctive plot thread token" not in prompt
    assert "marker: distinctive plot thread token" not in context


def test_style_sample_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello."}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Atlas")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening")
    store.link_scene_session(
        scene["id"],
        store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["id"],
    )
    store.create_style_sample(
        project["id"],
        "storm-signal",
        "marker: distinctive style sample token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())
    assert "marker: distinctive style sample token" not in prompt
    assert "marker: distinctive style sample token" not in context


def test_relationship_markers_do_not_leak_to_debug_prompt_or_context(tmp_path):
    store = TavernStore(tmp_path / "tavern.sqlite3")
    store.save_card(parse_character_card({"name": "Alice", "description": "Scholar", "first_mes": "Hello."}))
    runtime = TavernRuntime(store)
    runtime.handle_command_sync(RPCommand("start", ["Alice"], "/rp start Alice"), Event())

    project = store.create_project("Atlas")
    chapter = store.create_chapter(project["id"], "Prologue")
    scene = store.create_scene(chapter["id"], "Opening")
    store.link_scene_session(
        scene["id"],
        store.get_active_session("telegram:chat:chat-1:thread:main:user:user-1")["id"],
    )
    relationship = store.create_relationship_state(
        project["id"],
        "ominous bond",
        "Trust remains intentionally local metadata.",
    )
    store.rename_relationship_state(
        relationship["id"],
        "marker: distinctive relationship label token",
    )

    prompt = runtime.handle_command_sync(RPCommand("debug", ["prompt"], "/rp debug prompt"), Event())
    context = runtime.handle_command_sync(RPCommand("debug", ["context"], "/rp debug context"), Event())
    assert "marker: distinctive relationship label token" not in prompt
    assert "marker: distinctive relationship label token" not in context


def test_project_export_file_includes_all_current_metadata_sections_in_order(tmp_path, monkeypatch):
    runtime = TavernRuntime(TavernStore(tmp_path / "tavern.sqlite3"))
    monkeypatch.setenv("HERMES_HOME", str(tmp_path / "hermes home"))

    project = runtime.store.create_project("Harbor Signal", "quiet political drama")

    runtime.store.set_project_brief_type(project["id"], "novel")
    runtime.store.set_project_premise(
        project["id"],
        "A courier follows a map to the old bell tower during one final fog shift.",
    )
    runtime.store.set_project_outline(project["id"], "Act One sets the harbor map in motion; Act Two reveals debts; Act Three closes the ledger.")
    runtime.store.set_project_style_guide(
        project["id"],
        "Tone: restrained and sensory\nPacing: measured",
    )
    runtime.store.create_style_sample(project["id"], "night-watch", "Gulls keep the time where clocks cannot.")
    runtime.store.create_location(project["id"], "The Quay", "A lamp-lit landing where tides and bells dictate every decision.")
    runtime.store.create_organization(
        project["id"],
        "The Night Watch",
        "Records cargo manifests and watches every lantern change.",
    )
    runtime.store.create_plot_thread(
        project["id"],
        "Inherited Ledger",
        "A missing ledger tied to old harbor debts resurfaces.",
    )
    runtime.store.create_character_state(project["id"], "Mara Voss", "Steady negotiator, loyal to inherited promises.")
    runtime.store.create_relationship_state(
        project["id"],
        "mara-calder",
        "A pragmatic tie built from mutual leverage, not trust.",
    )
    runtime.store.create_chapter(project["id"], "Opening")

    response = runtime.handle_command_sync(
        RPCommand("project", ["export", str(project["id"])], f"/rp project export {project['id']}"),
        Event(),
    )

    assert "Project exported as Markdown." in response
    assert 'MEDIA:"' in response
    media_payload = response.split("MEDIA:", 1)[1].strip()
    assert media_payload.startswith('"') and media_payload.endswith('"')
    file_path = media_payload[1:-1]

    from pathlib import Path

    exported_path = Path(file_path)
    assert str(exported_path).startswith(str(tmp_path / "hermes home"))
    assert exported_path.exists()

    exported = exported_path.read_text(encoding="utf-8")

    section_headers = [
        "## Summary",
        "## Project Brief",
        "## Outline",
        "## Style Guide",
        "## Style Samples",
        "## Locations",
        "## Organizations",
        "## Plot Threads",
        "## Characters",
        "## Relationships",
        "## Chapters",
    ]
    section_indexes = [exported.index(section) for section in section_headers]
    assert section_indexes == sorted(section_indexes)

    assert "A courier follows a map" in exported
    assert "Type: novel" in exported
    assert "Act One sets the harbor map in motion" in exported
    assert "Tone: restrained and sensory" in exported
    assert "### night-watch" in exported
    assert "The Quay" in exported
    assert "Night Watch" in exported
    assert "Inherited Ledger" in exported
    assert "Mara Voss" in exported
    assert "mara-calder" in exported
    assert "### Chapter 1: Opening" in exported
