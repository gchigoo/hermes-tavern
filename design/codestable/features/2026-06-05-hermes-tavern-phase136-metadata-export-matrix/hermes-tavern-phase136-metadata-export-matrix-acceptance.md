---
doc_type: feature-acceptance
feature: "2026-06-05-hermes-tavern-phase136-metadata-export-matrix"
status: accepted
date: "2026-06-05"
summary: >
  Phase 136 is accepted as a test-only metadata export matrix hardening slice.
  It adds no source/product behavior, but locks current project metadata Markdown
  export ordering, optional-section omission, and `/rp project export [id]`
  local file export coverage through controller-verified tests and
  docs/status-only S2 closeout.
tags: [novel, metadata, export, regression, test-only, acceptance]
---

# Phase 136 Metadata Export Matrix Acceptance

> Phase: S2 verify/accept test-only phase
> Controller verification date: 2026-06-05
> Design: `design/codestable/features/2026-06-05-hermes-tavern-phase136-metadata-export-matrix/design.md`
> Checklist: `design/codestable/features/2026-06-05-hermes-tavern-phase136-metadata-export-matrix/checklist.yaml`

## 1. Scope and design contract

Phase 136 is accepted as test-only regression hardening around current project
metadata export ordering and runtime file export behavior. It introduces no new
commands, schema tables, migrations, CRUD helpers, prompt modules, provider
paths, generation behavior, retrieval/vectorization, credential handling,
importer/exporter formats, archive output, relationship graph/rename behavior,
automatic extraction, or Hermes core changes.

Accepted S1 implementation surface:

- `tests/test_hermes_tavern_novel_db.py`
- `tests/test_hermes_tavern_novel_runtime.py`

Accepted S2 status surface:

- this acceptance report
- `checklist.yaml` status/evidence updates

## 2. DB export co-presence matrix

Accepted evidence:

- `test_export_project_markdown_orders_all_current_metadata_sections`

The DB-level matrix creates a single project containing all current metadata
families and asserts the section order:

`Summary -> Project Brief -> Outline -> Style Guide -> Style Samples -> Locations -> Organizations -> Plot Threads -> Characters -> Relationships -> Chapters`

This directly covers the Phase 136 design requirement that recently-added local
metadata families coexist in one export-order regression instead of being proven
only by isolated per-family tests.

## 3. Representative metadata coverage

The same DB matrix asserts representative content for every current metadata
family in scope:

- Project Brief
- Outline
- Style Guide
- Style Samples
- Locations
- Organizations
- Plot Threads
- Characters
- Relationships
- Chapters

This satisfies the design contract that the matrix prove meaningful section
contents, not merely heading indices.

## 4. Optional-section omission matrix

Accepted evidence:

- `test_export_project_markdown_omits_all_optional_project_metadata_sections_when_empty`

The omission regression proves optional metadata sections are absent when the
project has no optional metadata, while required export sections still render
according to current behavior. This locks the negative path for an otherwise
empty project and prevents future export additions from accidentally emitting
empty optional headings.

## 5. Runtime file export matrix

Accepted evidence:

- `test_project_export_file_includes_all_current_metadata_sections_in_order`

The runtime regression exercises `/rp project export <project-id>` through the
existing command path, monkeypatches `HERMES_HOME`, verifies the exported
Markdown file exists under the profile-safe local export path, preserves the
quoted `MEDIA:"<path>"` response contract, and asserts the current metadata
section order including `## Plot Threads` in the written file.

## 6. Test-only reverse-scope contract

Controller review confirms the phase stayed within the approved test-only and
status-only boundaries:

- S1 changed only the two allowed novel DB/runtime test files plus
  controller-owned Phase 136 design/checklist artifacts.
- S2 changed only this acceptance report and `checklist.yaml` status/evidence.
- Reverse-scope guard was empty for `README.md`, `src`, `tests`, `run_agent.py`,
  `cli.py`, `gateway/run.py`, `design/HERMES_TAVERN_DESIGN.md`,
  `design/codestable/architecture/ARCHITECTURE.md`, and `build/lib` after the
  S2 status pass.
- No prompt/provider/generation/retrieval/credential/importer/archive/graph,
  protected core, cloud/collaboration, media/TTS/image, or safety-bypass paths
  were modified.

## 7. Architecture/root-design writeback

No architecture or root-design writeback is required. Phase 136 changes no
runtime/product behavior and introduces no stable system capability beyond
regression coverage for already-current export behavior. `design.md` remains
`status: approved`; acceptance is recorded in this report and checklist status.

## 8. Requirement/roadmap writeback and verification evidence

Requirement writeback: none. The design frontmatter declares no requirement, and
this phase adds regression tests/status only rather than a user-visible ability.

Roadmap writeback: none. The design frontmatter declares no roadmap or
roadmap_item, and the phase was not seeded from a roadmap entry.

Controller-run S2 verification:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py` — passed with no output.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py -q -o 'addopts=' -p no:cacheprovider` — passed, `199 passed in 9.68s`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider` — passed, `961 passed in 44.29s`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` — passed, `961 passed in 43.26s`.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase136-metadata-export-matrix/design.md --require doc_type --require status --require feature` — passed.
- `python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase136-metadata-export-matrix/hermes-tavern-phase136-metadata-export-matrix-acceptance.md --require doc_type --require status --require feature` — passed.
- `python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-05-hermes-tavern-phase136-metadata-export-matrix/checklist.yaml` — passed.
- `git diff --name-only -- README.md src tests run_agent.py cli.py gateway/run.py design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md build/lib` — empty output.
- `git diff --check` — passed.

## 9. Attention candidates and residual deferred work

Attention updates: none. This phase did not expose a new project-wide command,
build, environment, or workflow rule that needs to be added to `attention.md`.

Residual deferred work remains unchanged:

- relationship graph/rename/default binding
- automatic extraction or generated metadata
- archive ZIP/import/export
- retrieval/vectorization/provider-routing integration
- cloud/collaboration/backend accounts
- any safety-boundary bypass surface

Those items remain outside Phase 136 and should only advance through separate
CodeStable phases.
