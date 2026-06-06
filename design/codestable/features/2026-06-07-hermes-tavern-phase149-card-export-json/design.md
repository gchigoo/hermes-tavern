---
doc_type: feature-design
status: implemented
feature: "2026-06-07-hermes-tavern-phase149-card-export-json"
date: "2026-06-07"
summary: >
  IMPLEMENTED S1 - Add a bounded local /rp card export <card> command that writes
  one stored character card as SillyTavern-compatible JSON and returns a quoted
  MEDIA marker without mutating runtime state or touching provider/generation
  paths. S2 acceptance/writeback remains planned.
tags: [hermes-tavern, card, export, sillytavern, command-surface, offline]
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
---

# Phase 149: Card Export JSON

## Background

No planned or in-progress recent checklist remains after Phase 148. The root
design still lists `/rp card export <card>` in the character-card command vision.
Current source exposes `/rp card import`, `/rp card inspect`, `/rp card use`, and
`/rp card greeting`, but no standalone card export command.

This is a small SillyTavern asset-compatibility gap: imported cards preserve raw
card data in `cards.data_json`, but mobile users cannot export one stored card
back to a JSON file without exporting a whole session.

## Scope

Add one local, offline command:

- `/rp card export <card>` under the existing card command family.
- Resolve `<card>` through existing `TavernStore.get_card(...)`, including `last`.
- Write one JSON file under `get_hermes_home() / "plugins" / "hermes-tavern" / "exports" / "cards"`.
- Prefer preserved `data_json.raw` when it is a JSON object; otherwise write a
  normalized SillyTavern-compatible JSON card document from stored card fields.
- Return a compact response with `file: <path>` and quoted `MEDIA:"<path>"`.
- Add generated help and README Core command visibility.
- Add focused offline tests.

## Non-goals / Boundaries

This phase does not add PNG export, bulk export, archive ZIP export/import,
remote upload, card editing, card deletion, card merge, card validation tooling,
or session/project export changes.

No schema, card/session/message mutation, prompt/debug/context-budget behavior,
provider/model routing, generation, credentials, retrieval/vectorization,
content-mode, media/TTS/image provider behavior, archive/import workflow,
automatic extraction, minors/underage, safety-bypass, plugin registration, or
protected Hermes core behavior changes are in scope.

Do not edit `run_agent.py`, `cli.py`, `gateway/run.py`, `src/hermes_tavern/runtime.py`,
DB files, importer files, provider/model/generation/prompt files, `plugins/**`,
or `build/lib/**`.

## Proposed Design

Current noun layer:

- Stored cards live in `cards(id, name, data_json, source_path, created_at)`.
- `data_json` stores normalized card fields plus preserved `raw` imported card JSON.
- `TavernStore.get_card(card_id_or_name)` already resolves ids, short ids, names,
  and the process-local `last` card reference.
- Session and project exports already use local files plus quoted `MEDIA:"..."`
  markers for gateway delivery.

Change:

- Extend `card_command` with an `export` subcommand.
- Add a card export helper in `runtime_assets.py`.
- The helper loads one stored card, parses `data_json`, chooses preserved raw JSON
  when available, falls back to normalized ST-compatible JSON, writes UTF-8 JSON,
  and returns bounded command output.
- Export does not call card importers, prompt compiler, model router, provider
  bridge, generation, session mutation, or message mutation paths.

Flow:

```text
/rp card export <card>
  -> TAVERN_COMMAND_TABLE["card"]
  -> runtime_assets.card_command
  -> card_export
  -> TavernStore.get_card(ref)
  -> choose preserved raw JSON or normalized fallback
  -> write profile-safe JSON export
  -> return file path + MEDIA marker
```

No micro-refactor is needed. `runtime_assets.py` already owns card subcommands
and can host this bounded export branch beside import/search/inspect/greeting.

## S1 Allowed Files

- `src/hermes_tavern/runtime_assets.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_card_export.py`
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
- `design/**` during S1 implementation, except controller-owned materialization/status sync

## S1 Implementation Plan

1. Add `/rp card export <card>` to card usage text and generated help.
2. Add `card_export` handling under `runtime_assets.card_command`.
3. Write exported JSON under the profile-safe Hermes Tavern export directory.
4. Prefer preserved raw card JSON and provide a normalized fallback for synthetic cards.
5. Return bounded success, usage, and missing-card messages with quoted `MEDIA:"..."`.
6. Add focused tests for raw export, fallback export, `last`, missing card, usage, help, and README visibility.
7. Run focused and Tavern-wide offline verification.

## Acceptance Criteria

1. `/rp card export <card>` writes one JSON file for an existing stored card.
2. Export works without an active RP session.
3. `last` resolves consistently with existing card inspect/greeting behavior.
4. Missing cards return the existing card-not-found style response.
5. Exported paths are under `get_hermes_home()` and responses include quoted `MEDIA:"<path>"`.
6. Preserved raw card JSON is exported when present; normalized fallback JSON is used when raw is absent.
7. Generated help and README Core commands include `/rp card export <card>`.
8. No schema, card/session/message mutation, prompt/debug/context-budget, provider/model, generation, credential, retrieval/vectorization, content-mode, media/TTS/image provider, archive/import, automatic extraction, minors/underage, safety-bypass, plugin registration, or protected core behavior changes occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/commands.py src/hermes_tavern/runtime_assets.py tests/test_hermes_tavern_card_export.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_card_export.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/importers plugins build/lib design`
- `git diff --check`

## Risks / Rollback

Risk: export could drift into session/project export semantics. Mitigation: keep
the handler nested under `runtime_assets.py`, export only one card row, and do
not read session/message tables.

Risk: path handling could break gateway media delivery for paths with spaces.
Mitigation: reuse the quoted `MEDIA:"<path>"` response contract and test spaces in
the Hermes home path.

Rollback is simple: remove the card subcommand branch, help/README literal, and
focused tests. No DB migration or data rollback is needed.
