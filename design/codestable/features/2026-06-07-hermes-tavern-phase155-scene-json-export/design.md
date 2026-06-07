---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase155-scene-json-export"
date: "2026-06-07"
summary: >
  Phase 155 adds one bounded /rp scene export <scene-id> JSON export command
  for any stored novel scene, following the Phase 149–154 export pattern.
  Resolves scene by integer ID, exports scene metadata as a profile-safe JSON
  file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, scene, novel, offline, export, json]
owner: codestable-cron
---

# Phase 155: Scene JSON Export by ID

## Background

Phases 149–154 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, and chapters. Each exports one stored asset to a profile-safe
local JSON file and returns `file:` plus quoted `MEDIA:"<path>"`. Phase 146 added
`/rp scene inspect <scene-id>` for read-only scene metadata inspection, and
Phase 154 added `/rp chapter export <chapter-id>` including an embedded scenes
array, but there is no way to export a single scene as a standalone JSON file.

## Scope

Add one nested command:

- `/rp scene export <scene-id>`
- Resolve `<scene-id>` as an integer ID through existing `get_scene(scene_id)`.
- Read full scene metadata (id, chapter_id, session_id, title, summary,
  scene_number, status, created_at, updated_at).
- Build a JSON export payload with scene metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "scenes"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `scene_command()` dispatcher.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change scene schema/index/migration code, session linking behavior, scene
start/narration/goal/beat/summary behavior, prompt compiler, provider/model routing,
generation settings, credentials, content-mode, project archive, plugin registration,
gateway/core files, or build artifacts.

This phase does not implement bulk scene export, scene import, scene merge,
scene editing tooling, or cross-scene analysis.

## Current State

Noun layer:

- `novel_scenes(id, chapter_id, session_id, title, summary, scene_number, status,
  created_at, updated_at)` stores scene metadata.
- `TavernStore.get_scene(scene_id)` resolves a scene row or returns None.
- `TavernStore.get_scene_summary(scene_id)` returns the summary text for a scene.
- Scene command dispatcher: `scene_command()` in `runtime_novel.py` (line 81–99)
  routes subcommands: create, list, inspect, start, beat, goal, narration, summary.

Command layer:

- `/rp scene inspect <scene-id>` (Phase 146) shows scene metadata read-only.
- `/rp scene export <scene-id>` does not exist.

Verification layer:

- `tests/test_hermes_tavern_novel_runtime.py` contains chapter export tests
  (Phase 154) and scene inspect/summary tests (Phase 146).
- `tests/test_hermes_tavern_readme_docs.py` validates README Core commands.

## Design

### Command dispatch

Add `if subcommand == "export": return scene_export(runtime, command)` to
`scene_command()` immediately after the `summary` case (line 98).

### Export function

```python
def scene_export(runtime: Any, command: RPCommand) -> str:
    if len(command.args) != 2:
        return _SCENE_USAGE

    scene_id = _safe_int(command.args[1])
    if scene_id is None or scene_id <= 0:
        return _SCENE_USAGE

    scene = runtime.store.get_scene(scene_id)
    if scene is None:
        return f"No novel scene found: {scene_id}"

    export_doc = {
        "hermes_tavern_export": True,
        "exported_at": datetime.utcnow().isoformat(),
        "scene_id": scene["id"],
        "chapter_id": scene["chapter_id"],
        "title": scene["title"],
        "scene_number": scene["scene_number"],
        "summary": scene.get("summary") or "",
        "status": scene["status"],
        "session_id": scene.get("session_id"),
        "created_at": scene.get("created_at"),
        "updated_at": scene.get("updated_at"),
    }

    export_dir = get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "scenes"
    export_dir.mkdir(parents=True, exist_ok=True)
    export_path = Path(export_dir) / f"scene_{scene_id}.json"
    export_path.write_text(
        json.dumps(export_doc, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return f"Scene exported as JSON.\nfile: {export_path}\nMEDIA:\"{export_path}\""
```

### Help visibility

Add `"/rp scene export <scene-id>",` to the scene command entry in
`commands.py` (TavernCommandEntry help_lines).

### README Core commands

Add `| `/rp scene export <scene-id>` | Export scene metadata as standalone JSON file. |`
to the Core Commands table in README.md, after the existing scene summary row.

### Tests

Add tests to `tests/test_hermes_tavern_novel_runtime.py`:

- scene_export_by_id — export a scene, verify file contents match
- scene_export_not_found — reject non-existent scene id
- scene_export_non_positive_id — reject 0 and negative IDs
- scene_export_missing_args — missing scene-id returns usage
- scene_export_path_containment — file path is under exports/scenes
- scene_export_quoted_media — output contains MEDIA:"<path>"
- scene_export_no_mutation — scene data unchanged after export
- scene_export_with_session — session_id included when linked
- scene_export_without_session — session_id null when not linked

Add help-line check to `tests/test_hermes_tavern_readme_docs.py`.

## Verification

- [ ] `PYTHONDONTWRITEBYTECODE=1 python -m py_compile` on changed files
- [ ] Targeted tests: `python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- [ ] Full Tavern suite: `python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- [ ] Protected-files diff: `git diff --name-only --` on prohibited files (empty output)
- [ ] `git diff --check` clean
- [ ] YAML validation on design.md and checklist.yaml

## Risks

| Risk | Mitigation |
|------|-----------|
| Scene ID may be invalid or not found | Reject with "No novel scene found: <id>" (same UX as scene_inspect) |
| Scene export path collisions | Each file named scene_{id}.json, one file per scene |

## Rollback

Remove the scene export branch, the `scene_export` function, help and README
literal, and focused tests. No DB migration or stored-data rollback is required.

## Notes

- No architect pass was run (gpt-5.5 rate-limited). Controller materialized
  artifacts following the proven Phase 149–154 export pattern.
- Implementation will be done by Codex executor (gpt-5.3-codex-spark).
- S2 acceptance/architecture writeback deferred to controller after S1 passes
  verification.
