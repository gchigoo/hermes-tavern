---
doc_type: feature-acceptance
feature: "2026-06-06-hermes-tavern-phase140-relationship-label-rename"
status: accepted
date: "2026-06-06"
summary: >
  Phase 140 is accepted as metadata-only Relationship Label Rename through
  `/rp relationship rename <relationship-id> <label>`. It updates only
  `novel_relationship_states.label` and `updated_at`, keeps relationship metadata
  visible through existing command/export surfaces, and does not alter prompt,
  provider, retrieval/vectorization, generation, or archive/import behavior.
  Controller verification passed focused, Tavern-wide, and full offline pytest,
  CodeStable validators, stale-wording guards, reverse-scope guards, and whitespace checks.
tags: [novel, relationships, metadata, commands, export, offline]
---

# Phase 140 Relationship Label Rename Acceptance

> Phase: S2 verify/accept/write current docs
> Design: `design/codestable/features/2026-06-06-hermes-tavern-phase140-relationship-label-rename/design.md`
> Checklist: `design/codestable/features/2026-06-06-hermes-tavern-phase140-relationship-label-rename/checklist.yaml`

## 1. Interface contract

Accepted interface contract remains:

- DB helper: `rename_relationship_state(relationship_id, label)` in
  `src/hermes_tavern/db_novel.py`.
- Runtime route: `/rp relationship rename <relationship-id> <label>` inside
  `runtime_novel.relationship_command` (nested relationship family).
- Command surface and docs:
  - `/rp help` and `TAVERN_COMMAND_TABLE["relationship"]` include nested
    `rename`.
  - README Core commands and doc tests include the nested literal.
- Schema remains unchanged: no table/index migration, no schema drift, only
  helper-level metadata writes.

## 2. Behavior and decisions

- Metadata-only rename: only `novel_relationship_states.label` and `updated_at` are
  updated.
- State body isolation: `state_text` is not changed by rename.
- Bounded validation:
  - blank labels are rejected with `ValueError("Relationship label cannot be blank")`,
  - missing rows are rejected with `ValueError("Relationship state not found")`,
  - malformed relationship IDs return bounded runtime usage behavior.
- Router decision preserved: rename is nested under `/rp relationship`; there is no
  top-level `/rp relationship-rename` or `/rp rel`.
- No side-effect scope expansion: no graph/alias/merge-split/automatic extraction,
  prompt/debug/context-provider paths, context-budget reporting, content-mode,
  provider/router/model, generation, retrieval/vectorization, media, archive,
  safety-bypass, or importer/exporter behavior changes in this phase.

## 3. Acceptance scenarios

- AC1: `rename_relationship_state(...)` exists and updates only `label` and
  `updated_at` for an existing row (S1 DB test + static helper presence).
- AC2: helper preserves id/project_id/state_text/created_at and deterministic row
  ordering (S1 DB test assertions).
- AC3: blank label / malformed id / missing row are bounded in DB+runtime paths
  (S1 DB/runtime tests).
- AC4: `/rp relationship rename <relationship-id> <label>` is wired via existing
  relationship command routing (S1 runtime command tests).
- AC5: `/rp relationship update` remains state-text-only and does not alter label
  (S1 DB/runtime separation tests).
- AC6: `/rp relationship list`, `/rp relationship inspect`, and `/rp project export`
  show renamed label through existing read/export surfaces (S1 runtime/export tests).
- AC7: help/readme/docs command surfaces include the nested literal; no top-level
  route (S1 command/docs tests).
- AC8: `TAVERN_COMMAND_TABLE` remains nested; no top-level runtime.py shim or
  prohibited command-route changes (S1 command tests + source scope expectation).
- AC9: renamed text is not visible in `/rp debug prompt` or `/rp debug context`
  and remains absent from prompt/provider/context-bounded outputs (S1 no-leak test
  and reverse-scope constraints).
- AC10: controller verification passed focused py_compile, focused pytest
  (`323 passed`), Tavern-wide pytest (`1014 passed`), and full pytest
  (`1014 passed`) without network/provider calls.
- AC11: S1 left acceptance report, architecture, root design, and accepted final
  status untouched; S2 updated only allowed docs/status artifacts after controller
  verification.

Controller-run verification evidence on 2026-06-06:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile ...` passed for touched source/test files.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider` → `323 passed`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` → `1014 passed`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` → `1014 passed`.
- CodeStable validators passed for `design.md`, `checklist.yaml`, and this acceptance report.
- Reverse-scope guard for `README.md`, `src`, `tests`, core/gateway, plugin, and build paths was empty; no runtime/code/test files changed during S2.
- Stale wording guards for `relationship graph/rename` were empty, required `/rp relationship rename <relationship-id> <label>` docs were present, protected prompt/provider/importer/media route scans were empty, and `git diff --check` passed.

## 4. Terminology consistency

- "Relationship label" means user-facing display metadata in
  `novel_relationship_states.label`.
- It is mutable for local correction and does not represent graph identity,
  alias mapping, merge/split semantics, graph extraction, ST import/export identity,
  or generation intent.

## 5. Architecture merge

- `design/codestable/architecture/ARCHITECTURE.md` updated in relevant sections:
  - capability summary includes Phase 140,
  - `/rp relationship rename` command line added in current surface list,
  - "current through Phase 140" markers updated,
  - relationship-boundary bullet added under Known Constraints.
- `design/HERMES_TAVERN_DESIGN.md` updated in relevant sections:
  - relationship label correction command added under current project/novel behavior,
  - command lists in both `### 6.7 Project / Novel` and `### 13.2 Writing commands`
    include `/rp relationship rename ...`,
  - stale broad wording replaced with deferred "graph/aliases/merge-split/automatic extraction"
    plus explicit current-label behavior,
  - tables section notes that Phase 140 updates only label/updated_at,
  - importer/exporter phase range advanced to 121–140 with relationship label
    export note.

## 6. Requirement writeback

No new requirement artifact was required for this bounded S2 docs/status slice.
No requirement frontmatter in this acceptance draft.

## 7. Roadmap writeback

No roadmap artifact was required for this bounded docs/status slice.
No roadmap/frontmatter in this acceptance draft.

## 8. attention.md candidates

No recurring workflow/operational rule was identified for new `attention.md`
entries during this phase.

## 9. Residuals

- Graph, aliases, merge/split, and automatic extraction semantics remain deferred.
- Relationship label rename intentionally updates metadata only and does not affect
  prompt modules, context budget, provider routing, generation, content mode,
  retrieval/vectorization, archive ZIP, or safety/bypass flows.
- No schema/import/export format changes were introduced in Phase 140.
