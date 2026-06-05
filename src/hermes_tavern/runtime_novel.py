"""Novel domain command handlers for Hermes Tavern runtime."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hermes_tavern.commands import RPCommand
from hermes_tavern.hermes_home import get_hermes_home
from hermes_tavern import runtime_lifecycle
from hermes_tavern.identity import session_key_from_event
from hermes_tavern.runtime_utils import mobile_preview as _mobile_preview


def project_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "create":
        return project_create(runtime, command, event)
    if subcommand == "list":
        return project_list(runtime)
    if subcommand == "info":
        return project_info(runtime, command)
    if subcommand == "set":
        return project_set(runtime, command, event)
    if subcommand == "outline":
        return project_outline(runtime, command, event)
    if subcommand == "export":
        return project_export(runtime, command, event)
    if subcommand == "style":
        return project_style(runtime, command, event)
    if subcommand == "brief":
        return project_brief(runtime, command, event)
    return (
        "Usage: /rp project create <title> | /rp project list | /rp project info <id> | /rp project set <id> "
        "| /rp project export [id] | /rp project style [project-id] | /rp project style inspect [project-id] | "
        "/rp project style set [project-id] <text> | /rp project style clear [project-id] "
        "| /rp project brief [project-id] | /rp project brief inspect [project-id] | "
        "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other> | "
        "/rp project brief type clear <project-id> | /rp project brief premise set <project-id> <text> | "
        "/rp project brief premise clear <project-id> | /rp project outline [project-id] | /rp project outline inspect [project-id] | "
        "/rp project outline set [project-id] <text> | /rp project outline clear [project-id]"
    )


def chapter_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "create":
        return chapter_create(runtime, command, event)
    if subcommand == "list":
        return chapter_list(runtime, command, event)
    if subcommand == "summary":
        return chapter_summary(runtime, command, event)
    return (
        "Usage: /rp chapter create [project-id] <title> | /rp chapter list [project-id] | "
        "/rp chapter summary <chapter-id> [text] | /rp chapter summary clear <chapter-id>"
    )


def scene_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "create":
        return scene_create(runtime, command, event)
    if subcommand == "list":
        return scene_list(runtime, command)
    if subcommand == "start":
        return scene_start(runtime, command, event)
    if subcommand == "beat":
        return scene_beat(runtime, command, event)
    if subcommand == "goal":
        return scene_goal(runtime, command)
    if subcommand == "narration":
        return scene_narration(runtime, command)
    if subcommand == "summary":
        return scene_summary(runtime, command, event)
    return (
        "Usage: /rp scene create <chapter-id> <title> | /rp scene list <chapter-id> | "
        "/rp scene start <scene-id> | /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id> | "
        "/rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | "
        "/rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | /rp scene beat delete <beat-id> | "
        "/rp scene summary <scene-id> [text] | /rp scene summary clear <scene-id> | "
        "/rp scene narration <scene-id> | /rp scene narration clear <scene-id> | "
        "/rp scene narration pov <scene-id> <label> | /rp scene narration tense <scene-id> <past|present>"
    )


def canon_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "add":
        return canon_add(runtime, command, event)
    if subcommand == "list":
        return canon_list(runtime, command, event)
    if subcommand == "group":
        return canon_group(runtime, command, event)
    return "Usage: /rp canon add <project-id> <title> <content...> | /rp canon list [project-id] [group] | /rp canon group [project-id] <group>"


def timeline_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "add":
        return timeline_add(runtime, command, event)
    if subcommand == "list":
        return timeline_list(runtime, command, event)
    return "Usage: /rp timeline add <project-id> <date> <title> [description...] | /rp timeline list [project-id]"


def character_command(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return _CHARACTER_USAGE

    if command.args[0].lower() != "state":
        return _CHARACTER_USAGE

    subcommand = command.args[1].lower()
    if subcommand == "add":
        return character_state_add(runtime, command, event)
    if subcommand == "list":
        return character_state_list(runtime, command, event)
    if subcommand == "inspect":
        return character_state_inspect(runtime, command)
    if subcommand == "update":
        return character_state_update(runtime, command)
    if subcommand == "delete":
        return character_state_delete(runtime, command)

    return _CHARACTER_USAGE


def relationship_command(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return _RELATIONSHIP_USAGE

    subcommand = command.args[0].lower()
    if subcommand == "add":
        return relationship_add(runtime, command, event)
    if subcommand == "list":
        return relationship_list(runtime, command, event)
    if subcommand == "inspect":
        return relationship_inspect(runtime, command)
    if subcommand == "update":
        return relationship_update(runtime, command)
    if subcommand == "delete":
        return relationship_delete(runtime, command)

    return _RELATIONSHIP_USAGE


def location_command(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return _LOCATION_USAGE

    subcommand = command.args[0].lower()
    if subcommand == "add":
        return location_add(runtime, command, event)
    if subcommand == "list":
        return location_list(runtime, command, event)
    if subcommand == "inspect":
        return location_inspect(runtime, command)
    if subcommand == "update":
        return location_update(runtime, command)
    if subcommand == "delete":
        return location_delete(runtime, command)

    return _LOCATION_USAGE


def organization_command(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return _ORGANIZATION_USAGE

    subcommand = command.args[0].lower()
    if subcommand == "add":
        return organization_add(runtime, command, event)
    if subcommand == "list":
        return organization_list(runtime, command, event)
    if subcommand == "inspect":
        return organization_inspect(runtime, command)
    if subcommand == "update":
        return organization_update(runtime, command)
    if subcommand == "delete":
        return organization_delete(runtime, command)

    return _ORGANIZATION_USAGE


def plot_command(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return _PLOT_THREAD_USAGE

    if command.args[0].lower() != "thread":
        return _PLOT_THREAD_USAGE

    if len(command.args) < 2:
        return _PLOT_THREAD_USAGE

    subcommand = command.args[1].lower()
    if subcommand == "add":
        return plot_thread_add(runtime, command, event)
    if subcommand == "list":
        return plot_thread_list(runtime, command, event)
    if subcommand == "inspect":
        return plot_thread_inspect(runtime, command)
    if subcommand == "update":
        return plot_thread_update(runtime, command)
    if subcommand == "delete":
        return plot_thread_delete(runtime, command)

    return _PLOT_THREAD_USAGE


def binding_command(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return BINDING_USAGE

    subcommand = command.args[0].lower()
    if subcommand == "set":
        return binding_set(runtime, command, event)
    if subcommand == "list":
        return binding_list(runtime, command)
    if subcommand == "inspect":
        return binding_inspect(runtime, command)
    if subcommand == "clear":
        return binding_clear(runtime, command)

    return BINDING_USAGE


def style_command(runtime: Any, command: RPCommand, event: Any) -> str:
    if not command.args:
        return _STYLE_SAMPLE_USAGE

    if command.args[0].lower() != "sample":
        return _STYLE_SAMPLE_USAGE

    if len(command.args) < 2:
        return _STYLE_SAMPLE_USAGE

    subcommand = command.args[1].lower()
    if subcommand == "add":
        return style_sample_add(runtime, command, event)
    if subcommand == "list":
        return style_sample_list(runtime, command, event)
    if subcommand == "inspect":
        return style_sample_inspect(runtime, command)
    if subcommand == "update":
        return style_sample_update(runtime, command)
    if subcommand == "delete":
        return style_sample_delete(runtime, command)

    return _STYLE_SAMPLE_USAGE


def _safe_int(text: str) -> int | None:
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


BINDING_USAGE = (
    "Usage: /rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id> | "
    "/rp binding list <project|chapter|scene> <scope-id> | "
    "/rp binding inspect <binding-id> | /rp binding clear <binding-id>. "
    "Default bindings are metadata-only/inert and are not auto-applied."
)


_RELATIONSHIP_USAGE = (
    "Usage: /rp relationship add <project-id> <label> <state...> | "
    "/rp relationship list [project-id] | /rp relationship inspect <relationship-id> | "
    "/rp relationship update <relationship-id> <state...> | "
    "/rp relationship delete <relationship-id>"
)


_LOCATION_USAGE = (
    "Usage: /rp location add <project-id> <label> <description...> | "
    "/rp location list [project-id] | /rp location inspect <location-id> | "
    "/rp location update <location-id> <description...> | "
    "/rp location delete <location-id>"
)


_ORGANIZATION_USAGE = (
    "Usage: /rp organization add <project-id> <label> <description...> | "
    "/rp organization list [project-id] | /rp organization inspect <organization-id> | "
    "/rp organization update <organization-id> <description...> | "
    "/rp organization delete <organization-id>"
)

_PLOT_THREAD_USAGE = (
    "Usage: /rp plot thread add <project-id> <label> <description...> | "
    "/rp plot thread list [project-id] | /rp plot thread inspect <plot-thread-id> | "
    "/rp plot thread update <plot-thread-id> <description...> | "
    "/rp plot thread delete <plot-thread-id>"
)


_STYLE_SAMPLE_USAGE = (
    "Usage: /rp style sample add <project-id> <label> <sample...> | "
    "/rp style sample list [project-id] | /rp style sample inspect <style-sample-id> | "
    "/rp style sample update <style-sample-id> <sample...> | "
    "/rp style sample delete <style-sample-id>"
)


_CHARACTER_USAGE = (
    "Usage: /rp character state add <project-id> <label> <state...> | "
    "/rp character state list [project-id] | /rp character state inspect <character-state-id> | "
    "/rp character state update <character-state-id> <state...> | "
    "/rp character state delete <character-state-id>"
)


def _binding_error_text(error: str, context_id: str | int) -> str:
    if error == "Invalid scope type":
        return BINDING_USAGE
    if error == "Invalid asset type":
        return BINDING_USAGE
    if error == "Card not found":
        return f"No card found: {context_id}"
    if error == "Preset not found":
        return f"No preset found: {context_id}"
    if error == "Lorebook not found":
        return f"No lorebook found: {context_id}"
    if error == "Persona not found":
        return f"No persona found: {context_id}"
    if error == "Project not found":
        return f"No novel project found: {context_id}"
    if error == "Chapter not found":
        return f"No novel chapter found: {context_id}"
    if error == "Scene not found":
        return f"No novel scene found: {context_id}"
    return "Could not set binding."


def _parse_binding_set(command: RPCommand) -> tuple[str, int, str, str] | str:
    if len(command.args) != 5:
        return BINDING_USAGE

    scope_type = (command.args[1] or "").strip().lower()
    scope_id = _safe_int(command.args[2])
    asset_type = (command.args[3] or "").strip().lower()
    asset_id = (command.args[4] or "").strip()

    if scope_id is None or scope_id <= 0:
        return BINDING_USAGE
    if not asset_id:
        return BINDING_USAGE
    return scope_type, scope_id, asset_type, asset_id


def binding_set(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    parsed = _parse_binding_set(command)
    if isinstance(parsed, str):
        return parsed
    scope_type, scope_id, asset_type, asset_id = parsed
    try:
        binding = runtime.store.set_default_binding(
            scope_type,
            scope_id,
            asset_type,
            asset_id,
        )
    except ValueError as exc:
        error = str(exc)
        context_id: str | int = (
            scope_id
            if error in {"Project not found", "Chapter not found", "Scene not found"}
            else asset_id
        )
        return _binding_error_text(error, context_id)

    return (
        f"Default binding set: [{binding['id']}] {binding['scope_type']}[{binding['scope_id']}] -> "
        f"{binding['asset_type']}:{binding['asset_id']} (metadata-only/inert)"
    )


def binding_list(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 3:
        return BINDING_USAGE

    scope_type = (command.args[1] or "").strip().lower()
    scope_id = _safe_int(command.args[2])
    if scope_id is None or scope_id <= 0:
        return BINDING_USAGE

    try:
        bindings = runtime.store.list_default_bindings(scope_type, scope_id)
    except ValueError as exc:
        return _binding_error_text(str(exc), scope_id)

    if not bindings:
        return f"No default bindings for {scope_type}[{scope_id}] (metadata-only/inert)"

    lines = [f"Default bindings for {scope_type}[{scope_id}] (metadata-only/inert):"]
    for binding in bindings:
        lines.append(
            f"- [{binding['id']}] {binding['asset_type']}:{binding['asset_id']}"
        )
    return "\n".join(lines)


def binding_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return BINDING_USAGE

    binding_id = _safe_int(command.args[1])
    if binding_id is None or binding_id <= 0:
        return BINDING_USAGE
    binding = runtime.store.get_default_binding(binding_id)
    if binding is None:
        return f"No default binding found: {binding_id}"
    return (
        f"Default binding [{binding['id']}] {binding['scope_type']}[{binding['scope_id']}] -> "
        f"{binding['asset_type']}:{binding['asset_id']} (metadata-only/inert)"
    )


def binding_clear(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return BINDING_USAGE

    binding_id = _safe_int(command.args[1])
    if binding_id is None or binding_id <= 0:
        return BINDING_USAGE
    binding = runtime.store.get_default_binding(binding_id)
    if binding is None:
        return f"No default binding found: {binding_id}"
    if runtime.store.clear_default_binding(binding_id):
        return f"Default binding [{binding_id}] cleared. (metadata-only/inert)"
    return f"No default binding found: {binding_id}"


def _scene_card_unavailable_message(runtime: Any) -> str:
    if runtime.store.get_card("last") is None:
        return "No card has been imported yet. Import a card first: /rp card import <file>"
    return (
        "No active Hermes Tavern session with a bound card. "
        "Use /rp start <card> to begin a fresh session."
    )


def _scene_start_card(runtime: Any, event: Any) -> dict[str, Any] | None:
    session_key = session_key_from_event(event)
    session = runtime.store.get_active_session(session_key) or runtime.store.get_paused_session(
        session_key
    )
    if not session or not session.get("card_id"):
        return None
    return runtime.store.get_card(session["card_id"])


def _project_scope(runtime: Any, event: Any) -> dict[str, int]:
    return runtime._novel_active_projects


def _project_scope_key(event: Any) -> str:
    return session_key_from_event(event)


def _project_active_id(runtime: Any, event: Any) -> int | None:
    return _project_scope(runtime, event).get(_project_scope_key(event))


def _project_set_active(runtime: Any, event: Any, project_id: int) -> None:
    _project_scope(runtime, event)[_project_scope_key(event)] = project_id


def _resolve_project_id(
    runtime: Any,
    command: RPCommand,
    event: Any,
    *,
    usage: str,
    default_ok: bool = False,
    fallback_index: int = 1,
) -> tuple[int | None, str | None]:
    if len(command.args) > fallback_index:
        project_id = _safe_int(command.args[fallback_index])
        if project_id is None:
            return None, usage
        return project_id, None
    if default_ok:
        active = _project_active_id(runtime, event)
        if active is not None:
            return active, None
    return None, usage


def project_create(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp project create <title>"
    title = " ".join(command.args[1:]).strip()
    if not title:
        return "Usage: /rp project create <title>"
    project = runtime.store.create_project(title, "")
    _project_set_active(runtime, event, project["id"])
    return f"Hermes Tavern project created: [{project['id']}] {project['title']}"


def project_list(runtime: Any) -> str:
    projects = runtime.store.list_projects()
    if not projects:
        return "No novel projects yet."
    lines = ["Hermes Tavern novel projects:"]
    for project in projects:
        lines.append(
            f"  - [{project['id']}] {project['title']} (chapters: {project['chapter_count']}, {project['status']})"
        )
    return "\n".join(lines)


def project_info(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp project info <id>"
    project_id = _safe_int(command.args[1])
    if project_id is None:
        return "Usage: /rp project info <id>"
    project = runtime.store.get_project(project_id)
    if project is None:
        return f"No novel project found: {project_id}"

    lines = [
        "Hermes Tavern project info:",
        f"id: {project['id']}",
        f"title: {project['title']}",
        f"summary: {project['summary']}",
        f"status: {project['status']}",
        f"chapters: {project.get('chapter_count', 0)}",
    ]
    try:
        brief = runtime.store.get_project_brief(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"
    if brief:
        brief_type = (brief.get("project_type") or "").strip()
        if brief_type:
            lines.append(f"project_type: {brief_type}")
        premise_text = (brief.get("premise_text") or "").strip()
        if premise_text:
            lines.append(f"premise: {_mobile_preview(premise_text, 220)}")
    try:
        outline = runtime.store.get_project_outline(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"
    outline_text = (outline.get("outline_text") or "").strip() if outline else ""
    if outline_text:
        lines.append(f"outline: {_mobile_preview(outline_text, 220)}")
    return "\n".join(lines)


def project_set(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp project set <id>",
        default_ok=False,
    )
    if project_id is None:
        return err or "Usage: /rp project set <id>"
    project = runtime.store.get_project(project_id)
    if project is None:
        return f"No novel project found: {project_id}"
    _project_set_active(runtime, event, project_id)
    return f"Active novel project set: [{project['id']}] {project['title']}"


_PROJECT_BRIEF_USAGE = (
    "Usage: /rp project brief [project-id] | /rp project brief inspect [project-id] | "
    "/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other> | "
    "/rp project brief type clear <project-id> | /rp project brief premise set <project-id> <text> | "
    "/rp project brief premise clear <project-id>"
)


def project_brief(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) == 1:
        project_id = _project_active_id(runtime, event)
        if project_id is None:
            return "No active novel project. Use /rp project set <id> or pass project-id."
        return project_brief_inspect(runtime, project_id)

    mode = command.args[1].lower()
    if mode == "inspect":
        if len(command.args) == 2:
            project_id = _project_active_id(runtime, event)
            if project_id is None:
                return "No active novel project. Use /rp project set <id> or pass project-id."
            return project_brief_inspect(runtime, project_id)
        if len(command.args) != 3:
            return _PROJECT_BRIEF_USAGE
        project_id = _safe_int(command.args[2])
        if project_id is None:
            return _PROJECT_BRIEF_USAGE
        return project_brief_inspect(runtime, project_id)

    if mode == "type":
        return project_brief_type(runtime, command)

    if mode == "premise":
        return project_brief_premise(runtime, command)

    project_id = _safe_int(mode)
    if project_id is None:
        return _PROJECT_BRIEF_USAGE
    if len(command.args) != 2:
        return _PROJECT_BRIEF_USAGE
    return project_brief_inspect(runtime, project_id)


def project_brief_inspect(runtime: Any, project_id: int) -> str:
    try:
        brief = runtime.store.get_project_brief(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if not brief:
        return f"No project brief set for project [{project_id}]."

    project_type = (brief.get("project_type") or "").strip()
    premise_text = (brief.get("premise_text") or "").strip()
    if not project_type and not premise_text:
        return f"No project brief set for project [{project_id}]."

    lines = [f"Project brief for project [{project_id}]:"]
    if project_type:
        lines.append(f"Type: {project_type}")
    if premise_text:
        lines.append(f"Premise: {_mobile_preview(premise_text, 220)}")
    return "\n".join(lines)


def project_brief_type(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 3:
        return _PROJECT_BRIEF_USAGE
    action = command.args[2].lower()
    if action == "set":
        if len(command.args) != 5:
            return _PROJECT_BRIEF_USAGE
        project_id = _safe_int(command.args[3])
        if project_id is None:
            return _PROJECT_BRIEF_USAGE
        brief_type = command.args[4].strip().lower()
        if not brief_type:
            return _PROJECT_BRIEF_USAGE
        try:
            runtime.store.set_project_brief_type(project_id, brief_type)
        except ValueError as exc:
            message = str(exc)
            if message == "Project not found":
                return f"No novel project found: {project_id}"
            if message == "Invalid project type":
                return "Invalid project type. Use novel, serial, rp, worldbuilding, or other."
            raise
        return f"Project type set for project [{project_id}]: {brief_type}"

    if action == "clear":
        if len(command.args) != 4:
            return _PROJECT_BRIEF_USAGE
        project_id = _safe_int(command.args[3])
        if project_id is None:
            return _PROJECT_BRIEF_USAGE
        try:
            runtime.store.clear_project_brief_type(project_id)
        except ValueError:
            return f"No novel project found: {project_id}"
        return f"Project type cleared for project [{project_id}]."

    return _PROJECT_BRIEF_USAGE


def project_brief_premise(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 3:
        return _PROJECT_BRIEF_USAGE
    action = command.args[2].lower()
    if action == "set":
        if len(command.args) < 5:
            return _PROJECT_BRIEF_USAGE
        project_id = _safe_int(command.args[3])
        if project_id is None:
            return _PROJECT_BRIEF_USAGE
        premise_text = " ".join(command.args[4:]).strip()
        if not premise_text:
            return _PROJECT_BRIEF_USAGE
        try:
            runtime.store.set_project_premise(project_id, premise_text)
        except ValueError:
            return f"No novel project found: {project_id}"
        return (
            f"Project premise set for project [{project_id}]: "
            f"{_mobile_preview(premise_text, 180)}"
        )

    if action == "clear":
        if len(command.args) != 4:
            return _PROJECT_BRIEF_USAGE
        project_id = _safe_int(command.args[3])
        if project_id is None:
            return _PROJECT_BRIEF_USAGE
        try:
            runtime.store.clear_project_premise(project_id)
        except ValueError:
            return f"No novel project found: {project_id}"
        return f"Project premise cleared for project [{project_id}]."

    return _PROJECT_BRIEF_USAGE


_PROJECT_OUTLINE_USAGE = (
    "Usage: /rp project outline [project-id] | /rp project outline inspect [project-id] | "
    "/rp project outline set [project-id] <text> | /rp project outline clear [project-id]"
)


def project_outline(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) == 1:
        project_id = _project_active_id(runtime, event)
        if project_id is None:
            return "No active novel project. Use /rp project set <id> or pass project-id."
        return project_outline_inspect(runtime, project_id)

    mode = command.args[1].lower()
    if mode == "inspect":
        if len(command.args) == 2:
            project_id = _project_active_id(runtime, event)
            if project_id is None:
                return "No active novel project. Use /rp project set <id> or pass project-id."
            return project_outline_inspect(runtime, project_id)
        if len(command.args) != 3:
            return _PROJECT_OUTLINE_USAGE
        project_id = _safe_int(command.args[2])
        if project_id is None:
            return _PROJECT_OUTLINE_USAGE
        return project_outline_inspect(runtime, project_id)

    if mode == "clear":
        if len(command.args) > 3:
            return _PROJECT_OUTLINE_USAGE
        if len(command.args) == 2:
            project_id = _project_active_id(runtime, event)
            if project_id is None:
                return "No active novel project. Use /rp project set <id> or pass project-id."
            return project_outline_clear(runtime, project_id)
        project_id = _safe_int(command.args[2])
        if project_id is None:
            return _PROJECT_OUTLINE_USAGE
        return project_outline_clear(runtime, project_id)

    if mode == "set":
        return project_outline_set(runtime, command, event)

    project_id = _safe_int(mode)
    if project_id is None:
        return _PROJECT_OUTLINE_USAGE
    if len(command.args) != 2:
        return _PROJECT_OUTLINE_USAGE
    return project_outline_inspect(runtime, project_id)


def project_outline_inspect(runtime: Any, project_id: int) -> str:
    try:
        outline = runtime.store.get_project_outline(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    outline_text = (outline.get("outline_text") or "").strip() if outline else ""
    if not outline_text:
        return f"No project outline set for project [{project_id}]."
    return f"Project outline for project [{project_id}]: {_mobile_preview(outline_text, 220)}"


def project_outline_set(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 3:
        return _PROJECT_OUTLINE_USAGE

    explicit_project = _safe_int(command.args[2])
    if explicit_project is None:
        project_id = _project_active_id(runtime, event)
        if project_id is None:
            return "No active novel project. Use /rp project set <id> or pass project-id."
        outline_text = " ".join(command.args[2:]).strip()
    else:
        project_id = explicit_project
        if len(command.args) < 4:
            return _PROJECT_OUTLINE_USAGE
        outline_text = " ".join(command.args[3:]).strip()

    if not outline_text:
        return _PROJECT_OUTLINE_USAGE

    try:
        runtime.store.set_project_outline(project_id, outline_text)
    except ValueError:
        return f"No novel project found: {project_id}"

    return (
        f"Project outline set for project [{project_id}]: "
        f"{_mobile_preview(outline_text, 180)}"
    )


def project_outline_clear(runtime: Any, project_id: int) -> str:
    try:
        runtime.store.clear_project_outline(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"
    return f"Project outline cleared for project [{project_id}]."


_PROJECT_STYLE_USAGE = (
    "Usage: /rp project style [project-id] | /rp project style inspect [project-id] | "
    "/rp project style set [project-id] <text> | /rp project style clear [project-id]"
)


def project_style(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        project_id = _project_active_id(runtime, event)
        if project_id is None:
            return "No active novel project. Use /rp project set <id> or pass project-id."
        return project_style_inspect(runtime, project_id)

    mode = command.args[1].lower()
    if mode == "inspect":
        if len(command.args) > 3:
            return _PROJECT_STYLE_USAGE
        if len(command.args) == 2:
            project_id = _project_active_id(runtime, event)
            if project_id is None:
                return "No active novel project. Use /rp project set <id> or pass project-id."
            return project_style_inspect(runtime, project_id)
        project_id = _safe_int(command.args[2])
        if project_id is None or len(command.args) != 3:
            return _PROJECT_STYLE_USAGE
        return project_style_inspect(runtime, project_id)

    if mode == "clear":
        if len(command.args) > 3:
            return _PROJECT_STYLE_USAGE
        if len(command.args) == 2:
            project_id = _project_active_id(runtime, event)
            if project_id is None:
                return "No active novel project. Use /rp project set <id> or pass project-id."
            return project_style_clear(runtime, project_id)
        project_id = _safe_int(command.args[2])
        if project_id is None:
            return _PROJECT_STYLE_USAGE
        return project_style_clear(runtime, project_id)

    if mode == "set":
        return project_style_set(runtime, command, event)

    project_id = _safe_int(command.args[1])
    if project_id is None:
        return _PROJECT_STYLE_USAGE
    if len(command.args) != 2:
        return _PROJECT_STYLE_USAGE
    return project_style_inspect(runtime, project_id)


def project_style_inspect(runtime: Any, project_id: int) -> str:
    try:
        style_guide = runtime.store.get_project_style_guide(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if style_guide is None:
        return f"No project style guide set for project [{project_id}]."
    return (
        f"Project style guide for project [{project_id}]: "
        f"{_mobile_preview(style_guide['style_text'] or '', 220)}"
    )


def project_style_set(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 3:
        return _PROJECT_STYLE_USAGE

    explicit_project = _safe_int(command.args[2])
    if explicit_project is None:
        project_id = _project_active_id(runtime, event)
        if project_id is None:
            return "No active novel project. Use /rp project set <id> or pass project-id."
        style_text = " ".join(command.args[2:]).strip()
    else:
        project_id = explicit_project
        if len(command.args) < 4:
            return _PROJECT_STYLE_USAGE
        style_text = " ".join(command.args[3:]).strip()

    if not style_text:
        return _PROJECT_STYLE_USAGE

    try:
        runtime.store.set_project_style_guide(project_id, style_text)
    except ValueError:
        return f"No novel project found: {project_id}"

    return (
        f"Project style guide set for project [{project_id}]: "
        f"{_mobile_preview(style_text, 180)}"
    )


def project_style_clear(runtime: Any, project_id: int) -> str:
    try:
        runtime.store.clear_project_style_guide(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"
    return f"Project style guide cleared for project [{project_id}]."


def project_export(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp project export [id]",
        default_ok=True,
    )
    if project_id is None:
        return err or "Usage: /rp project export [id]"

    try:
        markdown = runtime.store.export_project_markdown(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    export_dir = get_hermes_home() / "plugins" / "hermes-tavern" / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = Path(export_dir) / f"project_{project_id}.md"
    export_path.write_text(markdown, encoding="utf-8")
    return f"Project exported as Markdown.\nfile: {export_path}\nMEDIA:\"{export_path}\""


def chapter_create(runtime: Any, command: RPCommand, event: Any) -> str:
    explicit_project_id = _safe_int(command.args[1]) if len(command.args) > 1 else None
    if explicit_project_id is not None and len(command.args) > 2:
        project_id = explicit_project_id
        title = " ".join(command.args[2:]).strip()
    else:
        project_id = _project_active_id(runtime, event)
        title = " ".join(command.args[1:]).strip()
    if not title:
        return "Usage: /rp chapter create [project-id] <title>"
    if project_id is None:
        return "No active novel project. Use /rp project set <id> or pass project-id."
    try:
        chapter = runtime.store.create_chapter(project_id, title)
    except ValueError:
        return f"No novel project found: {project_id}"
    _project_set_active(runtime, event, project_id)
    return (
        f"Hermes Tavern chapter created: [{chapter['id']}] {chapter['title']} "
        f"(Chapter {chapter['chapter_number']})"
    )


def chapter_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp chapter list [project-id]",
        default_ok=True,
        fallback_index=1,
    )
    if project_id is None:
        return err or "Usage: /rp chapter list [project-id]"
    try:
        chapters = runtime.store.list_chapters(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"
    if not chapters:
        return f"No chapters for novel project [{project_id}] yet."
    lines = [f"Hermes Tavern chapters for project [{project_id}]:"]
    for chapter in chapters:
        lines.append(
            f"  - [{chapter['id']}] Chapter {chapter['chapter_number']}: {chapter['title']} ({chapter['status']})"
        )
    return "\n".join(lines)


def chapter_summary(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    usage = (
        "Usage: /rp chapter summary <chapter-id> [text] | /rp chapter summary clear <chapter-id>"
    )
    if len(command.args) < 2:
        return usage

    mode = command.args[1].lower()
    if mode == "clear":
        if len(command.args) != 3:
            return usage
        chapter_id = _safe_int(command.args[2])
        if chapter_id is None:
            return usage
        try:
            runtime.store.clear_chapter_summary(chapter_id)
        except ValueError:
            return f"No novel chapter found: {chapter_id}"
        return f"Chapter summary cleared for chapter [{chapter_id}]."

    chapter_id = _safe_int(mode)
    if chapter_id is None:
        return usage

    if len(command.args) == 2:
        try:
            summary = runtime.store.get_chapter_summary(chapter_id)
        except ValueError:
            return f"No novel chapter found: {chapter_id}"
        if summary is None:
            return f"Chapter [{chapter_id}] summary: (not set)"
        return (
            f"Chapter [{chapter_id}] summary: "
            f"{_mobile_preview((summary['summary'] or '').strip(), 220)}"
        )

    text = " ".join(command.args[2:]).strip()
    if not text:
        return usage
    try:
        runtime.store.set_chapter_summary(chapter_id, text)
    except ValueError:
        return f"No novel chapter found: {chapter_id}"
    return (
        f"Chapter summary set for chapter [{chapter_id}]: "
        f"{_mobile_preview(text, 180)}"
    )


def scene_create(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 3:
        return "Usage: /rp scene create <chapter-id> <title>"
    chapter_id = _safe_int(command.args[1])
    if chapter_id is None:
        return "Usage: /rp scene create <chapter-id> <title>"
    title = " ".join(command.args[2:]).strip()
    if not title:
        return "Usage: /rp scene create <chapter-id> <title>"
    try:
        scene = runtime.store.create_scene(chapter_id, title)
    except ValueError:
        return f"No novel chapter found: {chapter_id}"
    return f"Hermes Tavern scene created: [{scene['id']}] {scene['title']} (scene {scene['scene_number']})"


def scene_list(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 2:
        return "Usage: /rp scene list <chapter-id>"
    chapter_id = _safe_int(command.args[1])
    if chapter_id is None:
        return "Usage: /rp scene list <chapter-id>"
    try:
        scenes = runtime.store.list_scenes(chapter_id)
    except ValueError:
        return f"No novel chapter found: {chapter_id}"
    if not scenes:
        return f"No scenes for chapter [{chapter_id}] yet."
    lines = [f"Hermes Tavern scenes for chapter [{chapter_id}]:"]
    for scene in scenes:
        session_hint = " (no session linked)" if not scene["session_id"] else ""
        lines.append(
            f"  - [{scene['id']}] Scene {scene['scene_number']}: {scene['title']} ({scene['status']}){session_hint}"
        )
    return "\n".join(lines)


def scene_summary(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    usage = (
        "Usage: /rp scene summary <scene-id> [text] | /rp scene summary clear <scene-id>"
    )
    if len(command.args) < 2:
        return usage

    mode = command.args[1].lower()
    if mode == "clear":
        if len(command.args) != 3:
            return usage
        scene_id = _safe_int(command.args[2])
        if scene_id is None:
            return usage
        try:
            runtime.store.clear_scene_summary(scene_id)
        except ValueError:
            return f"No novel scene found: {scene_id}"
        return f"Scene summary cleared for scene [{scene_id}]."

    scene_id = _safe_int(mode)
    if scene_id is None:
        return usage

    if len(command.args) == 2:
        try:
            summary = runtime.store.get_scene_summary(scene_id)
        except ValueError:
            return f"No novel scene found: {scene_id}"
        if summary is None:
            return f"Scene [{scene_id}] summary: (not set)"
        return (
            f"Scene [{scene_id}] summary: "
            f"{_mobile_preview((summary['summary'] or '').strip(), 220)}"
        )

    text = " ".join(command.args[2:]).strip()
    if not text:
        return usage
    try:
        runtime.store.set_scene_summary(scene_id, text)
    except ValueError:
        return f"No novel scene found: {scene_id}"
    return (
        f"Scene summary set for scene [{scene_id}]: "
        f"{_mobile_preview(text, 180)}"
    )


def scene_start(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 2:
        return "Usage: /rp scene start <scene-id>"
    scene_id = _safe_int(command.args[1])
    if scene_id is None:
        return "Usage: /rp scene start <scene-id>"
    scene = runtime.store.get_scene(scene_id)
    if scene is None:
        return f"No novel scene found: {scene_id}"
    card = _scene_start_card(runtime, event)
    if card is None:
        return _scene_card_unavailable_message(runtime)
    start = runtime_lifecycle.start(
        runtime,
        RPCommand("start", [card["id"]], f"/rp start {card['id']}"),
        event,
    )
    session = runtime.store.get_active_session(session_key_from_event(event))
    if session is None:
        return "Failed to start or locate active RP session."
    runtime.store.link_scene_session(scene_id, session["id"])
    return start


def scene_goal(runtime: Any, command: RPCommand) -> str:
    usage = (
        "Usage: /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id>"
    )
    if len(command.args) < 2:
        return usage

    mode = command.args[1].lower()
    if mode == "clear":
        if len(command.args) != 3:
            return usage
        scene_id = _safe_int(command.args[2])
        if scene_id is None:
            return usage
        try:
            runtime.store.clear_scene_goal(scene_id)
        except ValueError:
            return f"No novel scene found: {scene_id}"
        return f"Scene goal cleared for scene [{scene_id}]."

    if len(command.args) < 2:
        return usage
    scene_id = _safe_int(command.args[1])
    if scene_id is None:
        return usage

    if len(command.args) == 2:
        try:
            goal = runtime.store.get_scene_goal(scene_id)
        except ValueError:
            return f"No novel scene found: {scene_id}"
        if goal is None:
            return f"No scene goal set for scene [{scene_id}]."
        return f"Scene [{scene_id}] goal: {_mobile_preview(goal['goal_text'], 220)}"

    text = " ".join(command.args[2:])
    if not text.strip():
        return usage
    try:
        runtime.store.set_scene_goal(scene_id, text)
    except ValueError:
        return f"No novel scene found: {scene_id}"
    return f"Scene goal set for scene [{scene_id}]: {_mobile_preview(text, 180)}"


def scene_beat(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    usage = (
        "Usage: /rp scene beat add <scene-id> <label> <beat...> | /rp scene beat list <scene-id> | "
        "/rp scene beat inspect <beat-id> | /rp scene beat update <beat-id> <beat...> | "
        "/rp scene beat delete <beat-id>"
    )
    if len(command.args) < 2:
        return usage

    subcommand = command.args[1].lower()
    if subcommand == "add":
        if len(command.args) < 5:
            return usage
        scene_id = _safe_int(command.args[2])
        if scene_id is None:
            return usage
        label = command.args[3].strip()
        beat_text = " ".join(command.args[4:]).strip()
        try:
            beat = runtime.store.create_scene_beat(
                scene_id,
                label,
                beat_text,
            )
        except ValueError as exc:
            message = str(exc)
            if message == "Scene not found":
                return f"No novel scene found: {scene_id}"
            if message == "Scene beat label cannot be blank":
                return "Scene beat label cannot be blank"
            if message == "Scene beat text cannot be blank":
                return "Scene beat text cannot be blank"
            raise
        return (
            f"Scene beat added: [{beat['id']}] {beat['label']} -> "
            f"{_mobile_preview(beat['beat_text'], 180)}"
        )

    if subcommand == "list":
        if len(command.args) != 3:
            return usage
        scene_id = _safe_int(command.args[2])
        if scene_id is None:
            return usage
        try:
            beats = runtime.store.list_scene_beats(scene_id)
        except ValueError as exc:
            if str(exc) == "Scene not found":
                return f"No novel scene found: {scene_id}"
            raise
        if not beats:
            return f"No scene beats for scene [{scene_id}]."
        lines = [f"Hermes Tavern scene beats for scene [{scene_id}]:"]
        for beat in beats:
            lines.append(
                f"  - [{beat['id']}] {beat['label']}: {_mobile_preview(beat['beat_text'], 140)}"
            )
        return "\n".join(lines)

    if subcommand == "inspect":
        if len(command.args) != 3:
            return usage
        beat_id = _safe_int(command.args[2])
        if beat_id is None:
            return usage
        beat = runtime.store.get_scene_beat(beat_id)
        if beat is None:
            return f"No scene beat found: {beat_id}"
        return (
            f"Scene beat for [{beat['id']}] (scene [{beat['scene_id']}]): "
            f"{beat['label']}: {_mobile_preview(beat['beat_text'], 220)}"
        )

    if subcommand == "update":
        if len(command.args) < 4:
            return usage
        beat_id = _safe_int(command.args[2])
        if beat_id is None:
            return usage
        beat_text = " ".join(command.args[3:]).strip()
        if not beat_text:
            return usage
        beat = runtime.store.update_scene_beat(beat_id, beat_text)
        if beat is None:
            return f"No scene beat found: {beat_id}"
        return (
            f"Scene beat updated for scene beat [{beat_id}]: "
            f"{_mobile_preview(beat['beat_text'], 180)}"
        )

    if subcommand == "delete":
        if len(command.args) != 3:
            return usage
        beat_id = _safe_int(command.args[2])
        if beat_id is None:
            return usage
        if not runtime.store.delete_scene_beat(beat_id):
            return f"No scene beat found: {beat_id}"
        return f"Scene beat deleted for scene beat [{beat_id}]."

    return usage


def scene_narration(runtime: Any, command: RPCommand) -> str:
    usage = (
        "Usage: /rp scene narration <scene-id> | /rp scene narration clear <scene-id> | "
        "/rp scene narration pov <scene-id> <label> | /rp scene narration tense <scene-id> <past|present>"
    )
    if len(command.args) < 2:
        return usage

    mode = command.args[1].lower()
    if mode == "clear":
        if len(command.args) != 3:
            return usage
        scene_id = _safe_int(command.args[2])
        if scene_id is None:
            return usage
        try:
            runtime.store.clear_scene_narration_controls(scene_id)
        except ValueError as exc:
            if str(exc) == "Scene not found":
                return f"No novel scene found: {scene_id}"
            raise
        return f"Scene narration controls cleared for scene [{scene_id}]."

    if mode == "pov":
        if len(command.args) < 4:
            return usage
        scene_id = _safe_int(command.args[2])
        if scene_id is None:
            return usage
        label = " ".join(command.args[3:]).strip()
        if not label:
            return usage
        try:
            runtime.store.set_scene_narration_controls(scene_id, pov_label=label)
        except ValueError as exc:
            if str(exc) == "Scene not found":
                return f"No novel scene found: {scene_id}"
            raise
        return f"Scene narration POV set for scene [{scene_id}]: {_mobile_preview(label, 180)}"

    if mode == "tense":
        if len(command.args) != 4:
            return usage
        scene_id = _safe_int(command.args[2])
        if scene_id is None:
            return usage
        tense = command.args[3].strip().lower()
        try:
            runtime.store.set_scene_narration_controls(scene_id, tense=tense)
        except ValueError as exc:
            message = str(exc)
            if message == "Scene not found":
                return f"No novel scene found: {scene_id}"
            if message == "Invalid tense":
                return "Invalid tense. Use past or present."
            raise
        return f"Scene narration tense set for scene [{scene_id}]: {tense}"

    if len(command.args) != 2:
        return usage
    scene_id = _safe_int(command.args[1])
    if scene_id is None:
        return usage
    try:
        controls = runtime.store.get_scene_narration_controls(scene_id)
    except ValueError as exc:
        if str(exc) == "Scene not found":
            return f"No novel scene found: {scene_id}"
        raise
    if not controls:
        return f"No scene narration controls set for scene [{scene_id}]."
    pov = controls.get("pov_label") or "(not set)"
    tense = controls.get("tense") or "(not set)"
    return "\n".join(
        [
            f"Scene narration controls for scene [{scene_id}]:",
            f"POV: {pov}",
            f"Tense: {tense}",
        ]
    )


def canon_add(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    if len(command.args) < 4:
        return "Usage: /rp canon add <project-id> <title> <content...> [--group <group>]"
    project_id = _safe_int(command.args[1])
    if project_id is None:
        return "Usage: /rp canon add <project-id> <title> <content...> [--group <group>]"
    title = command.args[2].strip()
    if not title:
        return "Usage: /rp canon add <project-id> <title> <content...> [--group <group>]"
    content_args = list(command.args[3:])
    group = "general"
    if "--group" in content_args:
        group_index = content_args.index("--group")
        if group_index + 1 >= len(content_args):
            return "Usage: /rp canon add <project-id> <title> <content...> [--group <group>]"
        group = content_args[group_index + 1]
        content_args = content_args[:group_index]
    content = " ".join(content_args).strip()
    if not content:
        return "Usage: /rp canon add <project-id> <title> <content...> [--group <group>]"
    try:
        canon = runtime.store.create_canon(project_id, title, content, group=group)
    except ValueError:
        return f"No novel project found: {project_id}"
    return f"Hermes Tavern canon added: [{canon['id']}] {canon['title']} ({canon['canon_group']})"


def canon_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id: int | None = None
    group = None
    if len(command.args) > 1:
        maybe_project_id = _safe_int(command.args[1])
        if maybe_project_id is not None:
            project_id = maybe_project_id
            if len(command.args) > 2:
                group = command.args[2]
        else:
            project_id = _project_active_id(runtime, event)
            group = command.args[1]
    else:
        project_id = _project_active_id(runtime, event)
    if project_id is None:
        return "Usage: /rp canon list [project-id] [group]"
    try:
        canon = runtime.store.list_canon(project_id, group=group)
    except ValueError:
        return f"No novel project found: {project_id}"
    if not canon:
        group_label = f" in group '{group}'" if group else ""
        return f"No canon entries for project [{project_id}]{group_label}."
    lines = [f"Hermes Tavern canon for project [{project_id}]:"]
    for entry in canon:
        preview = _mobile_preview(entry.get("content") or "", 80)
        lines.append(f"  - [{entry['id']}] {entry['title']} ({entry['canon_group']}): {preview}")
    return "\n".join(lines)


def canon_group(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id: int | None = _safe_int(command.args[1]) if len(command.args) > 1 else None
    group = None
    if project_id is not None:
        if len(command.args) < 3:
            return "Usage: /rp canon group [project-id] <group>"
        group = command.args[2]
    else:
        project_id = _project_active_id(runtime, event)
        if project_id is None or len(command.args) < 2:
            return "Usage: /rp canon group [project-id] <group>"
        group = command.args[1]
    try:
        entries = runtime.store.list_canon(project_id, group=group)
    except ValueError:
        return f"No novel project found: {project_id}"
    if not entries:
        return f"No canon entries for project [{project_id}] in group '{group}'."
    lines = [f"Hermes Tavern canon group '{group}' for project [{project_id}]:"]
    for entry in entries:
        preview = _mobile_preview(entry.get("content") or "", 80)
        lines.append(f"  - [{entry['id']}] {entry['title']}: {preview}")
    return "\n".join(lines)


def timeline_add(runtime: Any, command: RPCommand, event: Any) -> str:
    if len(command.args) < 4:
        return "Usage: /rp timeline add <project-id> <date> <title> [description...]"
    project_id = _safe_int(command.args[1])
    if project_id is None:
        return "Usage: /rp timeline add <project-id> <date> <title> [description...]"
    event_date = command.args[2].strip()
    if not event_date:
        return "Usage: /rp timeline add <project-id> <date> <title> [description...]"
    title = command.args[3].strip()
    if not title:
        return "Usage: /rp timeline add <project-id> <date> <title> [description...]"
    description = " ".join(command.args[4:]).strip()
    try:
        timeline_event = runtime.store.create_timeline_event(
            project_id,
            event_date,
            title,
            description,
        )
    except ValueError:
        return f"No novel project found: {project_id}"
    return (
        f"Hermes Tavern timeline event added: [{timeline_event['id']}] "
        f"{timeline_event['event_date']} — {timeline_event['title']}"
    )


def timeline_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp timeline list [project-id]",
        default_ok=True,
        fallback_index=1,
    )
    if project_id is None:
        return err or "Usage: /rp timeline list [project-id]"
    try:
        timeline = runtime.store.list_timeline(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"
    if not timeline:
        return f"No timeline events for project [{project_id}] yet."
    lines = [f"Hermes Tavern timeline for project [{project_id}]:"]
    for entry in timeline:
        description = entry.get("description") or ""
        suffix = f" — {description}" if description else ""
        lines.append(f"  - [{entry['sort_key'] or entry['event_date']}] {entry['title']}{suffix}")
    return "\n".join(lines)


def relationship_add(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    if len(command.args) < 4:
        return _RELATIONSHIP_USAGE

    project_id = _safe_int(command.args[1])
    if project_id is None:
        return _RELATIONSHIP_USAGE

    label = command.args[2].strip()
    if not label:
        return _RELATIONSHIP_USAGE

    state_text = " ".join(command.args[3:]).strip()
    if not state_text:
        return _RELATIONSHIP_USAGE

    try:
        relationship = runtime.store.create_relationship_state(
            project_id,
            label,
            state_text,
        )
    except ValueError:
        return f"No novel project found: {project_id}"

    return (
        f"Relationship state added: [{relationship['id']}] {relationship['label']} -> "
        f"{_mobile_preview(relationship['state_text'], 180)}"
    )


def relationship_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp relationship list [project-id]",
        default_ok=True,
        fallback_index=1,
    )
    if project_id is None:
        return err or _RELATIONSHIP_USAGE

    try:
        relationships = runtime.store.list_relationship_states(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if not relationships:
        return f"No relationship states for project [{project_id}]."

    lines = [f"Hermes Tavern relationships for project [{project_id}]:"]
    for relationship in relationships:
        lines.append(
            f"  - [{relationship['id']}] {relationship['label']}: "
            f"{_mobile_preview(relationship['state_text'], 120)}"
        )
    return "\n".join(lines)


def relationship_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return _RELATIONSHIP_USAGE

    relationship_id = _safe_int(command.args[1])
    if relationship_id is None:
        return _RELATIONSHIP_USAGE

    relationship = runtime.store.get_relationship_state(relationship_id)
    if relationship is None:
        return f"No relationship state found: {relationship_id}"

    return (
        f"Relationship state for [{relationship_id}] (project [{relationship['project_id']}]): "
        f"{relationship['label']}: {_mobile_preview(relationship['state_text'], 220)}"
    )


def relationship_update(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 3:
        return _RELATIONSHIP_USAGE

    relationship_id = _safe_int(command.args[1])
    if relationship_id is None:
        return _RELATIONSHIP_USAGE

    state_text = " ".join(command.args[2:]).strip()
    if not state_text:
        return _RELATIONSHIP_USAGE

    try:
        relationship = runtime.store.update_relationship_state(relationship_id, state_text)
    except ValueError:
        return f"No relationship state found: {relationship_id}"

    return (
        f"Relationship state updated for relationship [{relationship['id']}]: "
        f"{_mobile_preview(relationship['state_text'], 180)}"
    )


def relationship_delete(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return _RELATIONSHIP_USAGE

    relationship_id = _safe_int(command.args[1])
    if relationship_id is None:
        return _RELATIONSHIP_USAGE

    if not runtime.store.delete_relationship_state(relationship_id):
        return f"No relationship state found: {relationship_id}"

    return f"Relationship state deleted for relationship [{relationship_id}]."


def location_add(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    if len(command.args) < 4:
        return _LOCATION_USAGE

    project_id = _safe_int(command.args[1])
    if project_id is None:
        return _LOCATION_USAGE

    label = command.args[2].strip()
    if not label:
        return _LOCATION_USAGE

    description_text = " ".join(command.args[3:]).strip()
    if not description_text:
        return _LOCATION_USAGE

    try:
        location = runtime.store.create_location(
            project_id,
            label,
            description_text,
        )
    except ValueError:
        return f"No novel project found: {project_id}"

    return (
        f"Location added: [{location['id']}] {location['label']} -> "
        f"{_mobile_preview(location['description_text'], 180)}"
    )


def location_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp location list [project-id]",
        default_ok=True,
        fallback_index=1,
    )
    if project_id is None:
        return err or _LOCATION_USAGE

    try:
        locations = runtime.store.list_locations(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if not locations:
        return f"No locations for project {project_id}."

    lines = [f"Hermes Tavern locations for project [{project_id}]:"]
    for location in locations:
        lines.append(
            f"  - [{location['id']}] {location['label']}: "
            f"{_mobile_preview(location['description_text'], 120)}"
        )
    return "\n".join(lines)


def location_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return _LOCATION_USAGE

    location_id = _safe_int(command.args[1])
    if location_id is None:
        return _LOCATION_USAGE

    location = runtime.store.get_location(location_id)
    if location is None:
        return f"No location found: {location_id}"

    return (
        f"Location for [{location_id}] (project [{location['project_id']}]): "
        f"{location['label']}: {_mobile_preview(location['description_text'], 220)}"
    )


def location_update(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 3:
        return _LOCATION_USAGE

    location_id = _safe_int(command.args[1])
    if location_id is None:
        return _LOCATION_USAGE

    description_text = " ".join(command.args[2:]).strip()
    if not description_text:
        return _LOCATION_USAGE

    try:
        location = runtime.store.update_location(location_id, description_text)
    except ValueError:
        return f"No location found: {location_id}"

    return (
        f"Location updated for location [{location['id']}]: "
        f"{_mobile_preview(location['description_text'], 180)}"
    )


def location_delete(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return _LOCATION_USAGE

    location_id = _safe_int(command.args[1])
    if location_id is None:
        return _LOCATION_USAGE

    if not runtime.store.delete_location(location_id):
        return f"No location found: {location_id}"

    return f"Location deleted for location [{location_id}]."


def organization_add(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    if len(command.args) < 4:
        return _ORGANIZATION_USAGE

    project_id = _safe_int(command.args[1])
    if project_id is None:
        return _ORGANIZATION_USAGE

    label = command.args[2].strip()
    if not label:
        return _ORGANIZATION_USAGE

    description_text = " ".join(command.args[3:]).strip()
    if not description_text:
        return _ORGANIZATION_USAGE

    try:
        organization = runtime.store.create_organization(
            project_id,
            label,
            description_text,
        )
    except ValueError:
        return f"No novel project found: {project_id}"

    return (
        f"Organization added: [{organization['id']}] {organization['label']} -> "
        f"{_mobile_preview(organization['description_text'], 180)}"
    )


def organization_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp organization list [project-id]",
        default_ok=True,
        fallback_index=1,
    )
    if project_id is None:
        return err or _ORGANIZATION_USAGE

    try:
        organizations = runtime.store.list_organizations(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if not organizations:
        return f"No organizations for project {project_id}."

    lines = [f"Hermes Tavern organizations for project [{project_id}]:"]
    for organization in organizations:
        lines.append(
            f"  - [{organization['id']}] {organization['label']}: "
            f"{_mobile_preview(organization['description_text'], 120)}"
        )
    return "\n".join(lines)


def organization_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return _ORGANIZATION_USAGE

    organization_id = _safe_int(command.args[1])
    if organization_id is None:
        return _ORGANIZATION_USAGE

    organization = runtime.store.get_organization(organization_id)
    if organization is None:
        return f"No organization found: {organization_id}"

    return (
        f"Organization for [{organization_id}] (project [{organization['project_id']}]): "
        f"{organization['label']}: {_mobile_preview(organization['description_text'], 220)}"
    )


def organization_update(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 3:
        return _ORGANIZATION_USAGE

    organization_id = _safe_int(command.args[1])
    if organization_id is None:
        return _ORGANIZATION_USAGE

    description_text = " ".join(command.args[2:]).strip()
    if not description_text:
        return _ORGANIZATION_USAGE

    try:
        organization = runtime.store.update_organization(
            organization_id,
            description_text,
        )
    except ValueError:
        return f"No organization found: {organization_id}"

    return (
        f"Organization updated for organization [{organization['id']}]: "
        f"{_mobile_preview(organization['description_text'], 180)}"
    )


def organization_delete(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return _ORGANIZATION_USAGE

    organization_id = _safe_int(command.args[1])
    if organization_id is None:
        return _ORGANIZATION_USAGE

    if not runtime.store.delete_organization(organization_id):
        return f"No organization found: {organization_id}"

    return f"Organization deleted for organization [{organization_id}]."


def plot_thread_add(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    if len(command.args) < 5:
        return _PLOT_THREAD_USAGE

    project_id = _safe_int(command.args[2])
    if project_id is None:
        return _PLOT_THREAD_USAGE

    label = command.args[3].strip()
    if not label:
        return _PLOT_THREAD_USAGE

    description_text = " ".join(command.args[4:]).strip()
    if not description_text:
        return _PLOT_THREAD_USAGE

    try:
        plot_thread = runtime.store.create_plot_thread(
            project_id,
            label,
            description_text,
        )
    except ValueError:
        return f"No novel project found: {project_id}"

    return (
        f"Plot thread added: [{plot_thread['id']}] {plot_thread['label']} -> "
        f"{_mobile_preview(plot_thread['description_text'], 180)}"
    )


def plot_thread_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp plot thread list [project-id]",
        default_ok=True,
        fallback_index=2,
    )
    if project_id is None:
        return err or _PLOT_THREAD_USAGE

    try:
        plot_threads = runtime.store.list_plot_threads(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if not plot_threads:
        return f"No plot threads for project {project_id}."

    lines = [f"Hermes Tavern plot threads for project [{project_id}]:"]
    for plot_thread in plot_threads:
        lines.append(
            f"  - [{plot_thread['id']}] {plot_thread['label']}: "
            f"{_mobile_preview(plot_thread['description_text'], 120)}"
        )
    return "\n".join(lines)


def plot_thread_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 3:
        return _PLOT_THREAD_USAGE

    plot_thread_id = _safe_int(command.args[2])
    if plot_thread_id is None:
        return _PLOT_THREAD_USAGE

    plot_thread = runtime.store.get_plot_thread(plot_thread_id)
    if plot_thread is None:
        return f"No plot thread found: {plot_thread_id}"

    return (
        f"Plot thread for [{plot_thread_id}] (project [{plot_thread['project_id']}]): "
        f"{plot_thread['label']}: {_mobile_preview(plot_thread['description_text'], 220)}"
    )


def plot_thread_update(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 4:
        return _PLOT_THREAD_USAGE

    plot_thread_id = _safe_int(command.args[2])
    if plot_thread_id is None:
        return _PLOT_THREAD_USAGE

    description_text = " ".join(command.args[3:]).strip()
    if not description_text:
        return _PLOT_THREAD_USAGE

    try:
        plot_thread = runtime.store.update_plot_thread(
            plot_thread_id,
            description_text,
        )
    except ValueError:
        return f"No plot thread found: {plot_thread_id}"

    return (
        f"Plot thread updated for plot thread [{plot_thread['id']}]: "
        f"{_mobile_preview(plot_thread['description_text'], 180)}"
    )


def plot_thread_delete(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 3:
        return _PLOT_THREAD_USAGE

    plot_thread_id = _safe_int(command.args[2])
    if plot_thread_id is None:
        return _PLOT_THREAD_USAGE

    if not runtime.store.delete_plot_thread(plot_thread_id):
        return f"No plot thread found: {plot_thread_id}"

    return f"Plot thread deleted for plot thread [{plot_thread_id}]."


def style_sample_add(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    if len(command.args) < 5:
        return _STYLE_SAMPLE_USAGE

    project_id = _safe_int(command.args[2])
    if project_id is None:
        return _STYLE_SAMPLE_USAGE

    label = command.args[3].strip()
    if not label:
        return _STYLE_SAMPLE_USAGE

    sample_text = " ".join(command.args[4:]).strip()
    if not sample_text:
        return _STYLE_SAMPLE_USAGE

    try:
        style_sample = runtime.store.create_style_sample(project_id, label, sample_text)
    except ValueError:
        return f"No novel project found: {project_id}"

    return (
        f"Style sample added: [{style_sample['id']}] {style_sample['label']} -> "
        f"{_mobile_preview(style_sample['sample_text'], 180)}"
    )


def style_sample_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp style sample list [project-id]",
        default_ok=True,
        fallback_index=2,
    )
    if project_id is None:
        return err or _STYLE_SAMPLE_USAGE

    try:
        style_samples = runtime.store.list_style_samples(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if not style_samples:
        return f"No style samples for project [{project_id}]."

    lines = [f"Hermes Tavern style samples for project [{project_id}]:"]
    for sample in style_samples:
        lines.append(
            f"  - [{sample['id']}] {sample['label']}: "
            f"{_mobile_preview(sample['sample_text'], 120)}"
        )
    return "\n".join(lines)


def style_sample_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 3:
        return _STYLE_SAMPLE_USAGE

    style_sample_id = _safe_int(command.args[2])
    if style_sample_id is None:
        return _STYLE_SAMPLE_USAGE

    style_sample = runtime.store.get_style_sample(style_sample_id)
    if style_sample is None:
        return f"No style sample found: {style_sample_id}"

    return (
        f"Style sample for [{style_sample_id}] (project [{style_sample['project_id']}]): "
        f"{style_sample['label']}: {_mobile_preview(style_sample['sample_text'], 220)}"
    )


def style_sample_update(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 4:
        return _STYLE_SAMPLE_USAGE

    style_sample_id = _safe_int(command.args[2])
    if style_sample_id is None:
        return _STYLE_SAMPLE_USAGE

    sample_text = " ".join(command.args[3:]).strip()
    if not sample_text:
        return _STYLE_SAMPLE_USAGE

    style_sample = runtime.store.update_style_sample(style_sample_id, sample_text)
    if style_sample is None:
        return f"No style sample found: {style_sample_id}"

    return (
        f"Style sample updated for style sample [{style_sample_id}]: "
        f"{_mobile_preview(style_sample['sample_text'], 180)}"
    )


def style_sample_delete(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 3:
        return _STYLE_SAMPLE_USAGE

    style_sample_id = _safe_int(command.args[2])
    if style_sample_id is None:
        return _STYLE_SAMPLE_USAGE

    if not runtime.store.delete_style_sample(style_sample_id):
        return f"No style sample found: {style_sample_id}"

    return f"Style sample deleted for style sample [{style_sample_id}]."


def character_state_add(runtime: Any, command: RPCommand, event: Any) -> str:
    del event
    if len(command.args) < 5:
        return _CHARACTER_USAGE

    project_id = _safe_int(command.args[2])
    if project_id is None:
        return _CHARACTER_USAGE

    label = command.args[3].strip()
    if not label:
        return _CHARACTER_USAGE

    state_text = " ".join(command.args[4:]).strip()
    if not state_text:
        return _CHARACTER_USAGE

    try:
        character_state = runtime.store.create_character_state(
            project_id,
            label,
            state_text,
        )
    except ValueError as exc:
        if str(exc) == "Project not found":
            return f"No novel project found: {project_id}"
        return _CHARACTER_USAGE

    return (
        f"Character state added: [{character_state['id']}] {character_state['label']} -> "
        f"{_mobile_preview(character_state['state_text'], 180)}"
    )


def character_state_list(runtime: Any, command: RPCommand, event: Any) -> str:
    project_id, err = _resolve_project_id(
        runtime,
        command,
        event=event,
        usage="Usage: /rp character state list [project-id]",
        default_ok=True,
        fallback_index=2,
    )
    if project_id is None:
        return err or _CHARACTER_USAGE

    try:
        character_states = runtime.store.list_character_states(project_id)
    except ValueError:
        return f"No novel project found: {project_id}"

    if not character_states:
        return f"No character states for project [{project_id}]."

    lines = [f"Hermes Tavern characters for project [{project_id}]:"]
    for character_state in character_states:
        lines.append(
            f"  - [{character_state['id']}] {character_state['label']}: "
            f"{_mobile_preview(character_state['state_text'], 120)}"
        )
    return "\n".join(lines)


def character_state_inspect(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 3:
        return _CHARACTER_USAGE

    character_state_id = _safe_int(command.args[2])
    if character_state_id is None:
        return _CHARACTER_USAGE

    character_state = runtime.store.get_character_state(character_state_id)
    if character_state is None:
        return f"No character state found: {character_state_id}"

    return (
        f"Character state for [{character_state_id}] (project [{character_state['project_id']}]): "
        f"{character_state['label']}: {_mobile_preview(character_state['state_text'], 220)}"
    )


def character_state_update(runtime: Any, command: RPCommand) -> str:
    if len(command.args) < 4:
        return _CHARACTER_USAGE

    character_state_id = _safe_int(command.args[2])
    if character_state_id is None:
        return _CHARACTER_USAGE

    state_text = " ".join(command.args[3:]).strip()
    if not state_text:
        return _CHARACTER_USAGE

    try:
        character_state = runtime.store.update_character_state(
            character_state_id,
            state_text,
        )
    except ValueError:
        return f"No character state found: {character_state_id}"

    return (
        f"Character state updated for character [{character_state['id']}]: "
        f"{_mobile_preview(character_state['state_text'], 180)}"
    )


def character_state_delete(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 3:
        return _CHARACTER_USAGE

    character_state_id = _safe_int(command.args[2])
    if character_state_id is None:
        return _CHARACTER_USAGE

    if not runtime.store.delete_character_state(character_state_id):
        return f"No character state found: {character_state_id}"

    return f"Character state deleted for character [{character_state_id}]."
