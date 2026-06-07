---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase158-relationship-json-export"
date: "2026-06-07"
summary: >
  Phase 158 adds one bounded /rp relationship export <relationship-id> JSON export command
  for any stored novel relationship state, following the Phase 149–157 export pattern.
  Resolves relationship state by integer ID, exports relationship metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, relationship, novel, offline, export, json]
owner: codestable-cron
---

# Phase 158: Relationship State JSON Export by ID

## Background

Phases 149–157 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, and timeline. Each exports one stored asset to a
profile-safe local JSON file and returns `file:` plus quoted `MEDIA:"<path>"`.
Phase 130 added `/rp relationship ...` CRUD commands but there is no way to
export a single relationship state as a standalone JSON file.

## Scope

Add one nested command:

- `/rp relationship export <relationship-id>`
- Resolve `<relationship-id>` as an integer ID through existing `get_relationship_state(relationship_id)`.
- Read full relationship state metadata (id, project_id, label, state_text, created_at, updated_at).
- Build a JSON export payload with relationship metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "relationships"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `relationship_command()` dispatcher.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change relationship schema/index/migration code, relationship ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk relationship export, relationship import, relationship merge,
relationship visualization, relationship graph analysis, or relationship auto-extraction.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "relationship_id": <int>,
  "project_id": <int>,
  "label": "<string>",
  "state_text": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_relationship_state(relationship_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/relationships/relationship_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `relationship_export()` function + export branch in `relationship_command()` dispatcher
- `src/hermes_tavern/commands.py`: updated help_lines for relationship command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp relationship export <relationship-id>` is visible in generated help and README Core commands.
- Exporting an existing relationship state by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found relationship IDs return "No relationship state found: <id>".
- Malformed/non-positive IDs return the relationship usage string.
- Relationship add/list/inspect/rename/update/delete behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current relationship object model from
the root design. It mirrors the Phase 149–157 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp relationship export <relationship-id>` command and preserve existing deferred boundaries
(graph/merge-split/auto-extraction remain out of scope).
