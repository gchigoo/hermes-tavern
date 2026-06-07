---
doc_type: feature-design
status: implemented
feature: "2026-06-07-hermes-tavern-phase152-persona-json-export"
date: "2026-06-07"
summary: >
  IMPLEMENTED (S1) — Phase 152 adds one bounded offline /rp persona export
  <persona> JSON export surface for stored personas, following the Phase 149
  card export, Phase 150 lorebook export, and Phase 151 preset export pattern
  without schema, importer, prompt, provider, generation, content-mode,
  archive, or safety behavior changes. S2 acceptance/writeback remains deferred.
tags: [hermes-tavern, persona, offline, export, sillytavern]
owner: codestable-cron
---

# Phase 152: Persona JSON Export

## Background

Phase 149 implemented `/rp card export <card>`, Phase 150 implemented
`/rp lore export <lorebook>`, and Phase 151 implemented `/rp preset export
<preset>`. Each exports one existing stored asset to a profile-safe local JSON
file, prefers preserved raw JSON when available, falls back to normalized stored
fields, and returns `file:` plus quoted `MEDIA:"<path>"`.

Current persona support already has `/rp persona import`, `new`, `list`,
`inspect`, `use`, `temp`, `clear`, and `debug`. `TavernStore.get_persona(...)`
resolves ids/names and `last`, and `TavernStore.list_personas(...)` exposes the
stored persona rows. The `personas` table stores `id`, `name`, `content`,
`raw_json`, `source_path`, and `created_at`. The missing parity surface is a
single-persona JSON export.

## Scope

Add one nested command:

- `/rp persona export <persona>`
- Resolve `<persona>` through existing `TavernStore.get_persona(...)`, including
  `last`, because current persona lookup already supports it.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "personas"`.
- Prefer stored `personas.raw_json` when it parses as a JSON object.
- Otherwise build a normalized fallback object from the existing persona row
  (`name`, `content`, `source_path`, `created_at`).
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change persona import parsing, persona new/temp text handling, persona
use/binding behavior, persona clear/debug behavior, prompt compiler behavior,
prompt/debug/context-budget output, provider/model routing, generation settings
application, credentials, content-mode behavior, retrieval/vectorization,
schema/index/migration code, project archive/import/export behavior, plugin
registration, gateway/core files, or build artifacts.

This phase does not implement bulk persona export, persona editing, persona
JSON import format expansion, or any top-level command family.

## Current State

Noun layer:

- `personas(id, name, content, raw_json, source_path, created_at)` stores
  imported persona metadata and preserved raw JSON text.
- `TavernStore.get_persona(ref)` resolves id/name and process-local `last`.
- `TavernStore.list_personas(limit, offset)` returns ordered persona rows.
- `runtime_persona.py` owns nested persona subcommands.
- `commands.py` owns generated `/rp help` literals.
- README Core commands mirror the public command surface.

Change:

- Add an `export` branch to `persona_command(...)`.
- Add local helper functions in `runtime_persona.py` for safe filename
  construction, raw JSON coercion, fallback payload construction, and file write.
- Keep export read-only against Tavern data tables; only the local export file is
  created.

Flow:

    /rp persona export <persona>
      -> TAVERN_COMMAND_TABLE["persona"]
      -> runtime_persona.persona_command
      -> persona_export
      -> TavernStore.get_persona(ref)
      -> parse personas.raw_json as object
      -> fallback to persona row if raw object is unavailable
      -> write get_hermes_home()/plugins/hermes-tavern/exports/personas/persona_<id>.json
      -> return file: and MEDIA:"<path>"

## Fallback Payload

When preserved raw JSON is invalid, missing, or not a JSON object, emit a compact
normalized object:

- `name`: stored persona name.
- `content`: stored persona content text.
- `source_path`: stored persona import source.
- `created_at`: stored persona creation timestamp.

Exporting persona content does not activate or bind it to any session. The
command does not change persona binding, session state, prompt compiler behavior,
or safety classification.

## Structure Health

No micro-refactor is required.

`runtime_persona.py` is the established owner for nested persona command
orchestration and is small enough for one bounded export helper cluster.
`commands.py`, README, and the existing persona/docs tests are direct help/docs
surfaces. No new module or directory is needed.

## S1 Allowed Files

- `src/hermes_tavern/runtime_persona.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_personas.py`
- `tests/test_hermes_tavern_commands.py`
- `tests/test_hermes_tavern_readme_docs.py`

## S1 Prohibited Files

- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime.py`
- `src/hermes_tavern/db.py`
- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/runtime_assets.py`
- `src/hermes_tavern/runtime_lore.py`
- `src/hermes_tavern/runtime_presets.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`

## S1 Implementation Plan

1. Add `/rp persona export <persona>` dispatch and usage in `runtime_persona.py`.
2. Use `get_hermes_home()` for the persona export directory; do not hard-code
   `~/.hermes`.
3. Sanitize the persona id for the export filename so path-like ids cannot escape
   the personas export directory.
4. Prefer a parsed object from `personas.raw_json`.
5. Add normalized fallback JSON from existing persona row fields.
6. Return bounded usage, not-found, and success messages with quoted
   `MEDIA:"<path>"`.
7. Add help and README Core command literals.
8. Add focused tests for raw export, fallback export, `last`, usage/not-found,
   quoted paths with spaces, path containment, and no session/message/persona
   mutation.

## Acceptance Criteria

1. `/rp persona export <persona>` writes one UTF-8 JSON file under
   `get_hermes_home()/plugins/hermes-tavern/exports/personas`.
2. Export works without an active RP session.
3. `last` resolves through existing persona lookup behavior.
4. Stored raw JSON objects are exported unchanged except pretty formatting.
5. Invalid, missing, or non-object raw JSON falls back to normalized persona
   row fields.
6. The response includes `file:` and quoted `MEDIA:"<path>"`, including paths
   with spaces.
7. Sanitized filenames remain inside the persona export directory.
8. Generated help and README Core commands include `/rp persona export <persona>`.
9. Persona/session/message rows are not mutated by export.
10. No schema, importer, prompt/debug/context-budget, provider/model,
    generation, retrieval/vectorization, credential, content-mode, project
    archive, plugin, build, minors/underage, or safety-bypass behavior changes
    occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_persona.py src/hermes_tavern/commands.py tests/test_hermes_tavern_personas.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_personas.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_assets.py src/hermes_tavern/runtime_lore.py src/hermes_tavern/runtime_presets.py src/hermes_tavern/importers plugins build/lib`
- `git diff --check`
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase152-persona-json-export/design.md --require doc_type --require status --require feature`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-07-hermes-tavern-phase152-persona-json-export/checklist.yaml`

## Risks / Rollback

Risk: exporting persona content could be mistaken for activating or binding a
persona. Mitigation: the command is file export only, never calls session binding,
never changes `persona_id` on any session, and keeps existing persona
import/binding behavior intact.

Risk: raw JSON and normalized fallback shape can differ. Mitigation: match the
Phase 149/150/151 rule: prefer preserved raw object; fallback only when raw
cannot be used as an object.

Rollback is limited to removing the persona export branch/helpers, the
help/README literal, and focused tests. No DB migration or data rollback is
needed.

## S2 Later Tick

S2 is a docs/status acceptance and writeback slice for a later cron tick only.
It should rerun S1 verification, create the acceptance report, then update
architecture/root-design current-state docs and finalize checklist/design status.
S2 must not edit source, tests, README, gateway/core, plugin, provider, prompt,
schema, importer, generation, content-mode, or build files.
