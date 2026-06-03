"""Prompt-module assembly helpers for Hermes Tavern runtime."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from hermes_tavern.lorebook import match_lorebook_entries, modules_from_lore_matches
from hermes_tavern.memory import (
    TavernMemoryContext,
    TavernMemoryFact,
    build_memory_modules,
)
from hermes_tavern.prompt import PromptModule


def session_preset_modules(runtime, session: dict[str, Any]) -> list[PromptModule]:
    preset_id = session.get("preset_id")
    if not preset_id:
        return []
    content_mode = session.get("content_mode") or "safe"
    modules: list[PromptModule] = []
    for row in runtime.store.list_prompt_modules(preset_id):
        if not row.get("enabled"):
            continue
        raw = json.loads(row.get("raw_json") or "{}")
        risk = raw.get("risk_level", "safe")
        if risk == "adult_fiction" and content_mode != "adult-fiction":
            continue
        if risk not in {"safe", "adult_fiction"}:
            continue
        modules.append(
            PromptModule(
                name=f"preset:{row['name']}",
                role=row.get("role") or "system",
                content=row.get("content") or "",
                position=row.get("position") or "before_char",
                insertion_order=int(row.get("insertion_order") or 0),
                enabled=True,
            )
        )
    return modules


def session_prompt_modules(
    runtime,
    session: dict[str, Any],
    user_text: str,
    history: list[dict[str, Any]],
) -> list[PromptModule]:
    modules = session_preset_modules(runtime, session)
    modules.extend(session_canon_modules(runtime, session))
    modules.extend(session_persona_modules(runtime, session))
    modules.extend(session_scene_narration_modules(runtime, session))
    modules.extend(session_scene_goal_modules(runtime, session))
    modules.extend(session_note_modules(runtime, session, history))
    modules.extend(session_memory_modules(runtime, session))
    modules.extend(session_lore_modules(runtime, session, user_text, history))
    return modules


def session_canon_modules(runtime, session: dict[str, Any]) -> list[PromptModule]:
    session_id = session.get("id") or ""
    if not session_id:
        return []
    try:
        project_id = runtime.store.get_project_id_for_session(session_id)
    except sqlite3.Error:
        return []
    if not project_id:
        return []
    try:
        canons = runtime.store.get_canon_for_prompt(project_id)
    except sqlite3.Error:
        return []
    if not canons:
        return []
    modules: list[PromptModule] = []
    for canon in canons:
        title = canon.get("title") or "Canon"
        content = canon.get("content") or ""
        if not content:
            continue
        modules.append(
            PromptModule(
                name=f"canon:{title}",
                role="system",
                content=f"{title}: {content}",
                position="after_card",
                insertion_order=-20,
                enabled=True,
            )
        )
    return modules


def session_persona_modules(runtime, session: dict[str, Any]) -> list[PromptModule]:
    persona_id = session.get("persona_id")
    if not persona_id:
        return []
    persona = runtime.store.get_persona(persona_id)
    if persona is None:
        return []
    return [
        PromptModule(
            name=f"persona:{persona['name']}",
            role="system",
            content=persona.get("content") or "",
            position="before_char",
            insertion_order=50,
            enabled=True,
        )
    ]


def session_scene_narration_modules(runtime, session: dict[str, Any]) -> list[PromptModule]:
    session_id = session.get("id") or ""
    if not session_id:
        return []

    try:
        controls = runtime.store.get_scene_narration_controls_for_session(session_id)
    except sqlite3.Error:
        return []
    if not controls:
        return []

    pov_label = (controls.get("pov_label") or "").strip()
    tense = (controls.get("tense") or "").strip()
    if not pov_label and not tense:
        return []

    try:
        scene = runtime.store.get_scene(controls.get("scene_id"))
    except sqlite3.Error:
        return []
    if not scene:
        return []

    lines = ["Scene narration controls:"]
    if pov_label:
        lines.append(f"POV: {pov_label}")
    if tense:
        lines.append(f"Tense: {tense}")

    return [
        PromptModule(
            name=f"scene_narration:{(scene.get('title') or 'Scene')}",
            role="system",
            content="\n".join(lines),
            position="before_user",
            insertion_order=65,
            enabled=True,
        )
    ]


def session_scene_goal_modules(runtime, session: dict[str, Any]) -> list[PromptModule]:
    session_id = session.get("id") or ""
    if not session_id:
        return []
    try:
        goal = runtime.store.get_scene_goal_for_session(session_id)
    except sqlite3.Error:
        return []
    if not goal:
        return []

    goal_text = (goal.get("goal_text") or "").strip()
    if not goal_text:
        return []

    try:
        scene = runtime.store.get_scene(goal["scene_id"])
    except sqlite3.Error:
        return []
    scene_title = (scene or {}).get("title") or "Scene"

    return [
        PromptModule(
            name=f"scene_goal:{scene_title}",
            role="system",
            content=f"Scene goal: {goal_text}",
            position="before_user",
            insertion_order=70,
            enabled=True,
        )
    ]


def session_note_modules(
    runtime, session: dict[str, Any], history: list[dict[str, Any]]
) -> list[PromptModule]:
    note_text = (session.get("note_text") or "").strip()
    if not note_text:
        return []
    frequency = session.get("note_frequency") or "always"
    every_n = max(2, min(20, int(session.get("note_every_n") or 3)))
    if frequency == "every_n":
        next_user_turn = sum(1 for row in history if row.get("role") == "user") + 1
        if next_user_turn % every_n != 0:
            return []
    position = session.get("note_position") or "before_user"
    order_by_position = {
        "before_char": 45,
        "after_history": 75,
        "before_user": 80,
    }
    return [
        PromptModule(
            name="note:author",
            role="system",
            content=note_text,
            position=position,
            insertion_order=order_by_position.get(position, 80),
            enabled=True,
        )
    ]


def session_memory_modules(runtime, session: dict[str, Any]) -> list[PromptModule]:
    session_key = session.get("session_key") or ""
    facts = tuple(
        TavernMemoryFact(
            id=row["id"],
            content=row.get("content") or "",
            importance=int(row.get("importance") or 1),
            source=row.get("source") or "manual",
        )
        for row in runtime.store.list_session_memory_facts(session_key)
    )
    summary_row = runtime.store.get_session_summary(session_key)
    context = TavernMemoryContext(
        summary=(summary_row or {}).get("summary") or "",
        facts=facts,
    )
    return build_memory_modules(context)


def session_lore_modules(
    runtime,
    session: dict[str, Any],
    user_text: str,
    history: list[dict[str, Any]],
) -> list[PromptModule]:
    lorebook_id = session.get("lorebook_id")
    if not lorebook_id:
        return []
    entries = runtime.store.list_lorebook_entries(lorebook_id)
    history_text = "\n".join(row.get("content", "") for row in history[-12:])
    result = match_lorebook_entries(entries, user_text, history_text=history_text)
    return modules_from_lore_matches(result)
