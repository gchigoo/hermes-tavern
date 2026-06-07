---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase164-default-binding-json-export"
date: "2026-06-07"
summary: >
  Phase 164 adds one bounded /rp binding export <binding-id> JSON export command
  for any stored novel default binding, following the Phase 149–163 export pattern.
  Resolves binding by integer ID, exports binding metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, default-binding, novel, offline, export, json]
owner: codestable-cron
---

# Phase 164: Default Binding JSON Export by ID

## Background

Phases 149–163 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, relationships, character states,
locations, organizations, plot threads, and style samples. Each exports one stored asset
to a profile-safe local JSON file and returns `file:` plus quoted `MEDIA:"<path>"`.
Phase 137 added `/rp binding ...` CRUD commands but there is no way to export a single
default binding as a standalone JSON file.

## Scope

Add one export branch to the existing binding command family:

- `/rp binding export <binding-id>`
- Resolve `<binding-id>` as an integer ID through existing `get_default_binding(binding_id)`.
- Read full binding metadata (id, scope_type, scope_id, asset_type, asset_id, created_at, updated_at).
- Build a JSON export payload with binding metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "bindings"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `binding_command()` dispatcher (after the `clear` case).
- Update `BINDING_USAGE` constant to include export.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change binding schema/index/migration code, binding ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk binding export, binding import, binding merge,
or binding auto-detection.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "binding_id": <int>,
  "scope_type": "<string>",
  "scope_id": <int>,
  "asset_type": "<string>",
  "asset_id": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_default_binding(binding_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/bindings/binding_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `binding_export()` function + `export` branch in `binding_command()` dispatcher (after `clear` case) + updated `BINDING_USAGE` constant
- `src/hermes_tavern/commands.py`: updated help_lines for binding command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp binding export <binding-id>` is visible in generated help and README Core commands.
- Exporting an existing binding by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found binding IDs return "No default binding found: <id>".
- Malformed/non-positive IDs return the binding usage string.
- Binding set/list/inspect/clear behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current default binding model from
the design. It mirrors the Phase 149–163 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp binding export <binding-id>` command and preserve existing deferred boundaries.
