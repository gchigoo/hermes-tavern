---
doc_type: feature-acceptance
feature: "2026-06-06-hermes-tavern-phase139-revision-notes-metadata"
status: accepted
date: "2026-06-06"
summary: >
  Phase 139 is accepted as Revision Notes Metadata v1. It adds local
  project-scoped revision-note metadata through nested /rp project revision
  commands and optional Markdown export visibility only; no prompt/provider/
  runtime behavior path is changed.
tags: [novel, revision-notes, metadata, export, offline]
---

# Phase 139 Revision Notes Metadata v1 Acceptance

> Phase: S2 verify/accept/write current docs
> Controller verification date: 2026-06-06
> Design: `design/codestable/features/2026-06-06-hermes-tavern-phase139-revision-notes-metadata/design.md`
> Checklist: `design/codestable/features/2026-06-06-hermes-tavern-phase139-revision-notes-metadata/checklist.yaml`

## 1. Scope and contract status

Phase 139 is accepted as implemented and writeback-updated through the allowed S2
documents. The feature is:

- local project metadata only (`novel_revision_notes`),
- managed only under `/rp project revision ...`,
- visible in project Markdown export as optional `## Revision Notes`,
- explicit in all surfaces as metadata-only/inert,
- excluded from prompt/debug/context-budget/provider/model/retrieval/session-generation behavior.

## 2. Interface / schema contract

Accepted schema contract:

- `novel_revision_notes(id, project_id, label, note_text, created_at, updated_at)` table exists.
- `project_id` is required and references `novel_projects(id)` with `ON DELETE CASCADE`.
- Index `idx_novel_revision_notes_project ON novel_revision_notes(project_id, id)` exists.
- Helpers:
  - `create_revision_note(project_id, label, note_text)`
  - `list_revision_notes(project_id)` returns rows `ORDER BY id ASC`
  - `get_revision_note(note_id)`
  - `update_revision_note(note_id, note_text)`
  - `delete_revision_note(note_id)`
- Validation is bounded:
  - blank/whitespace `project_id`/`label`/`note_text` are rejected,
  - missing project and missing note return bounded errors/messages,
  - project ownership is enforced by FK (via explicit check + helper validation).

Evidence references:

- `tests/test_hermes_tavern_novel_db.py` migration/index tests for
  `novel_revision_notes` and `idx_novel_revision_notes_project`.
- CRUD + validation tests for revision notes in the same file.

## 3. Command and export behavior

Supported command contract:

- `/rp project revision add <project-id> <label> <note...>`
- `/rp project revision list [project-id]`
- `/rp project revision inspect <note-id>`
- `/rp project revision update <note-id> <note...>`
- `/rp project revision delete <note-id>`

Behavioral constraints:

- Add/list/update/delete are routed through existing `runtime_novel.project_command`
  under nested `revision` subcommand (no top-level `/rp revision` family).
- Add requires explicit `<project-id>` (no implicit active-project fallback).
- List uses explicit `<project-id>` when given, and still accepts bounded active-project fallback semantics per existing project route policy.
- All messages are compact, deterministic, and local/in-memory metadata only.

Export contract:

- `/rp project export [id]` appends optional `## Revision Notes` only when rows exist.
- Section is omitted when no rows exist.
- When present, revision notes are emitted before `## Chapters` and with deterministic order (`id ASC`).
- Exported entries use `- <label>: <note_text>` formatting.

Evidence references:

- `tests/test_hermes_tavern_novel_runtime.py` for command behavior and no-leak checks.
- `tests/test_hermes_tavern_novel_db.py` and `tests/test_hermes_tavern_novel_runtime.py` for export inclusion/omission and ordering.
- `tests/test_hermes_tavern_commands.py` and `tests/test_hermes_tavern_readme_docs.py` for route/help/docs coverage.

## 4. Metadata-only/no-leak boundaries

Phase 139 remains metadata-only and does not affect:

- prompt assembly, prompt modules, prompt compilation,
- `/rp debug prompt`, `/rp debug context`, context-budget, context modules,
- active session behavior, session selection, switching, generation, or model routing,
- provider behavior, credentials persistence, content mode, retrieval/vectorization,
- vector search pipelines, archive/project ZIP workflows, ST importer/exporter pipelines,
- safety bypass paths.

No-leak and boundary evidence:

- Focused no-leak runtime test checks for distinctive marker text in both prompt
  and context output.
- Design check constraints in current architecture/root-design and unchanged protected files.
- Reverse-scope guard evidence is below and in checklist `verification_notes`.

## 5. Architecture and root-design writeback

S2 architecture/root-design updates were written with:

- `design/codestable/architecture/ARCHITECTURE.md`
  - add phase item for Phase 139,
  - add `/rp project revision ...` command surface in current command list,
  - add `novel_revision_notes`/`idx_novel_revision_notes_project` schema line,
  - add `## Revision Notes` as optional project export section,
  - add revision metadata boundary in exclusion list,
  - update current-through marker to include Phase 139.
- `design/HERMES_TAVERN_DESIGN.md`
  - mark Revision Notes Metadata as current in Project/Novel scope,
  - include nested command literals in project command lists,
  - update project export section ordering/placement in command/docs expectations,
  - add schema entry for `novel_revision_notes` in §16,
  - keep revision notes out of deferred list and add explicit deferred boundaries for version/rewrite/archive/import/extraction/graph areas.

## 6. Controller-run evidence

Implementation evidence retained from S1:

- Controller planning refinement logs for routing and scope alignment.
- Executor smoke JSONL and execution artifact for implementation attempts.
- Controller-verified test run outputs:
  - focused DB/runtime/command/docs tests,
  - full Tavern-wide and full project test runs,
  - py_compile pass,
  - reverse-scope diff guard pass (no prohibited file changes),
  - git diff --check pass.
- checklist `verification_notes` mirrors those controller evidence artifacts.

Acceptance/writeback evidence from S2:

- Codex architect S2 JSONL: `/tmp/hermes-tavern-architect-phase139-s2.jsonl`
  (`RESULT: ACCEPTANCE_WRITEBACK_ARTIFACT`).
- Codex executor smoke JSONL:
  `/tmp/hermes-tavern-executor-smoke-phase139-s2.jsonl` returned
  `EXECUTOR_SMOKE_OK`.
- Codex executor S2 JSONL: `/tmp/hermes-tavern-executor-phase139-s2.jsonl`;
  executor edited only the four allowed docs/status files and recovered from
  intermediate patch/validator failures before the controller finalized wording.
- Controller reran `py_compile` for changed source/test evidence files: passed
  with no output.
- Controller reran CodeStable validators for design, checklist, and this
  acceptance report: all passed.
- Controller reran focused DB/runtime/command/README docs pytest: `318 passed in
  12.07s`.
- Controller reran Tavern-wide pytest: `1009 passed in 46.51s`.
- Controller reran full pytest: `1009 passed in 42.50s`.
- Controller reran stale-wording guards for old Phase 138 ranges and
  revision-notes-deferred wording: empty output.
- Controller reran top-level `/rp revision` route guard against README, `src`,
  tests, root design, and architecture: empty output; feature-artifact matches
  are negative no-top-level assertions only.
- Controller reran protected reverse-scope diff guard for README, `src`, tests,
  core/gateway/plugin/build paths: empty output.
- Controller reran `git diff --check`: passed with no output.

## 7. Reverse-scope and guard evidence

- `git diff --check` is clean of whitespace and merge markers.
- Protected reverse-scope diff guard is empty for README, source, tests,
  core/gateway/plugin/build paths prohibited during S2.
- Stale-wording guards are empty for old Phase 138 ranges and
  revision-notes-deferred language. Top-level `/rp revision` route guards are
  empty for runtime/help/root-design/architecture surfaces; feature-artifact
  mentions are negative no-top-level assertions only.

## 8. Residual deferred work

Intentionally deferred and still out of scope for Phase 139:

- rewrite/generation pipeline for notes,
- note diffing/history/versioning,
- automatic extraction/summarization triggers around revision notes,
- archive ZIP import/export for revision notes,
- graph/relationship rename workflows,
- ST importer/exporter behavior changes tied to revision notes.

These items remain deferred in architecture/root-design with explicit no-side-effect
contract.
