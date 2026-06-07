---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase162-plot-thread-json-export"
date: "2026-06-07"
summary: >
  Phase 162 adds one bounded /rp plot thread export <plot-thread-id> JSON export command
  for any stored novel plot thread, following the Phase 149–161 export pattern.
  Resolves plot thread by integer ID, exports plot thread metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, plot-thread, novel, offline, export, json]
owner: codestable-cron
---

# Phase 162: Plot Thread JSON Export by ID

## Background

Phases 149–161 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, relationships, character states,
locations, and organizations. Each exports one stored asset to a profile-safe local JSON file and returns
`file:` plus quoted `MEDIA:"<path>"`. Phase 134 added `/rp plot thread ...` CRUD commands
but there is no way to export a single plot thread as a standalone JSON file.

## Scope

Add one export branch to the existing plot thread command family:

- `/rp plot thread export <plot-thread-id>`
- Resolve `<plot-thread-id>` as an integer ID through existing `get_plot_thread(plot_thread_id)`.
- Read full plot thread metadata (id, project_id, label, description_text, created_at, updated_at).
- Build a JSON export payload with plot thread metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "plot-threads"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `plot_thread_command()` dispatcher (after the `delete` case).
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change plot thread schema/index/migration code, plot thread ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk plot thread export, plot thread import, plot thread merge,
or plot thread auto-extraction.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "plot_thread_id": <int>,
  "project_id": <int>,
  "label": "<string>",
  "description_text": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_plot_thread(plot_thread_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/plot-threads/plot_thread_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `plot_thread_export()` function + export branch in `plot_command()` dispatcher (after `delete` case)
- `src/hermes_tavern/commands.py`: updated help_lines for plot thread command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp plot thread export <plot-thread-id>` is visible in generated help and README Core commands.
- Exporting an existing plot thread by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found plot thread IDs return "No plot thread found: <id>".
- Malformed/non-positive IDs return the plot thread usage string.
- Plot thread add/list/inspect/update/delete behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current plot thread model from
the root design. It mirrors the Phase 149–161 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp plot thread export <plot-thread-id>` command and preserve existing deferred boundaries
(plot thread auto-extraction remain out of scope).
