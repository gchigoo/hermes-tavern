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
        "/rp project brief premise clear <project-id>"
    )


def chapter_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "create":
        return chapter_create(runtime, command, event)
    if subcommand == "list":
        return chapter_list(runtime, command, event)
    return "Usage: /rp chapter create [project-id] <title> | /rp chapter list [project-id]"


def scene_command(runtime: Any, command: RPCommand, event: Any) -> str:
    subcommand = command.args[0].lower() if command.args else "list"
    if subcommand == "create":
        return scene_create(runtime, command, event)
    if subcommand == "list":
        return scene_list(runtime, command)
    if subcommand == "start":
        return scene_start(runtime, command, event)
    if subcommand == "goal":
        return scene_goal(runtime, command)
    if subcommand == "narration":
        return scene_narration(runtime, command)
    return (
        "Usage: /rp scene create <chapter-id> <title> | /rp scene list <chapter-id> | "
        "/rp scene start <scene-id> | /rp scene goal <scene-id> [text] | /rp scene goal clear <scene-id> | "
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


def _safe_int(text: str) -> int | None:
    try:
        return int(text)
    except (TypeError, ValueError):
        return None


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
