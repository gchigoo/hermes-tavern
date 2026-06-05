---
doc_type: feature-acceptance
feature: "2026-06-04-hermes-tavern-phase130-relationship-state-metadata"
status: accepted
date: "2026-06-05"
summary: >
  Phase 130 Relationship State Metadata v1 is accepted: local project-scoped
  relationship notes are managed via `/rp relationship ...`, backed by
  `novel_relationship_states`, exported as optional `## Relationships`, and
  verified to remain outside prompt/debug/provider/generation/context-budget/
  vectorization/retrieval paths.
tags: [novel, relationship, metadata, export, offline, acceptance]
---

# Phase 130: Relationship State Metadata v1 Acceptance

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-06-05
> 关联方案：design/codestable/features/2026-06-04-hermes-tavern-phase130-relationship-state-metadata/design.md

## 1. Interface Contract Check

- Relationship state persistence model exists as:
  `novel_relationship_states(id, project_id, label, state_text, created_at, updated_at)`.
- Required command literals are present and discoverable:
  - `/rp relationship add <project-id> <label> <state...>`
  - `/rp relationship list [project-id]`
  - `/rp relationship inspect <relationship-id>`
  - `/rp relationship update <relationship-id> <state...>`
  - `/rp relationship delete <relationship-id>`
- Foreign key/index constraints are present:
  - `project_id REFERENCES novel_projects(id) ON DELETE CASCADE`
  - `idx_novel_relationship_states_project ON novel_relationship_states(project_id)`
- Export contract is local metadata only:
  - Optional `## Relationships` section.
  - Only emitted when one-or-more rows exist.
  - Ordered after `## Style Guide` and before `## Chapters`.
- Scope contract is local metadata:
  - No prompt module injection.
  - Not included in debug prompt/context.
  - Excluded from context-budget payloads, vectorization/retrieval, provider/model
    behavior, generation, credentials, content mode, automation, and safety bypass
    paths.

## 2. S1 Evidence (Implementation)

- S1 commit identifier: `9665448`.
- Implemented in intended slice:
  - `src/hermes_tavern/db_novel.py` — relationship-state schema helpers + export block.
  - `src/hermes_tavern/runtime_novel.py` — `/rp relationship add/list/inspect/update/delete`.
  - `src/hermes_tavern/runtime.py` / `src/hermes_tavern/commands.py` — pass-through
    and help literal registration.
  - `README.md` — core command list reflects `/rp relationship ...`.
  - Focused tests in:
    - `tests/test_hermes_tavern_novel_db.py`
    - `tests/test_hermes_tavern_novel_runtime.py`
    - `tests/test_hermes_tavern_commands.py`
    - `tests/test_hermes_tavern_readme_docs.py`
- Controller reran S1 verification during S2: py_compile, focused tests,
  Tavern glob tests, full pytest, protected-file and whitespace checks passed.

## 3. S2 Evidence (Acceptance / Writeback)

- Codex architect produced a READY S2 planning artifact at
  `/tmp/hermes-tavern-architect-phase130-s2.jsonl`.
- Codex executor drafted acceptance/writeback docs at
  `/tmp/hermes-tavern-executor-phase130-s2.jsonl` without source/test/README changes.
- Controller finalized statuses after verification in:
  - `design/codestable/features/2026-06-04-hermes-tavern-phase130-relationship-state-metadata/design.md`
  - `design/codestable/features/2026-06-04-hermes-tavern-phase130-relationship-state-metadata/checklist.yaml`
  - `design/codestable/features/2026-06-04-hermes-tavern-phase130-relationship-state-metadata/hermes-tavern-phase130-relationship-state-metadata-acceptance.md`
  - `design/codestable/architecture/ARCHITECTURE.md`
  - `design/HERMES_TAVERN_DESIGN.md`

## 4. Acceptance Scenario Check (C1-C5)

- [x] C1: `novel_relationship_states` migration and project index are defined with cascade delete; CRUD/list helpers enforce bounded owner/ID behavior.
- [x] C2: Required `/rp relationship ...` literals are present for add/list/inspect/update/delete usage and IDs.
- [x] C3: Markdown export surfaces only when data exists, and placement is after Style Guide and before Chapters.
- [x] C4: Focused no-leak checks cover `/rp debug prompt` and `/rp debug context` exclusion from relationship text.
- [x] C5: Reverse-scope checks are constrained to feature slice; protected core/prompt/provider/model/generation/credentials/cloud-collab/minors-safety paths remain unchanged.

## 5. Boundary / Reverse Scope

Relationship state is intentionally project-local, command-editable metadata. It is
visible in command output and optional Markdown export only.

Prohibited side effects remain absent:

- automatic relationship extraction;
- prompt-module injection;
- debug/context-budget enrichment;
- vectorization/retrieval changes;
- provider/model/content-mode changes;
- credential persistence;
- retrieval automation;
- provider-safety bypass logic;
- cloud/collaboration and minors/underage handling routes.

## 6. Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/runtime.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` — 205 passed in 5.70s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` — 896 passed in 41.70s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` — 896 passed in 42.08s.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase130-relationship-state-metadata/design.md --require doc_type --require status --require feature` — passed.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase130-relationship-state-metadata/hermes-tavern-phase130-relationship-state-metadata-acceptance.md --require doc_type --require status --require feature` — passed.
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-04-hermes-tavern-phase130-relationship-state-metadata/checklist.yaml` — passed.
- `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py build/lib` — empty.
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py` — empty.
- `git diff --check` — passed.

## 7. Requirement / Roadmap / Attention

- Requirement / Roadmap writeback: skipped. This phase is a direct continuation of project metadata consolidation and has no dedicated requirement or roadmap frontmatter.
- Attention update: none. The existing attention constraints already cover plugin boundaries, protected core files, credentials, and adult-fiction safety boundaries.

## 8. Residual Risks

- Relationship command behavior should be rechecked if parser/routing changes in other novel command families are refactored.
- Export-order assumptions should be rechecked if future Markdown sections are inserted between Style Guide and Chapters.
- Relationship graphing, label rename, automatic extraction, prompt injection, vectorization/retrieval, cloud/collab, minors/underage paths, and provider-safety bypass remain explicit non-goals.
