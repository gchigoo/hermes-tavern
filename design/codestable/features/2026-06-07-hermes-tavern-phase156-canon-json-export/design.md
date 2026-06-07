---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase156-canon-json-export"
date: "2026-06-07"
summary: >
  Phase 156 adds one bounded /rp canon export <canon-id> JSON export command
  for any stored novel canon fact, following the Phase 149–155 export pattern.
  Resolves canon by integer ID, exports canon metadata as a profile-safe JSON
  file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, canon, novel, offline, export, json]
owner: codestable-cron
---

# Phase 156: Canon JSON Export by ID

## Background

Phases 149–155 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, and scenes. Each exports one stored asset to a profile-safe
local JSON file and returns `file:` plus quoted `MEDIA:"<path>"`. Phase 143 added
`/rp canon inspect <canon-id>` for read-only canon fact inspection, but there is no way
to export a single canon fact as a standalone JSON file.

## Scope

Add one nested command:

- `/rp canon export <canon-id>`
- Resolve `<canon-id>` as an integer ID through existing `get_canon(canon_id)`.
- Read full canon metadata (id, project_id, title, content, canon_group,
  importance, created_at, updated_at).
- Build a JSON export payload with canon metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "canon"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `canon_command()` dispatcher.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change canon schema/index/migration code, canon check/conflict/pin tools,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk canon export, canon import, canon merge,
canon vectorization, canon retrieval, or canonical/similarity analysis.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "canon_id": <int>,
  "project_id": <int>,
  "title": "<string>",
  "content": "<string>",
  "canon_group": "<string>",
  "importance": <int>,
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_canon(canon_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/canon/canon_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `canon_export()` function + export branch in `canon_command()` dispatcher
- `src/hermes_tavern/commands.py`: updated help_lines for canon command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp canon export <canon-id>` is visible in generated help and README Core commands.
- Exporting an existing canon fact by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found canon IDs return "No canon fact found: <id>".
- Malformed/non-positive IDs return the canon usage string.
- Canon list/inspect/group behavior and `get_canon_for_prompt` behavior are unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current canon object model from
the root design. It mirrors the Phase 149–155 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp canon export <canon-id>` command and preserve existing deferred boundaries
(check/conflict/pin remain out of scope).
