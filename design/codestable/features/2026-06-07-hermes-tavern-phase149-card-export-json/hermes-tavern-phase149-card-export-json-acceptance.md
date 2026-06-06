---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase149-card-export-json"
status: accepted
date: "2026-06-07"
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
tags: [hermes-tavern, card, export, acceptance, offline]
---
# Phase 149 Card Export JSON Acceptance

> 阶段：S2 验收/写回
> 验收日期：2026-06-07
> 关联设计文档：design/codestable/features/2026-06-07-hermes-tavern-phase149-card-export-json/design.md
> 关联 checklist：design/codestable/features/2026-06-07-hermes-tavern-phase149-card-export-json/checklist.yaml
> Codex architect artifact：/tmp/hermes-tavern-architect-phase149-s2.jsonl
> Codex executor artifact：/tmp/hermes-tavern-executor-phase149-s2.jsonl

## 1. Scope and S1 implementation contract

- S1 is accepted as a bounded local card-export surface:
  - Adds `/rp card export <card>` under the existing card command family.
  - Resolves one stored card via existing `TavernStore.get_card(...)`, including `last`.
  - Writes one UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/cards`.
  - Prefers preserved `cards.data_json.raw` when it is a JSON object; otherwise writes a normalized SillyTavern-compatible fallback payload.
  - Returns both `file: <path>` and quoted `MEDIA:"<path>"` output.
- S2 writes only CodeStable/current-state docs and status metadata. It does not edit source, tests, README, plugins, build artifacts, or Hermes core files.

## 2. Interface/schema contract

- Existing persistent card storage remains `cards(id, name, data_json, source_path, created_at)`.
- Existing stored-card lookup remains `TavernStore.get_card(card_id_or_name)`, including the existing `last` resolver behavior.
- Phase 149 introduces no schema/table/index/migration and no new runtime DB API.
- Exported JSON is generated from an existing card row only; no card row is edited while exporting.

## 3. Command/output contract

- Command: `/rp card export <card>`.
- Missing argument response: `Usage: /rp card export <card>`.
- Missing card response preserves existing card-not-found semantics, including the `last` no-card message.
- Success response starts with `Card exported as JSON.` and includes:
  - `file: <path>`
  - `MEDIA:"<path>"`
- Generated `/rp help` and README Core-command visibility were implemented and tested in S1; S2 leaves README unchanged.

## 4. No-session behavior

- `/rp card export <card>` works without an active RP session.
- It does not create, start, switch, bind, or mutate sessions.
- It does not append, edit, or delete messages.
- It does not alter active-session greeting, start, retry, undo, or turn-control behavior.

## 5. Export placement and MEDIA contract

- Export directory is profile-safe: `get_hermes_home()/plugins/hermes-tavern/exports/cards`.
- File names use sanitized `card_<id>.json` material and stay inside the cards export directory, including path-like card IDs.
- JSON is written as UTF-8 with `ensure_ascii=False` and stable indentation.
- The quoted `MEDIA:"<path>"` marker preserves attachment paths with spaces and matches the existing gateway media-delivery contract.
- Exports do not include raw event JSON or raw message metadata blobs.

## 6. Raw/fallback behavior

- If `data_json.raw` is a JSON object/dict, Phase 149 exports that preserved raw card payload.
- If `raw` is absent or not an object, Phase 149 exports a normalized SillyTavern-compatible fallback with `spec: chara_card_v2`, `spec_version: 3.0`, and normalized `data` fields from the stored card row.
- The fallback path is local/offline and does not call importers, validators, model providers, generation paths, prompt assembly, retrieval, or vectorization.

## 7. Help/README visibility evidence

- `src/hermes_tavern/commands.py` generated help includes `/rp card export <card>`.
- `tests/test_hermes_tavern_commands.py` asserts generated help visibility.
- `README.md` Core commands include `/rp card export <card>` from S1, and `tests/test_hermes_tavern_readme_docs.py` guards the literal.
- S2 intentionally does not edit README; current README visibility evidence is carried by S1 tests.

## 8. Reverse-scope / no-leak boundaries

Phase 149 remains limited to one stored-card JSON export and does not add or change:

- PNG card export.
- Bulk card export.
- Project archive ZIP export/import.
- Card editing, deletion, merge, or validation tooling.
- Session/project export semantics beyond this one-card JSON command.
- Card/session/message mutation.
- Prompt/debug/context-budget behavior.
- Provider/model routing, generation, credentials, media/TTS/image provider behavior.
- Retrieval/vectorization, automatic extraction, graph, archive/import workflow, or content-mode behavior.
- Minors/underage handling or safety-bypass behavior.
- Plugin registration, build artifacts, or protected Hermes core files.

## 9. Architecture and root-design writeback

- `design/codestable/architecture/ARCHITECTURE.md` is updated for:
  - Last updated date: 2026-06-07.
  - Phase 149 capability summary.
  - `/rp command surface (current through Phase 149)` and `/rp card ... export <card>` command line.
  - DB heading current through Phase 149 with no schema changes.
  - Phase 149 data/behavior paragraph near existing card-storage prose.
  - `Tavern export MEDIA contract` extended to `/rp card export <card>`.
  - Phase 149 boundary bullet preserving schema, prompt/provider/generation, retrieval/vectorization, credentials, content-mode, minors/underage, other archive/import/export, and safety-bypass boundaries.
- `design/HERMES_TAVERN_DESIGN.md` is updated for:
  - §6.2 current Phase 149 card-export paragraph.
  - §16.1 current Character Card storage/export semantics (`data_json.raw` preference + normalized fallback + no schema changes).
  - §17.1/§17.2 current Phase 121–149 export/import wording with project archive ZIP/import still deferred.

## 10. Requirement and roadmap writeback

- Phase 149 `design.md` has no `requirement`, `roadmap`, or `roadmap_item` frontmatter keys.
- No requirement or roadmap files are updated in S2.

## 11. Attention candidates

- No new `attention.md` candidates were discovered.
- Existing attention entries already cover protected Hermes core paths and profile-safe `get_hermes_home()` path usage.

## 12. Verification ledger

### 12.1 Prior S1 controller results

| Command / guard | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/commands.py src/hermes_tavern/runtime_assets.py tests/test_hermes_tavern_card_export.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` | passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_card_export.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | 102 passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | 1073 passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | 1073 passed |
| Protected-path diff guard | passed; empty |
| `git diff --check` | passed |

### 12.2 S2 controller verification

| Command / guard | Result |
|---|---|
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase149-card-export-json/design.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-07-hermes-tavern-phase149-card-export-json/hermes-tavern-phase149-card-export-json-acceptance.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-07-hermes-tavern-phase149-card-export-json/checklist.yaml` | passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/commands.py src/hermes_tavern/runtime_assets.py tests/test_hermes_tavern_card_export.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` | passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_card_export.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | 102 passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | 1073 passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | 1073 passed |
| `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py plugins build/lib` | passed; empty |
| Current-doc stale wording guard for old Phase 148/121-147 range labels and planned/pending Phase 149 wording | passed; empty in current Phase 149 docs, architecture, and root design |
| Current wording guard for `/rp card export <card>`, `Phase 149`, `MEDIA:"<path>"`, `exports/cards`, `data_json.raw`, and normalized fallback | passed; expected current hits |
| `git diff --check` | passed |

## 13. Residual deferred work

- PNG card export.
- Bulk card export.
- Project archive ZIP export/import.
- Card editing/deletion/merge and validation tooling.
- Provider/model/generation changes.
- Retrieval/vectorization coupling.
- Content-mode and minors/underage behavior.
- Safety-bypass-related behavior remains out of scope.
