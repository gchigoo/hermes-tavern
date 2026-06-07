---
doc_type: feature-design
status: accepted
feature: "2026-06-07-hermes-tavern-phase161-organization-json-export"
date: "2026-06-07"
summary: >
  Phase 161 adds one bounded /rp organization export <organization-id> JSON export command
  for any stored novel organization, following the Phase 149–160 export pattern.
  Resolves organization by integer ID, exports organization metadata as a profile-safe
  JSON file, and returns file: plus quoted MEDIA:"<path>". No schema, prompt,
  provider, generation, content-mode, or safety behavior changes.
tags: [hermes-tavern, organization, novel, offline, export, json]
owner: codestable-cron
---

# Phase 161: Organization JSON Export by ID

## Background

Phases 149–160 added individual JSON export commands for cards, lorebooks, presets,
personas, sessions, chapters, scenes, canon, timeline, relationships, character states,
and locations. Each exports one stored asset to a profile-safe local JSON file and returns
`file:` plus quoted `MEDIA:"<path>"`. Phase 133 added `/rp organization ...` CRUD commands
but there is no way to export a single organization as a standalone JSON file.

## Scope

Add one nested command:

- `/rp organization export <organization-id>`
- Resolve `<organization-id>` as an integer ID through existing `get_organization(organization_id)`.
- Read full organization metadata (id, project_id, label, description_text, created_at, updated_at).
- Build a JSON export payload with organization metadata.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "organizations"`.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add `export` subcommand branch to the existing `organization_command()` dispatcher.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change organization schema/index/migration code, organization ordering,
prompt compiler, provider/model routing, generation settings, credentials,
content-mode, project archive, plugin registration, gateway/core files, or
build artifacts.

This phase does not implement bulk organization export, organization import, organization merge,
or organization auto-extraction.

## Design

### JSON export payload

```json
{
  "hermes_tavern_export": true,
  "exported_at": "<ISO8601 UTC>",
  "organization_id": <int>,
  "project_id": <int>,
  "label": "<string>",
  "description_text": "<string>",
  "created_at": "<string>",
  "updated_at": "<string>"
}
```

### Data path

- Resolve: `runtime.store.get_organization(organization_id)` (existing API in db_novel.py)
- Write to: `<hermes_home>/plugins/hermes-tavern/exports/organizations/organization_<id>.json`
- No new DB APIs needed.

### Mount points

- `src/hermes_tavern/runtime_novel.py`: new `organization_export()` function + export branch in `organization_command()` dispatcher
- `src/hermes_tavern/commands.py`: updated help_lines for organization command
- `README.md`: Core commands table visibility
- `tests/test_hermes_tavern_novel_runtime.py`: focused export tests

### Slicing

S1 implements the export command, dispatcher branch, help, README, and focused tests.
S2 is controller-owned verification, acceptance, and architecture/root-design writeback.

## Acceptance Criteria

- `/rp organization export <organization-id>` is visible in generated help and README Core commands.
- Exporting an existing organization by ID writes a profile-safe JSON file and returns `file:` and `MEDIA:"<path>"`.
- Not-found organization IDs return "No organization found: <id>".
- Malformed/non-positive IDs return the organization usage string.
- Organization add/list/inspect/update/delete behavior is unchanged.
- No prompt/debug/context-budget, provider/model, generation, credential,
  retrieval/vectorization, archive/import, plugin shim, build artifact, or protected
  Hermes core behavior changes.

## Architecture/Root Design Relationship

This slice fills a small command-surface gap in the current organization model from
the root design. It mirrors the Phase 149–160 export pattern for inspect→export
command pairs. Architecture/root-design writeback in S2 should describe the new
`/rp organization export <organization-id>` command and preserve existing deferred boundaries
(organization merge/auto-extraction remain out of scope).
