---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase160-location-json-export"
date: "2026-06-07"
summary: >
  Phase 160 adds one bounded /rp location export <location-id> JSON export command
  for any stored novel location, following the Phase 149–159 export pattern.
  Resolves location by integer ID, exports location metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, location, novel, offline, export, json]
owner: codestable-cron
---

# Phase 160: Location JSON Export by ID

## Background

Phases 149–159 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, relationships, and character states.
Each exports one stored asset to a profile-safe local JSON file and returns `file:` plus
quoted `MEDIA:"<path>"`. Phase 132 added `/rp location ...` CRUD commands but there is no
way to export a single location as a standalone JSON file.

## Scope

Add one nested command:

- `/rp location export <location-id>`
- Resolve `<location-id>` as an integer ID through existing `get_location(location_id)`.
- Read full location metadata (id, project_id, label, description_text, created_at, updated_at).
- Build a JSON export payload with location metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "locations"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `location_command()` dispatcher.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change location schema/index/migration code, location ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk location export, location import, location merge,
location geocoding, or location auto-extraction.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "location_id": <int>,
  "project_id": <int>,
  "label": "<string>",
  "description_text": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_location(location_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/locations/location_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `location_export()` function + export branch in `location_command()` dispatcher
- `src/hermes_tavern/commands.py`: updated help_lines for location command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp location export <location-id>` is visible in generated help and README Core commands.
- Exporting an existing location by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found location IDs return "No location found: <id>".
- Malformed/non-positive IDs return the location usage string.
- Location add/list/inspect/update/delete behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current location model from
the root design. It mirrors the Phase 149–159 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp location export <location-id>` command and preserve existing deferred boundaries
(geocoding/auto-extraction remain out of scope).
