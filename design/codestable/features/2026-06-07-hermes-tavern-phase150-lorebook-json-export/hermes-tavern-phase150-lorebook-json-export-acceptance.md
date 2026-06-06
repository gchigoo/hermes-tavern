---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase150-lorebook-json-export"
status: accepted
date: "2026-06-07"
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
tags: [hermes-tavern, lorebook, export, acceptance, offline]
---

# Phase 150 Lorebook JSON Export Acceptance

> 阶段：S2 验收/写回
> 验收日期：2026-06-07
> 关联设计文档：design/codestable/features/2026-06-07-hermes-tavern-phase150-lorebook-json-export/design.md
> 关联 checklist：design/codestable/features/2026-06-07-hermes-tavern-phase150-lorebook-json-export/checklist.yaml
> Codex architect artifact：/tmp/hermes-tavern-architect-phase150-s2.jsonl
> Codex executor artifact：/tmp/hermes-tavern-executor-phase150-s2.jsonl

## 1. S1 scope contract

- S1 is implemented as one bounded local `/rp lore export <lorebook>` command for one existing stored lorebook.
- Implementation resolves lorebooks through existing `TavernStore.get_lorebook(...)` behavior, including `last`.
- It writes a UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/lorebooks`.
- It prefers `lorebooks.raw_json` when that value is a JSON object; otherwise it uses a normalized fallback assembled from the lorebook row + `list_lorebook_entries(...)`.
- Success output includes `file:` plus quoted `MEDIA:"<path>"`.
- S2 is documentation-only and does not alter source/runtime/tests/README/core/plugin/build artifact files.

## 2. Interface/schema contract

- No schema/table/index/migration files were changed in S2; feature implementation remains on top of existing `lorebooks` and `lorebook_entries` shape.
- S1 read path still uses `TavernStore.get_lorebook(... )`, and no new DB APIs were introduced.
- `lorebooks(id, name, source, raw_json, created_at)` and
  `lorebook_entries(...)` remain unchanged by Phase 150.
- S2 checks do not apply code mutations to DB schema or data model layers.

## 3. Command/output contract

- Command path: `/rp lore export <lorebook>`.
- Missing argument form returns `Usage: /rp lore export <lorebook>`.
- Missing lorebook returns the existing bounded not-found messaging used by lore lookup and supports existing `last` no-lorebook behavior.
- Success output includes:
  - `Lorebook exported as JSON.`
  - `file: <path>`
  - `MEDIA:"<path>"`
- Existing command-family behavior remains under `/rp lore ...`.

## 4. No-session / no-mutation behavior

- The command runs command-only, no active-session requirement.
- It does not create, switch, or mutate any session/message rows.
- It does not mutate stored lorebook or lorebook-entry rows.
- It does not mutate schema, prompts, provider/model routing, generation, retrieval/vectorization, or credentials.
- Existing S1 tests assert session/message invariance for export operations.

## 5. Export placement / MEDIA / path containment

- Exports are written to profile-safe path:
  `get_hermes_home()/plugins/hermes-tavern/exports/lorebooks`.
- Filename generation is sanitized (`lorebook_<id>.json`) and stays under that directory.
- JSON is written as UTF-8 with pretty formatting.
- Response uses quoted MEDIA marker, preserving spaces in paths and matching Tavern media-delivery contract.

## 6. Raw/fallback behavior

- If `lorebooks.raw_json` is a JSON object, it is exported as preserved payload (pretty-formatted).
- If `raw_json` is missing, invalid JSON, or not an object, export falls back to:
  - lorebook top-level fields (`name`, `source`),
  - normalized `entries` array from stored `lorebook_entries` row fields:
    `title`, `content`, `keys`, `secondary_keys`, `enabled`, `constant`, `regex`,
    `position`, `insertion_order`, `priority`, `probability`.
- This fallback path is deterministic, local, and does not require import or provider flows.

## 7. Help/README evidence

- S1 added `/rp lore export <lorebook>` to generated command help.
- S1 added core README command documentation.
- S2 does not re-edit README or source; it records those prior S1 evidence points for controller handoff.

## 8. Reverse-scope / no-leak boundaries

Phase 150 remains scoped to one lorebook export and does not implement:

- project archive ZIP export/import
- ST lorebook importer format transformation
- card export/preset export parity changes
- session/message editing, project lifecycle writes, or generation-path effects
- regex matching behavior changes
- provider/model routing, credential resolution, content-mode/minors/underage changes
- safety-bypass behavior changes

No prompt debug/context budgets, retrieval/vectorization, or prompt-module pipelines are changed for this command.

## 9. Architecture / root-design writeback

- `design/codestable/architecture/ARCHITECTURE.md` writeback includes:
  - `/rp command surface (current through Phase 150)` and lore command extension with `export <lorebook>`.
  - New Phase 150 bullet describing `/rp lore export <lorebook>` behavior.
  - DB heading updated to `current through Phase 150; unchanged by Phase 150`.
  - `Tavern export MEDIA contract` extended with `/rp lore export <lorebook>`.
  - New Phase 150 lore export boundary bullet and path/behavior summary.
- `design/HERMES_TAVERN_DESIGN.md` writeback includes:
  - `§6.6` lore command list and behavior paragraph for lore export.
  - `§17.1/§17.2` current-phase wording moved to 121–150.
  - Exporter wording updated from bare `lorebook export JSON` to `/rp lore export <lorebook> lorebook export JSON`.

## 10. Requirement / roadmap writeback

- `design/codestable/features/2026-06-07-hermes-tavern-phase150-lorebook-json-export/design.md` has no `requirement`, `roadmap`, or `roadmap_item`.
- No requirements/roadmaps are updated in S2.

## 11. Attention candidates

- No new `attention.md` candidate identified for this pass.
- Existing repository-level attentions (profile-safe path discipline, protected file constraints) remain sufficient for this S2 closeout pass.

## 12. Verification ledger

### 12.1 S1 controller results (factual)

| Command / guard | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_lore.py src/hermes_tavern/commands.py tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` | passed (2026-06-07 controller) |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | `105 passed` (2026-06-07 controller) |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | `1080 passed` (2026-06-07 controller) |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | `1080 passed` (2026-06-07 controller) |
| Protected-path reverse-scope guard for S1 source/runtime boundaries | returned empty diff |
| `git diff --check` | passed |

### 12.2 S2 controller verification

| Command / guard | Result |
|---|---|
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase150-lorebook-json-export/design.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase150-lorebook-json-export/hermes-tavern-phase150-lorebook-json-export-acceptance.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-07-hermes-tavern-phase150-lorebook-json-export/checklist.yaml` | passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_lore.py src/hermes_tavern/commands.py tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` | passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_lore_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | `105 passed` |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | `1080 passed` |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | `1080 passed` |
| Protected-path diff guard for README/source/tests/core/plugin/build paths | passed; empty output |
| Current-doc stale wording guard for old Phase 149 / Phase 121–149 current-state labels in current architecture/root-design/Phase 150 docs | passed; no current-doc hits |
| Current wording guard for `/rp lore export <lorebook>`, `Phase 150`, `exports/lorebooks`, `lorebooks.raw_json`, normalized fallback, and quoted `MEDIA:\"<path>\"` | passed; expected current hits |
| `git diff --check` | passed |

## 13. Residual deferred work

- Single-lorebook export is implemented; broader lore tooling remains deferred:
  lorebook bulk export, lorebook import/export workflow conversion, project archive ZIP importer/exporter, and broader extraction/tooling changes.
- Retrieval/vectorization coupling, project archive behaviors, provider/model routing,
  content-mode/minors updates, and safety-bypass behavior remain explicitly unchanged by Phase 150.
