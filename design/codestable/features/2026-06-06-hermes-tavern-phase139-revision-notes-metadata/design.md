---
doc_type: feature-design
feature: "2026-06-06-hermes-tavern-phase139-revision-notes-metadata"
status: approved
date: "2026-06-06"
summary: >
  Revision Notes Metadata v1 adds local project-scoped revision-note rows
  managed through /rp project revision add/list/inspect/update/delete and
  optional project Markdown export visibility. Notes remain metadata-only/inert
  and do not affect prompts, active sessions, provider/model routing, content
  mode, credentials, retrieval/vectorization, generation, media, archive, graph,
  automatic extraction, or safety behavior.
tags: [novel, revision-notes, metadata, export, offline]
---

# Phase 139: Revision Notes Metadata v1

## 0. Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Revision Note Metadata | A user-authored local project note describing a planned or completed writing revision. | Not `/rp note` author-note prompt injection, not generated rewrite output, and not an edit operation. |
| Revision Label | A compact one-token user label such as `continuity-pass`, `chapter-2-fix`, or `tone-pass`. | Not a route key, project status, version field, or workflow state machine. |
| Revision Note Text | Freeform user-authored prose for the revision note. | Not prompt context, memory, retrieval content, provider instruction, or generated summary. |

Startup inspection found Phase 138 accepted and revision notes still deferred in the root novel-engine design. Controller validation corrected the command routing surface: this feature must use the existing `/rp project ...` route, not a new top-level `/rp revision ...` command family.

## 1. Decisions And Constraints

### Need

Hermes Tavern now has project, brief, outline, style, relationship, character, location, organization, plot-thread, style-sample, default-binding, and scene-beat metadata. Revision notes are the next small local metadata slice: they let users track intended edits or revision passes for a project without adding rewrite generation, archive/versioning, graph workflows, or prompt behavior.

### Success

- A user can add a revision note to an existing project with `/rp project revision add <project-id> <label> <note...>`.
- A user can list revision notes for an explicit project with `/rp project revision list <project-id>`.
- A user can inspect, update note text, and delete a revision note by note ID.
- Project Markdown export includes a `## Revision Notes` section only when rows exist.
- `/rp help` and README Core commands expose the nested project revision command literals.
- Focused no-leak tests prove distinctive revision note text does not appear in `/rp debug prompt` or `/rp debug context`.
- Implementation stays local/offline and does not change prompt, session, provider, content-mode, credential, retrieval, vectorization, media, archive, or generation behavior.

### Explicit Non-Goals

- No top-level `/rp revision ...` or `/rp revision note ...` command family.
- No edits to `src/hermes_tavern/runtime.py`; routing must stay under existing `/rp project ...`.
- No rewrite generation, diffing, version history, branch/merge, archive import/export, Markdown import, automatic extraction, assistant-turn update cycle, or project status workflow.
- No prompt module injection and no changes to debug prompt/context, context-budget reporting, model routing, provider adapters, content mode, credentials, generation, memory, retrieval/vectorization, media/TTS/image, or safety behavior.
- No ST card/preset/lorebook/persona importer/exporter changes.
- No protected core edits to `run_agent.py`, `cli.py`, or `gateway/run.py`.
- No age, date-of-birth, minor/underage, school-grade, sexual-safety classification fields, examples, tests, or commands.

### Complexity

Small local plugin slice. It extends the existing project metadata pattern in `db_novel.py`, `runtime_novel.py`, `commands.py`, README, and focused tests. It avoids a new top-level command family by nesting under `runtime_novel.project_command`.

## 2. Names And Flow

### 2.1 Noun Layer

Current:

- `src/hermes_tavern/db_novel.py` owns novel project metadata persistence and Markdown export.
- `src/hermes_tavern/runtime_novel.py` owns `/rp project ...` behavior.
- `src/hermes_tavern/commands.py` owns `/rp help` literals for the existing project command entry.
- `src/hermes_tavern/runtime.py` already routes `_project_command` to `runtime_novel.project_command` and must not be edited.
- No current revision-note table, helpers, commands, docs, or tests exist.

Change:

Add local project-scoped metadata:

    novel_revision_notes(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      project_id INTEGER NOT NULL REFERENCES novel_projects(id) ON DELETE CASCADE,
      label TEXT NOT NULL,
      note_text TEXT NOT NULL,
      created_at TEXT NOT NULL DEFAULT (datetime('now')),
      updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    )

    CREATE INDEX idx_novel_revision_notes_project
      ON novel_revision_notes(project_id, id)

Expected store helpers:

- `create_revision_note(project_id, label, note_text)`
- `list_revision_notes(project_id)`
- `get_revision_note(note_id)`
- `update_revision_note(note_id, note_text)`
- `delete_revision_note(note_id)`

Rules:

- `project_id` must reference an existing local project.
- Blank label and blank note text are rejected.
- Labels are immutable in v1; update changes `note_text` only.
- List/export order is deterministic by `id ASC`.
- Missing project returns bounded `No novel project found: <id>` command behavior.
- Missing note returns bounded `No revision note found: <id>` command behavior.

### 2.2 Orchestration Layer

Flow:

    /rp project revision add <project-id> <label> <note...>
      -> existing project_command route
      -> validate project
      -> insert local revision-note row
      -> return compact confirmation

    /rp project revision list <project-id>
      -> existing project_command route
      -> validate project
      -> list rows ordered by id
      -> return compact mobile output

    /rp project revision inspect <note-id>
      -> existing project_command route
      -> fetch row
      -> return compact detail

    /rp project revision update <note-id> <note...>
      -> existing project_command route
      -> update note_text only
      -> return compact confirmation

    /rp project revision delete <note-id>
      -> existing project_command route
      -> delete row
      -> return compact confirmation or not-found

    /rp project export [id]
      -> export_project_markdown(project_id)
      -> emit optional ## Revision Notes before ## Chapters when rows exist

Flow constraints:

- Revision commands do not start, pause, resume, switch, archive, or mutate active sessions.
- Revision note text is not selected by `_session_prompt_modules`, prompt compiler, debug prompt/context, context-budget reporting, model routing, memory, retrieval/vectorization, provider adapters, image/TTS/media flows, or generation.
- Export reads revision rows only during local Markdown export.

### 2.3 Mount Points

Allowed S1 files:

| File | Purpose |
|---|---|
| `src/hermes_tavern/db_novel.py` | Add `novel_revision_notes`, CRUD/list helpers, and optional project Markdown export block. |
| `src/hermes_tavern/runtime_novel.py` | Add nested `/rp project revision ...` parsing and bounded command messages. |
| `src/hermes_tavern/commands.py` | Add `/rp project revision ...` help literals to the existing project command entry only. |
| `README.md` | Add Core command literals for nested project revision commands. |
| `tests/test_hermes_tavern_novel_db.py` | Add migration, CRUD, validation, missing-owner, export inclusion/omission/order tests. |
| `tests/test_hermes_tavern_novel_runtime.py` | Add command, usage/not-found, help, and no-leak tests. |
| `tests/test_hermes_tavern_commands.py` | Add help visibility assertions. |
| `tests/test_hermes_tavern_readme_docs.py` | Add README literal assertions. |

Prohibited S1 files:

- `src/hermes_tavern/runtime.py`
- `run_agent.py`
- `cli.py`
- `gateway/run.py`
- `src/hermes_tavern/runtime_prompt_modules.py`
- `src/hermes_tavern/prompt.py`
- `src/hermes_tavern/runtime_prompt_manager.py`
- `src/hermes_tavern/runtime_debug.py`
- `src/hermes_tavern/model_router.py`
- `src/hermes_tavern/provider_bridge.py`
- `src/hermes_tavern/adapters.py`
- `src/hermes_tavern/runtime_model.py`
- `src/hermes_tavern/runtime_generation.py`
- `src/hermes_tavern/runtime_content.py`
- `src/hermes_tavern/memory.py`
- `src/hermes_tavern/runtime_memory.py`
- `src/hermes_tavern/images.py`
- `src/hermes_tavern/runtime_images.py`
- `src/hermes_tavern/importers/**`
- `plugins/**`
- `build/lib/**`
- `design/codestable/architecture/ARCHITECTURE.md`
- `design/HERMES_TAVERN_DESIGN.md`
- Any CodeStable checklist, acceptance, or status file during S1

### 2.4 Slicing

S1 only: implement local project revision-note metadata persistence, nested project commands, help/README literals, optional Markdown export visibility, and focused tests. Do not mark checklist or acceptance done.

Architecture/root-design writeback and acceptance closure are controller-owned later work.

### 2.5 Structure Health

No pre-feature micro-refactor.

`db_novel.py` and `runtime_novel.py` are broad, but they already own novel persistence/export and project command families. This phase adds one narrow project-scoped metadata table and one nested project subcommand. A new top-level command family would require a prohibited `runtime.py` shim, and a broad metadata abstraction would add risk beyond the requested slice.

## 3. Acceptance Criteria

1. Migration creates `novel_revision_notes` with `project_id`, `label`, `note_text`, timestamps, and `idx_novel_revision_notes_project`.
2. Store helpers create, list, inspect, update, and delete revision-note rows with deterministic `id ASC` ordering.
3. Store helpers reject missing projects, blank labels, and blank note text with bounded behavior.
4. `/rp project revision add/list/inspect/update/delete` commands work through existing project command routing and return compact local metadata messages.
5. `TAVERN_COMMAND_TABLE` is not given a new top-level `revision` entry; only the existing `project` help lines are extended.
6. `src/hermes_tavern/runtime.py` remains unchanged.
7. README Core commands and command/docs tests include the nested project revision literals.
8. `/rp project export [id]` emits optional `## Revision Notes` only when rows exist and omits the section when none exist.
9. Revision note marker text does not appear in `/rp debug prompt`, `/rp debug context`, prompt modules, context-budget output, provider routing, content mode, retrieval/vectorization, or generation paths.
10. Focused and plugin-wide offline tests pass without network/provider calls.
11. Reverse-scope checks show no protected core, `runtime.py`, prompt/debug/context-budget, provider/model/content/generation/credential, retrieval/vectorization, memory, media/TTS/image, importer, plugin shim, build artifact, architecture/root-design, archive, graph, automatic extraction, or safety-bypass changes.

## 4. Verification Commands

S1 executor verification:

    PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    git diff --name-only -- src/hermes_tavern/runtime.py run_agent.py cli.py gateway/run.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/prompt.py src/hermes_tavern/runtime_prompt_manager.py src/hermes_tavern/runtime_debug.py src/hermes_tavern/model_router.py src/hermes_tavern/provider_bridge.py src/hermes_tavern/adapters.py src/hermes_tavern/runtime_model.py src/hermes_tavern/runtime_generation.py src/hermes_tavern/runtime_content.py src/hermes_tavern/memory.py src/hermes_tavern/runtime_memory.py src/hermes_tavern/images.py src/hermes_tavern/runtime_images.py src/hermes_tavern/importers plugins build/lib design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md
    git diff --check

Controller artifact validation after writing this artifact:

    python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-06-hermes-tavern-phase139-revision-notes-metadata/design.md --require doc_type --require status --require feature
    python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-06-hermes-tavern-phase139-revision-notes-metadata/checklist.yaml

## 5. Risks

- Revision-note terminology can imply generated rewrites or version control. Mitigation: command output, docs, tests, and no-leak checks keep notes metadata-only/inert.
- Routing can accidentally drift back to a top-level `/rp revision` family. Mitigation: tests must assert no `revision` key in `TAVERN_COMMAND_TABLE` and assert project help contains the nested literals.
- Project export order can become unstable. Mitigation: export tests cover optional inclusion, omission, and ordering before `## Chapters`.

## 6. Rollback

Remove the `novel_revision_notes` migration/index, store helpers, `/rp project revision ...` command handling/help literals, README command lines, Markdown export block, and focused tests. With no prompt/session/provider/runtime-core changes, removing those surfaces returns behavior to Phase 138.

## 7. Non-Goals

- No top-level `/rp revision ...` family.
- No `src/hermes_tavern/runtime.py` edit.
- No prompt compilation, active session behavior, provider/model routing, content mode, credential handling, retrieval/vectorization, generation, media/TTS/image, archive import/export, ST importer/exporter, cloud/collab, graph, automatic extraction, relationship graph/rename, revision generation/diffing/versioning, or safety-bypass behavior.
