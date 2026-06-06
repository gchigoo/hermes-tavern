---
doc_type: feature-acceptance
feature: "2026-06-06-hermes-tavern-phase147-project-inspect-alias"
status: accepted
date: "2026-06-06"
created: "2026-06-06"
updated: "2026-06-06"
owner: codestable-cron
tags: [hermes-tavern, project, command-surface, read-only, offline]
---
# Phase 147 Project Inspect Alias Acceptance

> 阶段：S2 验收/写回
> 验收日期：2026-06-06
> 关联设计文档：design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/design.md
> 关联 checklist：design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/checklist.yaml
> Codex architect artifact：/tmp/hermes-tavern-architect-phase147-s2.jsonl
> Codex executor artifact：/tmp/hermes-tavern-executor-phase147-s2.jsonl

## 1. Scope and S1 contract

- S1 contract is accepted as a bounded read-only project inspection alias:
  - `/rp project inspect <project-id>`
  - nested under the existing `/rp project ...` command family
  - delegated through the existing `/rp project info <id>` rendering path
  - no new persistence helper, schema, export, prompt, provider, retrieval, or safety behavior
- S1 evidence files were source/test/README changes from the implementation slice:
  - `src/hermes_tavern/runtime_novel.py`
  - `src/hermes_tavern/commands.py`
  - `tests/test_hermes_tavern_novel_runtime.py`
  - `tests/test_hermes_tavern_commands.py`
  - `tests/test_hermes_tavern_readme_docs.py`
  - `README.md`
- S2 docs/status/writeback files in scope for this closeout pass:
  - `design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/design.md`
  - `design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/checklist.yaml`
  - `design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/hermes-tavern-phase147-project-inspect-alias-acceptance.md`
  - `design/codestable/architecture/ARCHITECTURE.md`
  - `design/HERMES_TAVERN_DESIGN.md`
- S2 did not edit source/tests/README/core/plugin/build paths.

## 2. Store/interface contract

- `/rp project inspect <project-id>` reuses the existing project info path rather than adding a second renderer.
- The implementation routes inspect to `project_info(...)`; `project_info(...)` uses:
  - `runtime.store.get_project(project_id)` for the base row and chapter count.
  - existing project brief getter behavior for `project_type` / `premise` previews when present.
  - existing project outline getter behavior for outline preview when present.
- The alias returns the same visible project metadata as `/rp project info <id>` for the same row.
- S2 writeback does not introduce DB/helper/schema/index/order/export/read APIs.

## 3. Command/help/README behavior contract

- `/rp project inspect <project-id>` is nested under the existing project family.
- `/rp project info <id>` remains supported and behavior-compatible.
- Missing, malformed, non-positive, and extra inspect arguments return bounded project usage text that includes the inspect form.
- Missing project rows return `No novel project found: <id>` without exception details.
- S1 generated help and README Core commands were already updated for user visibility; S2 only currentized architecture/root-design narrative and CodeStable status docs.

## 4. Adjacent project behavior regression contract

- The following adjacent project-family contracts remain unchanged:
  - `/rp project create/list/info/set/export`
  - `/rp project style ...`
  - `/rp project brief ...`
  - `/rp project outline ...`
  - `/rp project revision ...`
- `/rp project inspect <project-id>` does not mutate project title, summary, status, style guide, brief, outline, revision notes, chapters, scenes, or export output.
- Markdown export behavior remains unchanged in this phase.

## 5. Deferred/no-leak boundary

Phase 147 remains bounded to command-visible metadata inspection and does not add:

- project update/delete/archive ZIP/import/export expansion
- cloud/collaboration workflow
- relationship graph/aliases/merge-split behavior
- automatic extraction
- prompt/debug/context-budget injection
- provider/model routing changes
- generation behavior
- retrieval/vectorization coupling
- credential persistence
- content-mode behavior changes
- minors/underage policy flow changes
- provider-safety bypass behavior
- plugin shim/build artifact behavior

## 6. Architecture and root-design writeback

- `design/codestable/architecture/ARCHITECTURE.md` now records:
  - `/rp command surface` current through Phase 147.
  - `DB schema` current through Phase 147 while explicitly unchanged by Phase 147.
  - `/rp project inspect <project-id>` in the current command surface.
  - a Phase 147 boundary bullet for read-only project inspection over existing `novel_projects` rows.
  - reuse of the existing `/rp project info <id>` rendering/getter path (`get_project(project_id)` plus brief/outline preview getters).
- `design/HERMES_TAVERN_DESIGN.md` now records:
  - `/rp project inspect <project-id>` in the long project command inventory.
  - `/rp project inspect <project-id>` in the compact writing commands section.
  - Phase 147 read-only project-inspect prose near the chapter/scene/timeline inspect paragraphs.
  - Phase 147 data-model prose tied to existing project info/getter reuse.
  - current Phase 121–147 export-scope wording while preserving Markdown-only export behavior.

## 7. Requirement and roadmap writeback

- `design.md` frontmatter has no `requirement`, `roadmap`, or `roadmap_item`.
- No requirement or roadmap files were updated in S2.

## 8. Attention candidates

- No new `attention.md` candidates were introduced by this S2 pass. Existing
  `attention.md` entries already cover protected path/process boundaries and
  runtime constraints.

## 9. Verification ledger

Controller reran verification after S2 docs/status/writeback edits and before finalizing checklist status:

| Command / guard | Result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` | passed |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` | 288 passed in 10.65s |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` | 1058 passed in 50.21s |
| `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` | 1058 passed in 53.28s |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/design.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/hermes-tavern-phase147-project-inspect-alias-acceptance.md --require doc_type --require status --require feature` | passed |
| `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/checklist.yaml` | passed |
| `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py plugins build/lib` | passed; empty output during S2 |
| Stale/current guard | passed after final status/writeback patch; current docs contain Phase 147 and `/rp project inspect <project-id>` while stale Phase 147 planned/pending wording is absent |
| `git diff --check` | passed |

Executor JSONL nuance: `/tmp/hermes-tavern-executor-phase147-s2.jsonl` contains one expected failed read of the not-yet-created acceptance report before the executor created it. The terminal stderr also showed recovered checklist `apply_patch` context misses. The final diff and controller reruns above are authoritative.

## 10. Residual and deferred work

Deferred boundaries remain for:

- project editing/deletion and lifecycle expansion
- project archive ZIP/export/import workflows beyond current Markdown export
- automatic extraction flows
- generation/provider/routing/retrieval/vectorization coupling
- prompt/debug/context-budget injection
- credential persistence and content-mode behavior changes
- minors/underage policy flow changes and safety-policy bypass behavior
