---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase159-character-state-json-export"
date: "2026-06-07"
summary: >
  Phase 159 adds one bounded /rp character state export <character-state-id> JSON export command
  for any stored novel character state, following the Phase 149–158 export pattern.
  Resolves character state by integer ID, exports character state metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, character-state, novel, offline, export, json]
owner: codestable-cron
---

# Phase 159: Character State JSON Export by ID

## Background

Phases 149–158 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, and relationships. Each exports one stored asset to a
profile-safe local JSON file and returns `file:` plus quoted `MEDIA:"<path>"`.
Phase 131 added `/rp character state ...` CRUD commands but there is no way to
export a single character state as a standalone JSON file.

## Scope

Add one nested command:

- `/rp character state export <character-state-id>`
- Resolve `<character-state-id>` as an integer ID through existing `get_character_state(character_state_id)`.
- Read full character state metadata (id, project_id, label, state_text, created_at, updated_at).
- Build a JSON export payload with character state metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "character-states"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `character_command()` dispatcher.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change character-state schema/index/migration code, character-state ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk character-state export, character-state import, character-state merge,
character-state visualization, or character-state auto-extraction.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "character_state_id": <int>,
  "project_id": <int>,
  "label": "<string>",
  "state_text": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_character_state(character_state_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/character-states/character_state_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `character_state_export()` function + export branch in `character_command()` dispatcher
- `src/hermes_tavern/commands.py`: updated help_lines for character command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp character state export <character-state-id>` is visible in generated help and README Core commands.
- Exporting an existing character state by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found character-state IDs return "No character state found: <id>".
- Malformed/non-positive IDs return the character usage string.
- Character state add/list/inspect/update/delete behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current character-state object model from
the root design. It mirrors the Phase 149–158 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp character state export <character-state-id>` command and preserve existing deferred boundaries
(visualization/auto-extraction remain out of scope).
