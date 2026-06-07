---
doc_type: feature-design
status: approved
feature: "2026-06-08-hermes-tavern-phase166-revision-note-json-export"
date: "2026-06-08"
summary: >
  Phase 166 adds one bounded /rp project revision export <note-id> JSON export command
  for any stored revision note, following the Phase 149–165 export pattern.
  Resolves revision note by integer ID, exports note metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, revision-notes, novel, offline, export, json]
owner: codestable-cron
---

# Phase 166: Revision Note JSON Export by ID

## Background

Phases 149–165 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, relationships, character states,
locations, organizations, plot threads, style samples, default bindings, and scene beats.
Each exports one stored asset to a profile-safe local JSON file and returns `file:` plus
quoted `MEDIA:"<path>"`. Phase 139 added `/rp project revision add/list/inspect/update/delete`
CRUD commands and Markdown export visibility but there is no way to export a single
revision note as a standalone JSON file.

## Scope

Add one export branch to the existing revision note command family:

- `/rp project revision export <note-id>`
- Resolve `<note-id>` as an integer ID through existing `get_revision_note(note_id)`.
- Read full note metadata (id, project_id, label, note_text, created_at, updated_at).
- Build a JSON export payload with note metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "revision_notes"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `project_revision()` dispatcher
  (after the `delete` case, before the final `return usage`).
- Update usage string to include export.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change revision note schema/index/migration code, note ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk note export, note import, note merge,
or note auto-detection.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "note_id": <int>,
  "project_id": <int>,
  "label": "<string>",
  "note_text": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_revision_note(note_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/revision_notes/note_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `project_revision_export()` function + `export`
  branch in `project_revision()` dispatcher (after `delete` case, before final
  `return usage`) + updated usage string
- `src/hermes_tavern/commands.py`: updated help_lines for project command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp project revision export <note-id>` is visible in generated help and README Core commands.
- Exporting an existing revision note by ID writes a profile-safe JSON file and returns
  `file:` and `MEDIA:"<path>"`.
- Not-found note IDs return "No revision note found: <id>".
- Malformed/non-positive IDs return the revision note usage string.
- Revision note add/list/inspect/update/delete behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills the last remaining command-surface gap in the current revision note
metadata model from Phase 139. It mirrors the Phase 149–165 export pattern for
inspect→export command pairs. Architecture/root-design writeback in S2 should describe
the new `/rp project revision export <note-id>` command and preserve existing deferred
boundaries.

## Verification Commands

S1 executor verification:

    PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_manager.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_content.py src/hermes_tavern/memory.py src/hermes_tavern/runtime_memory.py src/hermes_tavern/images.py src/hermes_tavern/runtime_images.py src/hermes_tavern/importers plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md src/hermes_tavern/db_novel.py
    git diff --check
