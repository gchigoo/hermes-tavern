---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase154-chapter-json-export"
date: "2026-06-07"
summary: >
  Phase 154 adds one bounded /rp chapter export <chapter-id> JSON export command
  for any stored novel chapter, following the Phase 149–153 export pattern.
  Resolves chapter by integer ID, exports chapter metadata + scenes + summary as
  a profile-safe JSON file, and returns file: plus quoted MEDIA:"<path>".
  No schema, prompt, provider, generation, content-mode, or safety behavior
  changes.
tags: [hermes-tavern, chapter, novel, offline, export, json]
owner: codestable-cron
---

# Phase 154: Chapter JSON Export by ID

## Background

Phases 149–153 added individual JSON export commands for cards, lorebooks, presets,
personas, and sessions. Each exports one stored asset to a profile-safe local JSON
file and returns `file:` plus quoted `MEDIA:"<path>"`. Phase 145 added `/rp chapter
inspect <chapter-id>` for read-only chapter metadata inspection, but there is no way
to export chapter data as a standalone JSON file.

## Scope

Add one nested command:

- `/rp chapter export <chapter-id>`
- Resolve `<chapter-id>` as an integer ID through existing `get_chapter(chapter_id)`.
- Read chapter metadata (title, chapter_number, summary, status, project_id).
- Read associated scenes via existing `list_scenes(chapter_id)`.
- Build a JSON export payload with chapter metadata + scenes array.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "chapters"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change chapter schema/index/migration code, prompt compiler, provider/model
routing, generation settings, credentials, content-mode, retrieval/vectorization,
project archive, plugin registration, gateway/core files, or build artifacts.

This phase does not implement bulk chapter export, chapter import, chapter merge,
chapter editing tooling, or cross-chapter analysis.

## Current State

Noun layer:

- `novel_chapters(id, project_id, title, chapter_number, summary, status, created_at,
  updated_at)` stores chapter metadata.
- `novel_scenes(id, chapter_id, session_id, title, summary, scene_number, status,
  created_at, updated_at)` stores per-chapter scenes.
- `TavernStore.get_chapter(chapter_id)` resolves a chapter row or returns None.
- `TavernStore.list_scenes(chapter_id)` lists scenes for a chapter.
- `TavernStore.get_chapter_summary(chapter_id)` returns the summary row.
- `runtime_novel.py` owns the `chapter_command` dispatch and `chapter_inspect` handler.
- `commands.py` owns generated `/rp help` literals.
- README Core commands mirror the public command surface.

Change:

- Add an `export` branch to `chapter_command(...)` in `runtime_novel.py`.
- Add a `chapter_export` function in `runtime_novel.py` that reads the chapter row,
  lists scenes, builds JSON payload, writes to profile-safe export path, and returns
  the file path + MEDIA marker.
- Keep export read-only against Tavern data tables; only the local export file is
  created.

Flow:

```text
/rp chapter export <chapter-id>
  -> TAVERN_COMMAND_TABLE["chapter"]
  -> runtime._chapter_command
  -> runtime_novel.chapter_command
  -> chapter_export
  -> get_chapter(chapter_id) -> reject if None
  -> list_scenes(chapter_id) for scene metadata
  -> write get_hermes_home()/plugins/hermes-tavern/exports/chapters/chapter_<id>.json
  -> return file: and MEDIA:"<path>"
```

## Export Payload Format

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO timestamp>",
  "chapter_id": <id>,
  "project_id": <project_id>,
  "title": "<title>",
  "chapter_number": <N>,
  "status": "<status>",
  "summary": "<summary text or ''>",
  "scenes": [
    {
      "scene_id": <id>,
      "title": "<title>",
      "scene_number": <N>,
      "summary": "<summary text or ''>",
      "status": "<status>",
      "session_id": "<session_id or null>"
    }
  ]
}
```

## Structure Health

No micro-refactor is required.

`runtime_novel.py` is the established owner for novel command dispatch and is large
enough for one bounded export helper cluster. `commands.py`, README, and the existing
novel/README docs tests are direct help/docs surfaces. No new module or directory is
needed.

## S1 Allowed Files

- `src/hermes_tavern/runtime_novel.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_novel_runtime.py`
- `tests/test_hermes_tavern_readme_docs.py`

## S1 Prohibited Files

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime.py`
- `src/hermes_tavern/runtime_lifecycle.py`
- `src/hermes_tavern/runtime_sessions.py`
- `src/hermes_tavern/runtime_assets.py`
- `src/hermes_tavern/db.py`
- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/runtime_lore.py`
- `src/hermes_tavern/runtime_persona.py`
- `src/hermes_tavern/runtime_presets.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`

## S1 Implementation Plan

1. Add `/rp chapter export <chapter-id>` dispatch and usage in `runtime_novel.py`.
2. Use `get_chapter(chapter_id)` for chapter resolution; reject if None.
3. Read chapter metadata fields (title, chapter_number, summary, status, project_id).
4. Read associated scenes via `list_scenes(chapter_id)` for scene metadata.
5. Build JSON payload with chapter metadata + scenes array.
6. Use `get_hermes_home()` for the chapter export directory; do not hard-code `~/.hermes`.
7. Write UTF-8 JSON file and return `file:` plus quoted `MEDIA:"<path>"`.
8. Add help and README Core command literals.
9. Add focused tests: export by ID, not-found chapter, chapter with scenes, chapter
   without scenes, path containment, quoted paths with spaces, and no chapter/scene
   mutation.

## Acceptance Criteria

1. `/rp chapter export <chapter-id>` writes one UTF-8 JSON file under
   `get_hermes_home()/plugins/hermes-tavern/exports/chapters`.
2. Export resolves chapter by integer ID; rejects not-found.
3. Export works for chapters with scenes, including scene metadata.
4. Export works for chapters with zero scenes (empty scenes array).
5. Export includes chapter summary text when available.
6. The response includes `file:` and quoted `MEDIA:"<path>"`, including paths with
   spaces.
7. Sanitized filenames remain inside the chapter export directory.
8. Generated help and README Core commands include `/rp chapter export <chapter-id>`.
9. Chapter/scene rows are not mutated by export.
10. No schema, prompt, provider/model, generation, retrieval/vectorization, credential,
    content-mode, project archive, plugin, build, minors/underage, or safety-bypass
    behavior changes occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/runtime_lifecycle.py src/hermes_tavern/runtime_sessions.py src/hermes_tavern/runtime_assets.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_lore.py src/hermes_tavern/runtime_persona.py src/hermes_tavern/runtime_presets.py src/hermes_tavern/importers plugins build/lib`
- `git diff --check`
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase154-chapter-json-export/design.md --require doc_type --require status --require feature`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-07-hermes-tavern-phase154-chapter-json-export/checklist.yaml`

## Risks / Rollback

Risk: Chapter ID may be invalid or not found.
Mitigation: reject with "No novel chapter found: <id>" (same UX as chapter_inspect).

Risk: Export payload may include too many scenes for very large chapters.
Mitigation: list_scenes returns all scenes for a chapter; pagination is deferred to
a later phase if needed.

Rollback is limited to removing the chapter export branch/helpers, the help/README
literal, and focused tests. No DB migration or data rollback is needed.

## S2 Later Tick

S2 is a docs/status acceptance and writeback slice for a later cron tick only.
It should rerun S1 verification, create the acceptance report, then update
architecture/root-design current-state docs and finalize checklist/design status.
S2 must not edit source, tests, README, gateway/core, plugin, provider, prompt,
schema, importer, generation, content-mode, or build files.
