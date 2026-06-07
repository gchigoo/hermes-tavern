---
doc_type: feature-design
status: approved
feature: "2026-06-07-hermes-tavern-phase165-scene-beat-json-export"
date: "2026-06-07"
summary: >
  Phase 165 adds one bounded /rp scene beat export <beat-id> JSON export command
  for any stored scene beat, following the Phase 149–164 export pattern.
  Resolves beat by integer ID, exports beat metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, scene-beats, novel, offline, export, json]
owner: codestable-cron
---

# Phase 165: Scene Beat JSON Export by ID

## Background

Phases 149–164 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, relationships, character states,
locations, organizations, plot threads, style samples, and default bindings. Each exports
one stored asset to a profile-safe local JSON file and returns `file:` plus quoted
`MEDIA:"<path>"`. Phase 138 added `/rp scene beat add/list/inspect/update/delete`
CRUD commands and Markdown export visibility but there is no way to export a single
scene beat as a standalone JSON file.

## Scope

Add one export branch to the existing scene beat command family:

- `/rp scene beat export <beat-id>`
- Resolve `<beat-id>` as an integer ID through existing `get_scene_beat(beat_id)`.
- Read full beat metadata (id, scene_id, label, beat_text, created_at, updated_at).
- Build a JSON export payload with beat metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "scene_beats"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `scene_beat()` dispatcher
  (after the `delete` case, before the final `return usage`).
- Update usage string to include export.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change scene beat schema/index/migration code, beat ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk beat export, beat import, beat merge,
or beat auto-detection.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "beat_id": <int>,
  "scene_id": <int>,
  "label": "<string>",
  "beat_text": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_scene_beat(beat_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/scene_beats/beat_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `scene_beat_export()` function + `export`
  branch in `scene_beat()` dispatcher (after `delete` case, before final
  `return usage`) + updated usage string
- `src/hermes_tavern/commands.py`: updated help_lines for scene beat command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp scene beat export <beat-id>` is visible in generated help and README Core commands.
- Exporting an existing scene beat by ID writes a profile-safe JSON file and returns
  `file:` and `MEDIA:"<path>"`.
- Not-found beat IDs return "No scene beat found: <id>".
- Malformed/non-positive IDs return the scene beat usage string.
- Beat add/list/inspect/update/delete behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current scene beat metadata model from
Phase 138. It mirrors the Phase 149–164 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp scene beat export <beat-id>` command and preserve existing deferred boundaries.

## Verification Commands

S1 executor verification:

    PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_manager.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_content.py src/hermes_tavern/memory.py src/hermes_tavern/runtime_memory.py src/hermes_tavern/images.py src/hermes_tavern/runtime_images.py src/hermes_tavern/importers plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md src/hermes_tavern/db_novel.py
    git diff --check
