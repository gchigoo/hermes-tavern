---
doc_type: feature-acceptance
feature: "2026-06-04-hermes-tavern-phase128-project-outline"
status: accepted
date: "2026-06-04"
summary: >
  Phase 128 Project Outline v1 includes local project outline persistence,
  `/rp project outline` command surface, project-info/export visibility, and S3
  architecture/root-design writeback. Controller verification passed while prompt
  assembly, provider routing, content mode, generation, credentials, protected
  core files, and deferred outline-generation boundaries remain unchanged.
tags: [novel, project, outline, metadata, export, acceptance]
---

# Phase 128: Project Outline v1 Acceptance

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-06-04
> 关联方案：design/codestable/features/2026-06-04-hermes-tavern-phase128-project-outline/design.md

## 1. Interface Contract Check

- Side table `novel_project_outlines(id, project_id, outline_text, created_at, updated_at)` exists and is uniquely indexed by `project_id`.
- Required schema literal is present:
  - `CREATE INDEX idx_novel_project_outlines_project ON novel_project_outlines(project_id)`
- Required command literals are present in code/help/docs:
  - `/rp project outline [project-id]`
  - `/rp project outline inspect [project-id]`
  - `/rp project outline set [project-id] <text>`
  - `/rp project outline clear [project-id]`
- `/rp project info <id>` shows outline preview only when an outline exists.
- Export adds `## Outline` only when text exists and places it after `## Project Brief` before `## Style Guide` and `## Chapters`.
- Outline is metadata-only: not included in prompt assembly, provider routing, model/profile behavior, content mode, or generation control.

## 2. S1 Evidence (Persist/Export)

- Implemented in `src/hermes_tavern/db_novel.py`.
  - Added `novel_project_outlines` table and `idx_novel_project_outlines_project` index.
  - Added `set_project_outline`, `get_project_outline`, `clear_project_outline`.
  - Added optional `## Outline` export section.
- Focused DB tests:
  - `python -m pytest tests/test_hermes_tavern_novel_db.py -q -o 'addopts=' -k "outline or migrat"` (6 passed).
- Full novel DB tests: `36 passed`.
- Full plugin suite test slice in this feature run: `860 passed`.
- Reverse-scope evidence in prior S1 report:
  - `src/hermes_tavern/db_novel.py` and `tests/test_hermes_tavern_novel_db.py` only.
  - No prompt/provider/model/content-mode/generation edits.

## 3. S2 Evidence (Runtime/Help/Docs)

- Implemented in `src/hermes_tavern/runtime_novel.py` and `src/hermes_tavern/commands.py`.
- Runtime/help/docs checks were completed:
  - Outline command routing with active-project fallback/usage/missing project states.
  - `/rp project info` outline preview behavior.
  - `/rp project outline` command visibility in `/rp help` and README literals.
  - No outline leak in `/rp debug prompt` and `/rp debug context`.
- Focused runtime docs tests passed for outline in:
  - `tests/test_hermes_tavern_novel_runtime.py`
  - `tests/test_hermes_tavern_commands.py`
  - `tests/test_hermes_tavern_readme_docs.py`

## 4. S3 Evidence (Writeback and acceptance docs)

- Updated writeback artifacts:
  - `design/codestable/architecture/ARCHITECTURE.md`
  - `design/HERMES_TAVERN_DESIGN.md`
  - `design/codestable/features/2026-06-04-hermes-tavern-phase128-project-outline/design.md`
  - `design/codestable/features/2026-06-04-hermes-tavern-phase128-project-outline/checklist.yaml`
  - `...-acceptance.md` (this file)
- S3 checklist and architecture/root design status are finalized after controller
  verification.

## 5. Acceptance Scenario Check

- [x] S1-C1: scope and migration constraints satisfied.
- [x] S1-C2: persistence contract and local side-table behavior satisfied.
- [x] S2-C3: project outline command contract satisfied.
- [x] S2-C4: info/export visibility behavior satisfied.
- [x] S2-C5: no prompt/provider/content-mode/generation behavior regression.
- [x] S3-C1: checklist precondition and writeback completion verified.
- [x] S3-C6: reverse-scope/protected-core verification passed.

## 6. Deferred Boundaries And Residuals

- Still deferred: structured beat/arc engine, outline generation, rewrite/expand/compress, canon policy metadata, project content-mode/default-card/default-preset/default-lorebook defaults, archive ZIP import/export, character/relationship states, cloud/collaboration, minors/underage handling paths, provider safety bypass.
- Provider routing, prompt assembly, generation behavior, credential persistence, and protected-core editing remain outside this phase.

## 7. Controller Verification

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` — passed, 177 tests.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` — passed, 868 tests.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` — passed, 868 tests.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase128-project-outline/design.md --require doc_type --require status --require feature` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase128-project-outline/hermes-tavern-phase128-project-outline-acceptance.md --require doc_type --require status --require feature` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-04-hermes-tavern-phase128-project-outline/checklist.yaml` — passed.
- `git diff --name-only -- run_agent.py cli.py gateway/run.py` — passed, no protected core diffs.
- `git diff --check` — passed.

## 8. Stage Status

- Overall report status: `accepted`; Phase 128 Project Outline v1 is closed.
