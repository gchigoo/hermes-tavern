---
doc_type: feature-acceptance
feature: "2026-06-05-hermes-tavern-phase134-plot-thread-metadata"
status: accepted
date: "2026-06-05"
summary: >
  Plot Thread Metadata v1 is accepted as project-scoped local metadata with
  `/rp plot thread` CRUD, help/README visibility from S1, optional
  `## Plot Threads` Markdown export placement, and architecture/root-design
  writeback. It remains offline/export-only and excluded from prompt,
  debug-context, provider, routing, generation, credential, retrieval,
  vectorization, automation, media, and safety-bypass paths.
tags: [novel, plot-thread, metadata, export, offline, acceptance]
---

# Phase 134 Plot Thread Metadata Acceptance

> Phase: S2 verify/accept/write architecture
> Controller verification date: 2026-06-05
> Design: `design/codestable/features/2026-06-05-hermes-tavern-phase134-plot-thread-metadata/design.md`
> Checklist: `design/codestable/features/2026-06-05-hermes-tavern-phase134-plot-thread-metadata/checklist.yaml`

## 1. Interface and schema contract

Accepted implementation surface:

- Schema: `novel_plot_threads(id, project_id, label, description_text, created_at, updated_at)`.
- Index: `idx_novel_plot_threads_project` on `novel_plot_threads(project_id)`.
- Helpers:
  - `create_plot_thread(project_id, label, description_text)`
  - `list_plot_threads(project_id)`
  - `get_plot_thread(plot_thread_id)`
  - `update_plot_thread(plot_thread_id, description_text)`
  - `delete_plot_thread(plot_thread_id)`
- Commands:
  - `/rp plot thread add <project-id> <label> <description...>`
  - `/rp plot thread list [project-id]`
  - `/rp plot thread inspect <plot-thread-id>`
  - `/rp plot thread update <plot-thread-id> <description...>`
  - `/rp plot thread delete <plot-thread-id>`

Controller reran the focused DB/runtime/help/README contract tests and accepted
S1's implementation evidence.

## 2. Behavior and scope contract

The accepted behavior remains the Phase 134 design scope:

- add/list/inspect/update/delete manage user-authored plot-thread rows under a novel project;
- add requires an explicit project ID;
- list accepts an explicit project ID or active-project fallback;
- inspect/update/delete operate by plot-thread ID;
- blank labels and blank descriptions are rejected;
- missing projects and missing plot-thread IDs return bounded messages;
- labels are metadata labels, not graph edges, gateway thread identities, task state, chapter bindings, default asset bindings, ages, or policy fields.

No source/test changes were needed in S2.

## 3. Markdown export contract

`## Plot Threads` is accepted as an optional project Markdown export section.
When plot-thread rows exist, it appears after `## Organizations` when present
(or after the prior project metadata placement otherwise) and before
`## Characters`, `## Relationships`, and `## Chapters`. It is omitted when empty.

## 4. No-leak / reverse-scope contract

Plot-thread metadata is accepted as local/offline metadata only. It remains
excluded from:

- prompt assembly and prompt module selection;
- `/rp debug prompt`, `/rp debug context`, and context-budget reporting;
- provider/model routing, content-mode behavior, credentials, and generation;
- retrieval, vectorization, summarization, automation, memory workflows;
- media/TTS/image behavior;
- ST asset importers/exporters, archive import/export, default bindings;
- relationship graph/rename/automatic extraction;
- minors/underage handling and provider-safety-bypass pathways.

Controller reverse-scope checks found no S2 diff under README, source, tests,
core entrypoints, gateway files, or build artifacts.

## 5. Architecture/root-design writeback

Updated:

- `design/codestable/architecture/ARCHITECTURE.md`
  - Phase 134 capability summary;
  - command-surface and DB-schema headings current through Phase 134;
  - `/rp plot thread ...` command literals;
  - `novel_plot_threads` schema/index entry;
  - Phase 134 metadata-only/export-only boundary notes;
  - prompt/debug/context-budget and provider/routing exclusion wording.
- `design/HERMES_TAVERN_DESIGN.md`
  - plot threads moved from deferred sub-object wording into current local metadata scope;
  - `/rp plot thread ...` command literals added to writing commands;
  - current Phase 121-134 Markdown export wording documents `## Plot Threads` placement;
  - deferred boundaries retained for relationship graph/rename/extraction, style samples,
    default bindings, canon/content-mode metadata, archive import/export,
    retrieval/vectorization, automation, provider/model routing, generation,
    cloud/collab, credentials, minors/underage, and safety bypass.

## 6. Requirement and roadmap writeback

No requirement or roadmap writeback was needed. The Phase 134 design has no
`requirement`, `roadmap`, or `roadmap_item` frontmatter target and is a bounded
local metadata continuation.

## 7. Controller verification

Controller-run verification after S2 writeback:

- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` → `256 passed in 8.87s`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` → `947 passed in 43.96s`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` → `947 passed in 40.70s`.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase134-plot-thread-metadata/design.md --require doc_type --require status --require feature` → passed.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase134-plot-thread-metadata/hermes-tavern-phase134-plot-thread-metadata-acceptance.md --require doc_type --require status --require feature` → passed.
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-05-hermes-tavern-phase134-plot-thread-metadata/checklist.yaml` → passed.
- `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py build/lib` → empty.
- stale-wording search over `design/codestable/architecture/ARCHITECTURE.md` and `design/HERMES_TAVERN_DESIGN.md` for Phase 133/plot-thread-deferred phrases → empty.
- `git diff --check` → passed.

Codex executor's sandboxed Tavern/full-suite attempts initially reported
transient/unrelated failures; controller reran the same gates successfully in the
controller environment before accepting this phase.

## 8. Attention candidates

No new project-wide `attention.md` rule was discovered in S2. Existing constraints
already cover protected core files, local/offline metadata scope, and validation
commands.

## 9. Residual deferred work

Still deferred after Phase 134:

- relationship graph/rename/automatic extraction;
- style samples;
- default card/preset/lorebook binding metadata;
- canon-policy/content-mode metadata behavior changes;
- project archive ZIP/import/export workflows beyond local Markdown export;
- retrieval/vectorization/automation integrations;
- provider routing/generation coupling;
- cloud/collaboration/account features;
- minors/underage fields or safety-classification surfaces;
- provider-safety bypass behavior.
