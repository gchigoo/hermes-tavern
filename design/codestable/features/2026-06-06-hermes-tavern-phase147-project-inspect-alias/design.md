---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase147-project-inspect-alias"
status: draft
date: "2026-06-06"
summary: >
  Phase 147 plans a read-only /rp project inspect <project-id> alias for existing
  novel project metadata, preserving /rp project info behavior, schema, export,
  prompt/provider/generation, retrieval/vectorization, credentials, protected
  core files, minors/underage boundaries, and safety behavior.
tags: [hermes-tavern, project, command-surface, read-only, offline]
created: "2026-06-06"
updated: "2026-06-06"
owner: codestable-cron
---

# Project Inspect Alias

## Background

CodeStable feature checklists are current through accepted Phase 146, and no
Phase 147 artifact was found. A pending-checklist scan found no planned, draft,
in-progress, pending, or todo feature checklist status.

Recent phases added read-only inspect surfaces for canon, timeline, chapter, and
scene rows. Project metadata already has `/rp project info <id>` backed by
`TavernStore.get_project(project_id)`, but the project family has no matching
`inspect` spelling. This leaves project commands less consistent than adjacent
novel entities while requiring no new persistence or provider behavior.

This cron tick produces planning artifacts only. No source, README, tests,
or implementation files should be written until a later implementation turn.

## Scope

Add one local, offline, read-only command alias:

- `/rp project inspect <project-id>` routes under the existing project command
  family in `src/hermes_tavern/runtime_novel.py`.
- The alias reuses existing project inspection data: project id, title, summary,
  status, chapter count, and current brief/outline preview behavior already shown
  by `/rp project info <id>`.
- `/rp project info <id>` remains supported and behavior-compatible.
- Generated `/rp help` and README Core commands include the new project inspect
  literal.
- Focused tests cover success, malformed args, missing rows, help visibility, and
  unchanged `/rp project info <id>` behavior.

## Non-goals / Boundaries

This phase does not add project update/delete/archive ZIP/import/export changes,
cloud/collaboration, relationship graphs, automatic extraction, vectorization,
prompt/debug/context-budget injection, provider/model routing, generation, image
generation, TTS, credential persistence, content-mode changes, minors/underage
handling, or provider safety-bypass behavior.

Do not edit `run_agent.py`, `cli.py`, `gateway/run.py`, `src/hermes_tavern/runtime.py`,
`src/hermes_tavern/db.py`, `src/hermes_tavern/db_novel.py`, prompt/provider/generation
files, importer files, `plugins/**`, or `build/lib/**`.

No new filesystem paths are needed. If later paths are introduced in a separate
phase, they must use `get_hermes_home()` and must never hard-code `~/.hermes`.
No DB-persisted `api_key` or `access_token` behavior may change.

## Proposed Design

The noun layer already exists:

`novel_projects(id, title, summary, status, created_at, updated_at)`

`TavernStore.get_project(project_id)` already returns one project row with chapter
count or `None`. Existing project info also reads project brief and outline through
current helpers. This phase adds no table, index, migration, getter, mutation, or
export semantics.

The orchestration layer follows the accepted inspect-surface pattern:

`/rp project inspect <project-id>` -> `TAVERN_COMMAND_TABLE["project"]` ->
`TavernRuntime._project_command` -> `runtime_novel.project_command` ->
project inspect branch -> existing project-info rendering path.

Argument handling should be explicit:

- Missing id, malformed id, non-positive id, and extra arguments return project
  usage text that includes `/rp project inspect <project-id>`.
- A missing project row returns `No novel project found: <id>`.
- `/rp project info <id>` remains valid and returns the same output it returns
  before this phase.

No micro-refactor is needed. `runtime_novel.py` already owns the project command
family, and `commands.py` already owns generated help. This is a small family-local
extension and must not touch `src/hermes_tavern/runtime.py`.

## S1 Allowed Files

- `src/hermes_tavern/runtime_novel.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- `tests/test_hermes_tavern_novel_runtime.py`
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
- `design/HERMES_TAVERN_DESIGN.md`
- `design/codestable/architecture/ARCHITECTURE.md`

## S1 Implementation Plan

1. Add `/rp project inspect <project-id>` handling under the existing project command
   family.
2. Preserve `/rp project info <id>` output and compatibility.
3. Update generated help and README Core command surface.
4. Add focused offline tests for success, bad args, missing project, help, README,
   and unchanged project info.

## S2 Acceptance / Writeback

S2 is controller-owned after S1 verification. It may update only the Phase 147
CodeStable artifacts plus architecture/root design docs to describe the current
read-only project inspect alias. S2 must not edit source, tests, README, plugin
shims, build artifacts, or protected core files.

Architecture/root design writeback should add only:

- `/rp project inspect <project-id>` in current command-surface lists.
- A note that project inspection reads existing project metadata through the current
  project info/getter path.
- Preserved boundaries: no schema, project mutation, export behavior, prompt/provider/
  generation/retrieval/vectorization/credential/content-mode, minors/underage, or
  safety-bypass behavior changes.

## Acceptance Criteria

1. `/rp project inspect <project-id>` returns project metadata for one existing project.
2. `/rp project info <id>` remains supported and behavior-compatible.
3. Malformed ids, missing ids, non-positive ids, and extra args return bounded project
   usage output.
4. Missing project rows return `No novel project found: <id>` without exceptions.
5. Generated help and README Core commands include `/rp project inspect <project-id>`.
6. No DB/schema, protected core/runtime.py, prompt/provider/generation, retrieval/
   vectorization, archive/import/export ZIP, credential, content-mode, plugin, build,
   minors/underage, or safety behavior changes occur.

## Verification Plan

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/design.md --require doc_type --require status --require feature`
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase147-project-inspect-alias/checklist.yaml`
- `git diff --name-only -- run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime.py src/hermes_tavern/db.py src/hermes_tavern/db_novel.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/importers plugins build/lib`
- `git diff --check`

## Risks / Rollback

Risk: users may infer this adds project editing. Mitigation: keep command text,
README text, and tests strictly read-only.

Risk: alias behavior may drift from `/rp project info`. Mitigation: route through
the same rendering path or assert equal output for the same project id.

Rollback is simple: remove the inspect branch, generated help literal, README
literal, and focused tests. No schema or data rollback is needed.

## Current / Deferred Boundary

Current for this phase: command-visible project inspection alias only.

Deferred: project editing/deletion, archive ZIP/import/export expansion, cloud or
collaboration workflows, relationship graphs, automatic extraction, vectorization,
prompt injection, provider calls, image/TTS calls, credential persistence, minors/
underage handling, and provider safety-bypass features.
