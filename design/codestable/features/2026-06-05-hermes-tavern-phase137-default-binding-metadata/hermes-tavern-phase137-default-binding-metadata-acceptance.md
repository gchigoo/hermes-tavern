---
doc_type: feature-acceptance
feature: "2026-06-05-hermes-tavern-phase137-default-binding-metadata"
status: accepted
date: "2026-06-05"
summary: >
  Phase 137 is accepted as Default Binding Metadata v1. It adds local,
  command-managed project/chapter/scene default-binding rows for card, preset,
  lorebook, and persona assets with command and Markdown export visibility only;
  controller verification confirms the rows are metadata-only/inert and do not
  affect prompts, sessions, providers, routing, content mode, or generation.
tags: [novel, metadata, bindings, export, acceptance]
---

# Phase 137 Default Binding Metadata v1 Acceptance

> Phase: S2 verify/accept/write current docs
> Controller verification date: 2026-06-05
> Design: `design/codestable/features/2026-06-05-hermes-tavern-phase137-default-binding-metadata/design.md`
> Checklist: `design/codestable/features/2026-06-05-hermes-tavern-phase137-default-binding-metadata/checklist.yaml`

## 1. Scope and design contract

Phase 137 is accepted as a local metadata feature. S1 implemented
`novel_default_bindings` and `/rp binding ...`; S2 closed acceptance/status and
project-level writeback only.

Accepted implementation surface:

- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/runtime.py` (minimal `_binding_command` shim only)
- `src/hermes_tavern/runtime_novel.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- focused DB/runtime/command/README docs tests

Accepted S2 status/writeback surface:

- this acceptance report
- `checklist.yaml` status/evidence updates
- Phase 137 `design.md` export-order correction to match implementation
- `design/codestable/architecture/ARCHITECTURE.md`
- `design/HERMES_TAVERN_DESIGN.md`

The feature remains metadata-only/inert. Default-binding rows are visible only
through `/rp binding ...` commands and project Markdown export.

## 2. Interface/schema contract核对

Accepted schema and helpers:

- `novel_default_bindings` is created in `src/hermes_tavern/db_novel.py` with
  `scope_type`, `scope_id`, `asset_type`, `asset_id`, timestamps, and
  `UNIQUE(scope_type, scope_id, asset_type)`.
- `asset_id` is stored as `TEXT`, preserving real string card/preset/lorebook/
  persona IDs instead of forcing integer IDs.
- `idx_novel_default_bindings_scope` indexes `(scope_type, scope_id)` for scoped
  lookup/export.
- Store helpers support `set_default_binding`, `list_default_bindings`,
  `list_default_bindings_for_project`, `get_default_binding`, and
  `clear_default_binding`.

Evidence:

- `tests/test_hermes_tavern_novel_db.py::test_migrate_creates_novel_tables`
  covers table creation, `asset_id` type, unique autoindex, and scope index.
- `tests/test_hermes_tavern_novel_db.py::test_default_binding_helpers_and_validations`
  covers project/chapter/scene scopes, card/preset/lorebook/persona assets,
  overwrite behavior, inspect/list/clear, and invalid/missing scope/asset errors.
- `tests/test_hermes_tavern_novel_db.py::test_default_binding_list_sorts_by_asset_type_and_asset_id`
  covers deterministic list ordering.
- `tests/test_hermes_tavern_novel_db.py::test_export_project_markdown_includes_default_bindings_and_excludes_other_projects`
  covers project-owned export discovery.

## 3. Command/export behavior核对

Accepted command surface:

- `/rp binding set <project|chapter|scene> <scope-id> <card|preset|lorebook|persona> <asset-id>`
- `/rp binding list <project|chapter|scene> <scope-id>`
- `/rp binding inspect <binding-id>`
- `/rp binding clear <binding-id>`

Evidence:

- `tests/test_hermes_tavern_commands.py::test_help_lists_binding_commands`
  verifies command-table help visibility.
- `tests/test_hermes_tavern_novel_runtime.py::test_project_command_help_includes_binding_lines`
  verifies runtime help surfaces the binding literals and metadata-only/inert note.
- `tests/test_hermes_tavern_novel_runtime.py::test_binding_routes_set_list_inspect_and_clear`
  verifies set/list/inspect/clear routing through the minimal runtime shim.
- `tests/test_hermes_tavern_novel_runtime.py::test_binding_command_validation_and_lookup_errors`
  verifies bounded command validation and lookup errors.
- `tests/test_hermes_tavern_readme_docs.py::test_readme_core_commands_include_binding_literals`
  verifies README core-command visibility and the “not auto-applied” boundary.

Accepted export behavior:

- `## Default Bindings` is emitted only when relevant rows exist.
- Export rows include bindings for the exported project plus its chapters and
  scenes, and exclude rows from other projects.
- Implemented placement is after `## Relationships` and before `## Chapters`,
  with `## Canon` and `## Timeline` still emitted after chapters by the existing
  export flow.

Evidence:

- `tests/test_hermes_tavern_novel_db.py::test_export_project_markdown_includes_default_bindings_and_excludes_other_projects`
- `tests/test_hermes_tavern_novel_db.py::test_export_project_markdown_omits_default_bindings_when_empty`

## 4. Acceptance criteria核对

- [x] AC1 — migration creates `novel_default_bindings`, unique scope/asset
  constraint, and scope index.
- [x] AC2 — helpers set, replace, list, inspect, and clear rows for project,
  chapter, and scene scopes.
- [x] AC3 — helpers validate missing scopes and missing assets with bounded
  behavior.
- [x] AC4 — `/rp binding set/list/inspect/clear` commands exist in help output
  and return compact metadata-only messages.
- [x] AC5 — README core commands and command/docs tests include binding literals.
- [x] AC6 — Markdown export emits optional `## Default Bindings` only when rows
  exist.
- [x] AC7 — export includes only the selected project, chapter, and scene binding
  rows and excludes another project's rows.
- [x] AC8 — binding marker text does not appear in `/rp debug prompt`,
  `/rp debug context`, active prompt modules, provider routing, or generation
  paths.
- [x] AC9 — focused and plugin-wide offline tests pass without network/provider
  calls.
- [x] AC10 — reverse-scope checks show no protected core, build artifact,
  provider/model/content/generation/credential/retrieval/vectorization/media,
  archive, ST importer/exporter, graph, automatic extraction, or safety-bypass
  changes.

## 5. Checklist C1-C5核对

- [x] C1 active checklist precondition: Phase 137 remained the active feature and
  no unrelated feature was advanced in this tick.
- [x] C2 metadata table and helpers: DB migration/helper tests pass.
- [x] C3 command visibility: command table, runtime help, README docs, and route
  tests pass.
- [x] C4 export visibility: optional omission and cross-project exclusion tests
  pass.
- [x] C5 no prompt/provider side effects: no-leak runtime test plus reverse-scope
  guard pass.

## 6. Architecture/root-design writeback

Architecture writeback completed in `design/codestable/architecture/ARCHITECTURE.md`:

- command surface headings now reflect current through Phase 137;
- Phase 137 summary documents `/rp binding set/list/inspect/clear`;
- DB schema includes `novel_default_bindings`, its unique scope/asset constraint,
  and `idx_novel_default_bindings_scope`;
- metadata-only boundary text excludes prompt/debug/context-budget,
  vectorization/retrieval, provider/model routing, content mode, credentials,
  automation/summarization, generation, media/TTS/image, archive, ST importer/
  exporter, graph, and safety-bypass behavior.

Root design writeback completed in `design/HERMES_TAVERN_DESIGN.md`:

- command-managed `novel_default_bindings` is current local metadata;
- automatic scalar defaults (`default_card_id`, `default_preset_id`,
  `default_lorebook_ids`) and automatic default application remain deferred;
- stale `Phase 121–135` Markdown-export wording is now Phase 121–137;
- `## Default Bindings` export placement is documented after Relationships and
  before Chapters;
- ST importer/exporter compatibility remains unchanged.

No requirement or roadmap file exists for this feature, so requirement/roadmap
writeback is not applicable.

## 7. Controller verification evidence

Controller reran the gates from scratch after the Codex S2 docs/status draft and
controller stale-wording patch:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` — passed, 280 tests.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` — passed, 971 tests.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` — passed, 971 tests.
- CodeStable validators for `design.md`, this acceptance report, and
  `checklist.yaml` — passed after final status updates.
- Protected reverse-scope diff guard for `README.md`, `src`, `tests`, `plugins`,
  `run_agent.py`, `cli.py`, `gateway/run.py`, and `build/lib` — empty output.
- Stale-wording scans for old Phase 135/121–135 and deferred default-binding
  phrases in current docs — empty output after controller patch.
- `git diff --check` — passed.

## 8. Attention candidates

No new project-wide command, environment, or workflow trap was discovered in
this S2 acceptance slice. Existing attention notes already cover `-o 'addopts='`,
profile-safe paths, no protected core edits, and the Tavern plugin boundary.

## 9. Residual/deferred work

Deferred by design:

- automatic prompt/session/default asset application;
- scalar default fields such as `default_card_id`, `default_preset_id`, and
  `default_lorebook_ids`;
- cascading cleanup when a referenced asset is deleted;
- archive ZIP/import/export, ST asset importer/exporter changes, relationship
  graph/rename, automatic extraction, vectorization/retrieval coupling,
  provider/model routing, content-mode coupling, generation behavior, cloud or
  collaboration workflows, and safety-bypass behavior.

No implementation blocker remains for Phase 137.
