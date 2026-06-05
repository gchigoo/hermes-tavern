---
doc_type: feature-acceptance
feature: "2026-06-05-hermes-tavern-phase132-location-metadata"
status: accepted
date: "2026-06-05"
summary: >
  Phase 132 Location Metadata v1 is accepted. S1 implemented local
  project-scoped location persistence, `/rp location ...` commands,
  help/README visibility, optional `## Locations` Markdown export, and no-leak
  tests. S2 verified the implementation, finalized the checklist, and merged the
  current metadata/export-only boundary into architecture and root design docs.
---

# Phase 132: Location Metadata v1 — Acceptance Report

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-06-05
> 关联方案 doc：`design/codestable/features/2026-06-05-hermes-tavern-phase132-location-metadata/design.md`
> Implementation commit under review：`c65e5f7 feat: add tavern location metadata`
> Architect artifact：`/tmp/hermes-tavern-architect-phase132-s2.jsonl`
> Executor artifact：`/tmp/hermes-tavern-executor-phase132-s2.jsonl`

## 1. 接口契约核对

- [x] `NovelStore.create_location(project_id, label, description_text)`：stores one local project-scoped row in `novel_locations`; S1 DB tests cover valid create/list and missing-project behavior.
- [x] `NovelStore.list_locations(project_id)`：returns project rows for display/export; S1 DB/runtime tests cover explicit project list and active-project fallback through the command layer.
- [x] `NovelStore.get_location(location_id)`：retrieves by location ID only; runtime inspect tests cover bounded not-found behavior.
- [x] `NovelStore.update_location(location_id, description_text)`：updates `description_text` only; label rename stays deferred.
- [x] `NovelStore.delete_location(location_id)`：deletes by ID with bounded missing-row behavior.
- [x] `/rp location add <project-id> <label> <description...>` requires an explicit project ID, stores the full description text, and returns a compact confirmation.
- [x] `/rp location list [project-id]` supports explicit project IDs and active-project fallback for list only.
- [x] `/rp location inspect/update/delete <location-id>` operate by row ID and return bounded usage/not-found messages.
- [x] Markdown export emits optional `## Locations` only when rows exist, after `## Style Guide` and before `## Characters` / `## Relationships` / chapter sections.
- [x] `/rp help` and README Core commands expose the location literals added in S1.

## 2. 行为与决策核对

- [x] Location Metadata means a user-authored local note describing a fictional project location; it is not map rendering, geocoding, retrieval memory, prompt injection, an ST asset binding, coordinates, or an address parser.
- [x] Location labels remain compact user labels. No age/date-of-birth/minor/underage/school-grade fields, examples, tests, or commands were added by Phase 132.
- [x] Location metadata is local metadata and optional Markdown export only. It is excluded from prompt assembly, session prompt-module selection, `/rp debug prompt`, `/rp debug context`, context-budget payloads, vectorization/retrieval, provider/model routing, content mode, credentials, automation, summarization, cloud/collaboration, and generation.
- [x] S1 implementation stayed in the intended plugin/source/docs/test files. S2 stayed docs/status-only.
- [x] `run_agent.py`, `cli.py`, `gateway/run.py`, README, source, tests, prompt/provider/model/generation/runtime-debug/context-budget paths, ST importer/exporter paths, and build artifacts have no Phase 132 S2 diff.

## 3. 验收场景核对

Controller-run verification:

- [x] Focused Phase 132 command/DB/docs tests:
  - `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
  - Result: `232 passed in 7.23s`.
- [x] Tavern plugin glob tests:
  - `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
  - Result: `923 passed in 41.82s`.
- [x] Full registry gate:
  - `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
  - Result: `923 passed in 43.12s`.
- [x] Design frontmatter validation:
  - `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase132-location-metadata/design.md --require doc_type --require status --require feature`
  - Result: passed.
- [x] Acceptance frontmatter validation:
  - `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase132-location-metadata/hermes-tavern-phase132-location-metadata-acceptance.md --require doc_type --require status --require feature`
  - Result: passed after controller finalization.
- [x] Checklist YAML validation:
  - `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-05-hermes-tavern-phase132-location-metadata/checklist.yaml`
  - Result: passed after controller finalization.
- [x] Reverse-scope/prohibited-path guard:
  - `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py build/lib`
  - `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_content.py src/hermes_tavern/importers build/lib`
  - Result: both empty.
- [x] Stale-current/deferred wording guard on current architecture/root-design docs:
  - `rg -n "current through Phase 131|Phase 121-131|Phase 121–131|Future sub-objects from the original vision remain deferred: locations|locations, organizations|Project Brief, Project Outline, Relationship State, and Character State metadata are|Relationship and character-state metadata remain" design/codestable/architecture/ARCHITECTURE.md design/HERMES_TAVERN_DESIGN.md`
  - Result: no matches.
- [x] Whitespace guard:
  - `git diff --check`
  - Result: passed.

## 4. 术语一致性

- [x] `Location Metadata` / `location metadata` consistently refers to project-scoped local metadata rows and optional export content.
- [x] `Location Label` remains a compact one-token user label; docs do not reframe it as coordinates, an address parser, map/geocoding metadata, ST asset binding, or retrieval memory.
- [x] `novel_locations` is the table name in architecture/root design writeback.
- [x] Stale root-design wording that listed locations as a deferred future sub-object was removed; organizations, plot threads, relationship graph/rename/automatic extraction, and style samples remain deferred.

## 5. 架构归并

- [x] `design/codestable/architecture/ARCHITECTURE.md` now includes Phase 132 in the capability summary.
- [x] `ARCHITECTURE.md` module summaries mention location CRUD/export and command handling through `db_novel.py` / `runtime_novel.py`.
- [x] `ARCHITECTURE.md` command surface is current through Phase 132 and lists `/rp location add/list/inspect/update/delete`.
- [x] `ARCHITECTURE.md` DB schema lists `novel_locations(id, project_id, label, description_text, created_at, updated_at)` and `idx_novel_locations_project`.
- [x] `ARCHITECTURE.md` metadata boundary notes state Location Metadata is excluded from prompt/debug/context-budget/vectorization/retrieval/provider/model/content-mode/credential/automation/summarization/generation paths and visible only through commands/Markdown export.
- [x] `design/HERMES_TAVERN_DESIGN.md` now marks locations as current local metadata, adds command literals, documents `## Locations` export placement, records DB/index shape, and preserves map/geocoding/address/asset-binding/import-export automation as out of scope.

## 6. requirement 回写

- [x] Skipped. The Phase 132 design has no `requirement` frontmatter, and this S2 slice does not create or update requirement artifacts.

## 7. roadmap 回写

- [x] Skipped. The Phase 132 design has no `roadmap` / `roadmap_item` frontmatter, and this S2 slice does not create or update roadmap artifacts.

## 8. attention.md 候选盘点

- [x] No `attention.md` candidate. The project-level constraints already cover protected core files, credential handling, and adult-fiction boundaries; Phase 132 did not introduce a reusable workflow pitfall that every future feature needs at startup.

## 9. 遗留

- Organizations, plot threads, relationship graph/rename/automatic extraction, style samples, canon/content-mode/default-binding metadata, archive ZIP/import, cloud/collaboration, retrieval/vectorization, summarization automation, provider/model routing, content-mode behavior, credential persistence, generation behavior, maps/geocoding/coordinates/address parsing, and ST asset binding remain out of Phase 132 scope.
- The executor JSONL contains one failed shell-quote probe while inspecting Markdown fences; it did not affect the final docs/status output, and controller verification ran from scratch.
- No follow-up issue is required for S2 acceptance closure.
