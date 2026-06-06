---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase151-preset-json-export"
status: accepted
date: "2026-06-07"
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
tags: [hermes-tavern, preset, export, acceptance, offline]
---

# Phase 151 Preset JSON Export Acceptance

> 阶段：S2 验收/写回
> 验收日期：2026-06-07
> 关联设计文档：design/codestable/features/2026-06-07-hermes-tavern-phase151-preset-json-export/design.md
> 关联 checklist：design/codestable/features/2026-06-07-hermes-tavern-phase151-preset-json-export/checklist.yaml

## 1. S1 scope contract

- S1 is implemented as one bounded local `/rp preset export <preset>` command for one existing stored preset.
- Implementation resolves presets through existing `TavernStore.get_preset(...)` behavior, including `last`.
- It writes a UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/presets`.
- It prefers `presets.raw_json` when that value parses as a JSON object; otherwise it uses a normalized fallback assembled from the preset row + `list_prompt_modules(...)` rows.
- Success output includes `file:` plus quoted `MEDIA:"<path>"`.
- S2 is documentation-only and does not alter source/runtime/tests/README/core/plugin/build artifact files.

## 2. Interface/schema contract

- No schema/table/index/migration files were changed in S2; feature implementation remains on top of existing `presets` and `prompt_modules` shape.
- S1 read path still uses `TavernStore.get_preset(...)` and `list_prompt_modules(...)`, and no new DB APIs were introduced.
- `presets(id, name, source, raw_json, created_at)` and `prompt_modules(...)` remain unchanged by Phase 151.
- S2 checks do not apply code mutations to DB schema or data model layers.

## 3. Command/output contract

- Command path: `/rp preset export <preset>`.
- Missing argument form returns `Usage: /rp preset export <preset>`.
- Missing preset returns the existing bounded not-found messaging used by preset lookup and supports existing `last` no-preset behavior.
- Success output includes:
  - `Preset exported as JSON.`
  - `file: <path>`
  - `MEDIA:"<path>"`
- Existing command-family behavior remains under `/rp preset ...`.

## 4. No-session / no-mutation behavior

- The command runs command-only, no active-session requirement.
- It does not create, switch, or mutate any session/message rows.
- It does not mutate stored preset or prompt-module rows.
- It does not mutate schema, prompts, provider/model routing, generation, retrieval/vectorization, or credentials.
- Existing S1 tests assert session/message invariance for export operations.

## 5. Export placement / MEDIA / path containment

- Exports are written to profile-safe path:
  `get_hermes_home()/plugins/hermes-tavern/exports/presets`.
- Filename generation is sanitized (`preset_<id>.json`) and stays under that directory.
- JSON is written as UTF-8 with pretty formatting.
- Response uses quoted MEDIA marker, preserving spaces in paths and matching Tavern media-delivery contract.

## 6. Raw/fallback behavior

- If `presets.raw_json` is a JSON object, it is exported as preserved payload (pretty-formatted).
- If `raw_json` is missing, invalid JSON, or not an object, export falls back to:
  - preset top-level fields (`name`, `source`),
  - normalized `prompts` array from stored `prompt_modules` row fields:
    `name`, `role`, `content`, `enabled`, `position`, `insertion_order`.
  - If a module `raw_json` parses as an object, it is included under `raw` for preserved risk metadata.
- This fallback path is deterministic, local, and does not require import or provider flows.

## 7. Help/README evidence

- S1 added `/rp preset export <preset>` to generated command help.
- S1 added core README command documentation.
- S2 does not re-edit README or source; it records those prior S1 evidence points for controller handoff.

## 8. Reverse-scope / no-leak boundaries

Phase 151 remains scoped to one preset export and does not implement:

- project archive ZIP export/import
- ST preset importer format transformation
- card export/lorebook export parity changes
- session/message editing, project lifecycle writes, or generation-path effects
- preset editing, preset validation, prompt-order semantics changes
- provider/model routing, credential resolution, content-mode/minors/underage changes
- safety-bypass behavior changes

No prompt debug/context budgets, retrieval/vectorization, or prompt-module pipelines are changed for this command.

## 9. Architecture / root-design writeback

- `design/codestable/architecture/ARCHITECTURE.md` writeback includes:
  - `/rp command surface (current through Phase 151)` and preset command extension with `export <preset>`.
  - New Phase 151 bullet describing `/rp preset export <preset>` behavior.
  - DB heading updated to `current through Phase 151; unchanged by Phase 151`.
  - `Tavern export MEDIA contract` extended with `/rp preset export <preset>`.
  - New Phase 151 preset export boundary bullet and path/behavior summary.
- `design/HERMES_TAVERN_DESIGN.md` writeback includes:
  - `§6.5` preset command list updated with `/rp preset export <preset>`.
  - Phase 151 paragraph after Phase 150 in `§6.6`.
  - `Phase 121–150` references updated to `Phase 121–151`.
  - Exporter section updated: `preset export JSON/native` moved from deferred to current.

## 10. Requirement / roadmap writeback

- `design/codestable/features/2026-06-07-hermes-tavern-phase151-preset-json-export/design.md` has no `requirement`, `roadmap`, or `roadmap_item`.
- No requirements/roadmaps are updated in S2.

## 11. Attention candidates

- No new `attention.md` candidate identified for this pass.
- Existing repository-level attentions (profile-safe path discipline, protected file constraints) remain sufficient for this S2 closeout pass.

## 12. Verification ledger

### 12.1 S1 controller results (factual)

| Command / guard | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_presets.py src/hermes_tavern/commands.py tests/test_hermes_tavern_runtime_presets.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` | passed (2026-06-07 controller) |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_runtime_presets.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | `106 passed` (2026-06-07 controller) |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | `1089 passed` (2026-06-07 controller) |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | `1089 passed` (2026-06-07 controller) |
| Protected-path reverse-scope guard for S1 source/runtime boundaries | returned empty diff |
| `git diff --check` | passed |

### 12.2 S2 controller verification

| Command / guard | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_runtime_presets.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | `106 passed` |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | `1089 passed` |
| Protected-path diff guard for README/source/tests/core/plugin/build paths | passed; empty output |
| `git diff --check` | passed |
| Current-doc stale wording guard for old Phase 150 / Phase 121–150 current-state labels | S2 updates applied |
| Current wording guard for `/rp preset export <preset>`, `Phase 151`, `exports/presets`, `presets.raw_json`, normalized fallback, and quoted `MEDIA:"<path>"` | passed; expected current hits |

## 13. Residual deferred work

- Single-preset export is implemented; broader preset tooling remains deferred:
  preset bulk export, preset editing, preset validation, project archive ZIP importer/exporter, and broader extraction/tooling changes.
- Retrieval/vectorization coupling, project archive behaviors, provider/model routing,
  content-mode/minors updates, and safety-bypass behavior remain explicitly unchanged by Phase 151.
