---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase157-timeline-json-export"
date: "2026-06-07"
summary: >
  Phase 157 adds one bounded /rp timeline export <timeline-id> JSON export command
  for any stored novel timeline event, following the Phase 149–156 export pattern.
  Resolves timeline event by integer ID, exports timeline metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, timeline, novel, offline, export, json]
owner: codestable-cron
---

# Phase 157: Timeline JSON Export by ID

## Background

Phases 149–156 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, and canon. Each exports one stored asset to a
profile-safe local JSON file and returns `file:` plus quoted `MEDIA:"<path>"`.
Phase 144 added `/rp timeline inspect <timeline-id>` for read-only timeline event
inspection, but there is no way to export a single timeline event as a standalone
JSON file.

## Scope

Add one nested command:

- `/rp timeline export <timeline-id>`
- Resolve `<timeline-id>` as an integer ID through existing `get_timeline_event(timeline_event_id)`.
- Read full timeline event metadata (id, project_id, event_date, title, description,
  chapter_id, sort_key, created_at).
- Build a JSON export payload with timeline metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "timeline"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `timeline_command()` dispatcher.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change timeline schema/index/migration code, timeline ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk timeline export, timeline import, timeline merge,
timeline visualization, timeline map/geocode, or timeline graph analysis.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "timeline_id": <int>,
  "project_id": <int>,
  "event_date": "<string>",
  "title": "<string>",
  "description": "<string>",
  "chapter_id": <int|null>,
  "sort_key": "<string>",
  "created_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_timeline_event(timeline_event_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/timeline/timeline_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `timeline_export()` function + export branch in `timeline_command()` dispatcher
- `src/hermes_tavern/commands.py`: updated help_lines for timeline command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp timeline export <timeline-id>` is visible in generated help and README Core commands.
- Exporting an existing timeline event by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found timeline IDs return "No timeline event found: <id>".
- Malformed/non-positive IDs return the timeline usage string.
- Timeline list/inspect behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current timeline object model from
the root design. It mirrors the Phase 149–156 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp timeline export <timeline-id>` command and preserve existing deferred boundaries
(graph/map/geocode remain out of scope).
