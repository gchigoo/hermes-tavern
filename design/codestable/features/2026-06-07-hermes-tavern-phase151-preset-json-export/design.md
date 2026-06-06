---
doc_type: feature-design
status: implemented
feature: "2026-06-07-hermes-tavern-phase151-preset-json-export"
date: "2026-06-07"
summary: >
  IMPLEMENTED - Phase 151 adds one bounded offline /rp preset export <preset>
  JSON export surface for stored presets, following the Phase 149 card export and
  Phase 150 lorebook export pattern without schema, importer, prompt, provider,
  generation, content-mode, archive, or safety behavior changes. S2 acceptance
  writeback remains planned.
tags: [hermes-tavern, preset, offline, export, sillytavern]
owner: codestable-cron
---

# Phase 151: Preset JSON Export

## Background

Phase 149 implemented `/rp card export <card>` and Phase 150 implemented
`/rp lore export <lorebook>`. Both export one existing stored asset to a
profile-safe local JSON file, prefer preserved raw JSON when available, fall back
to normalized stored fields, and return `file:` plus quoted `MEDIA:"<path>"`.

Current preset support already has `/rp preset import`, `list`, `inspect`, `use`,
and `clear`. `TavernStore.get_preset(...)` resolves ids/names and `last`, and
`list_prompt_modules(...)` exposes the stored prompt-module rows needed for a
fallback payload. The missing parity surface is a single-preset JSON export.

## Scope

Add one nested command:

- `/rp preset export <preset>`
- Resolve `<preset>` through existing `TavernStore.get_preset(...)`, including
  `last`, because current preset lookup already supports it.
- Write one UTF-8 JSON file under
  `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "presets"`.
- Prefer stored `presets.raw_json` when it parses as a JSON object.
- Otherwise build a normalized fallback object from the existing preset row and
  `prompt_modules` rows.
- Return bounded output containing `file: <path>` and quoted `MEDIA:"<path>"`.
- Add generated help and README Core command visibility.
- Add focused offline regression tests.

## Non-goals / Boundaries

Do not change preset import parsing, preset safety classification, prompt module
selection, prompt compiler behavior, prompt/debug/context-budget output,
provider/model routing, generation settings application, credentials,
content-mode behavior, retrieval/vectorization, schema/index/migration code,
project archive/import/export behavior, plugin registration, gateway/core files,
or build artifacts.

This phase does not implement bulk preset export, preset editing, preset
validation tooling, preset import format expansion, prompt-order semantics,
generation-setting application, provider-safety bypass behavior, minors/underage
behavior, or any top-level command family.

## Current State

Noun layer:

- `presets(id, name, source, raw_json, created_at)` stores imported preset
  metadata and preserved raw JSON text.
- `prompt_modules(id, preset_id, name, role, content, enabled, position,
  insertion_order, raw_json, created_at)` stores normalized preset modules.
- `TavernStore.get_preset(ref)` resolves id/name and process-local `last`.
- `TavernStore.list_prompt_modules(preset_id)` returns ordered module rows.
- `runtime_presets.py` owns nested preset subcommands.
- `commands.py` owns generated `/rp help` literals.
- README Core commands mirror the public command surface.

Change:

- Add an `export` branch to `preset_command(...)`.
- Add local helper functions in `runtime_presets.py` for safe filename
  construction, raw JSON coercion, fallback payload construction, and file write.
- Keep export read-only against Tavern data tables; only the local export file is
  created.

Flow:

    /rp preset export <preset>
      -> TAVERN_COMMAND_TABLE["preset"]
      -> runtime_presets.preset_command
      -> preset_export
      -> TavernStore.get_preset(ref)
      -> parse presets.raw_json as object
      -> fallback to preset + prompt_modules if raw object is unavailable
      -> write get_hermes_home()/plugins/hermes-tavern/exports/presets/preset_<id>.json
      -> return file: and MEDIA:"<path>"

## Fallback Payload

When preserved raw JSON is invalid, missing, or not a JSON object, emit a compact
normalized object:

- `name`: stored preset name.
- `source`: stored preset source.
- `prompts`: ordered list derived from `prompt_modules`.
- Each prompt includes `name`, `role`, `content`, `enabled`, `position`, and
  `insertion_order`.
- If a module `raw_json` parses as an object, include it under `raw` so stored
  risk metadata and original entry hints remain inspectable without changing
  prompt semantics.

Exporting disabled or risky imported module text does not activate it. The
command does not reclassify, optimize, relabel, enable, or inject preset content.

## Structure Health

No micro-refactor is required.

`runtime_presets.py` is the established owner for nested preset command
orchestration and is small enough for one bounded export helper cluster.
`commands.py`, README, and the existing preset/docs tests are direct help/docs
surfaces. No new module or directory is needed.

## S1 Allowed Files

- `src/hermes_tavern/runtime_presets.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_runtime_presets.py`
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
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`

## S1 Implementation Plan

1. Add `/rp preset export <preset>` dispatch and usage in `runtime_presets.py`.
2. Use `get_hermes_home()` for the preset export directory; do not hard-code
   `~/.hermes`.
3. Sanitize the preset id for the export filename so path-like ids cannot escape
   the presets export directory.
4. Prefer a parsed object from `presets.raw_json`.
5. Add normalized fallback JSON from existing preset and prompt-module rows.
6. Return bounded usage, not-found, and success messages with quoted
   `MEDIA:"<path>"`.
7. Add help and README Core command literals.
8. Add focused tests for raw export, fallback export, `last`, usage/not-found,
   quoted paths with spaces, path containment, and no session/message/preset/module
   mutation.

## Acceptance Criteria

1. `/rp preset export <preset>` writes one UTF-8 JSON file under
   `get_hermes_home()/plugins/hermes-tavern/exports/presets`.
2. Export works without an active RP session.
3. `last` resolves through existing preset lookup behavior.
4. Stored raw JSON objects are exported unchanged except pretty formatting.
5. Invalid, missing, or non-object raw JSON falls back to normalized preset and
   prompt-module rows.
6. The response includes `file:` and quoted `MEDIA:"<path>"`, including paths
   with spaces.
7. Sanitized filenames remain inside the preset export directory.
8. Generated help and README Core commands include `/rp preset export <preset>`.
9. Preset/session/message/prompt-module rows are not mutated by export.
10. No schema, importer, prompt/debug/context-budget, provider/model,
    generation, retrieval/vectorization, credential, content-mode, project
    archive, plugin, build, minors/underage, or safety-bypass behavior changes
    occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_presets.py src/hermes_tavern/commands.py tests/test_hermes_tavern_runtime_presets.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_runtime_presets.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/importers plugins build/lib`
- `git diff --check`
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase151-preset-json-export/design.md --require doc_type --require status --require feature`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-07-hermes-tavern-phase151-preset-json-export/checklist.yaml`

## Risks / Rollback

Risk: exporting preset content could be mistaken for activating unsafe preset
modules. Mitigation: the command is file export only, never calls prompt assembly,
never changes `enabled`, and keeps existing safety/import behavior intact.

Risk: raw JSON and normalized fallback shape can differ. Mitigation: match the
Phase 149/150 rule: prefer preserved raw object; fallback only when raw cannot be
used as an object.

Rollback is limited to removing the preset export branch/helpers, the help/README
literal, and focused tests. No DB migration or data rollback is needed.

## S1 Implementation Result

Codex architect returned `RESULT: IMPLEMENTABLE_NEW_FEATURE` in
`/tmp/hermes-tavern-architect-phase151-preset-json-export.jsonl`, and the
controller materialized this approved design plus checklist. Codex executor
implemented the bounded S1 slice in
`/tmp/hermes-tavern-executor-phase151-preset-json-export.jsonl`, limited to the
allowed preset runtime/help/README/test files. Controller verification passed:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_presets.py src/hermes_tavern/commands.py tests/test_hermes_tavern_runtime_presets.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_runtime_presets.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` (`106 passed`)
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` (`1089 passed`)
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` (`1089 passed`)
- protected-file reverse-scope guard: empty output
- CodeStable design/checklist validators
- `git diff --check`

Executor JSONL includes one harmless failed patch-file `py_compile` probe and one
initial focused pytest failure before executor self-repair; final executor and
controller reruns passed. Phase 151 S1 is implemented. S2 acceptance/writeback
remains planned.

## S2 Later Tick

S2 is a docs/status acceptance and writeback slice for a later cron tick only.
It should rerun S1 verification, create the acceptance report, then update
architecture/root-design current-state docs and finalize checklist/design status.
S2 must not edit source, tests, README, gateway/core, plugin, provider, prompt,
schema, importer, generation, content-mode, or build files.