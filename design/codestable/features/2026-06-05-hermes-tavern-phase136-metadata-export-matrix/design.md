---
doc_type: feature-design
status: approved
feature: "2026-06-05-hermes-tavern-phase136-metadata-export-matrix"
date: "2026-06-05"
summary: >
  Novel Metadata Export Matrix v1 adds test-only regression coverage for the
  complete current project metadata Markdown export order and runtime file export
  path after Phase 135. It makes no product, source, prompt, provider,
  generation, retrieval, credential, importer, archive, graph, or core-file
  behavior changes.
tags: [novel, metadata, export, regression, test-only, offline]
---

# Phase 136: Novel Metadata Export Matrix v1

## 0. Terms

| Term | Meaning | Conflict guard |
|---|---|---|
| Metadata Export Matrix | Regression tests that create multiple current novel metadata families together and verify one Markdown export order. | Not a new command, schema table, importer, archive format, graph, extraction flow, or prompt feature. |
| Current Project Metadata | Phase 127-135 project metadata: brief, outline, style guide, style samples, locations, organizations, plot threads, character states, and relationships. | Does not include deferred default bindings, relationship graph/rename, automatic extraction, retrieval, vectorization, summarization, provider routing, or generation. |
| Runtime File Export Path | `/rp project export [id]` writing local Markdown under `get_hermes_home()` and returning the existing quoted `MEDIA:"<path>"` attachment marker. | No archive ZIP, cloud sync, backend account, or ST asset importer/exporter behavior. |

Startup inspection found no active planned/pending/in-progress/draft feature
checklist under `design/codestable/features` and no existing Phase 136
directory. Phase 135 is accepted. Source inspection found
`TavernStore.export_project_markdown()` owns current Markdown section ordering in
`src/hermes_tavern/db_novel.py`, while `/rp project export [id]` writes the local
file through the existing runtime command path. Test inspection found strong
per-family coverage, but no single focused matrix that requires all current
Phase 127-135 optional metadata sections to coexist in one export, and runtime
export coverage does not include plot threads in the same file-export path as
style samples, locations, organizations, characters, and relationships.

## 1. Decisions And Constraints

### Need

The project now has several small optional project metadata families. Each recent
phase added focused CRUD/export/no-leak tests, but the export surface is now
order-sensitive enough that a single co-presence regression test is valuable.
This phase hardens the already-current behavior without adding another domain
object or changing runtime behavior.

### Success

- A DB-level export regression creates one project containing Project Brief, Outline, Style Guide, Style Samples, Locations, Organizations, Plot Threads, Characters, Relationships, and Chapters, then asserts the full section order and representative content.
- A runtime export regression uses `/rp project export [id]`, reads the written Markdown file, keeps the existing quoted `MEDIA:"<path>"` contract, and includes Plot Threads in the same file-export path as the other current metadata sections.
- An omission regression proves an otherwise empty project omits optional metadata sections while retaining the existing required export sections.
- The implementation is test-only and should pass against current source behavior. If a new matrix test exposes a source bug, S1 must stop and report a bug candidate rather than broadening into source fixes.
- No source, README, architecture, root design, prompt, provider, model-router, content-mode, generation, retrieval, vectorization, summarization, credential, importer, archive, graph, rename, automatic extraction, or protected core behavior changes occur.

### Explicit Non-Goals

- No new `/rp` commands, command aliases, help text, README commands, schema tables, migrations, CRUD helpers, or export format changes.
- No relationship graph, relationship rename, automatic extraction, generated metadata, default card/preset/lorebook binding, canon policy, content-mode metadata, or archive ZIP/import/export.
- No prompt module injection and no changes to debug prompt, debug context, context-budget reporting, model routing, provider adapters, content mode, credentials, generation, memory, retrieval, vectorization, automation, media, TTS, or images.
- No ST card/preset/lorebook/persona importer or exporter changes.
- No cloud sync, collaboration, backend accounts, credential persistence, provider-safety bypass, or Hermes core rewrites.
- No edits to `run_agent.py`, `cli.py`, or `gateway/run.py`.
- No age, date-of-birth, school-grade, minor/underage, or sexual-safety-classification examples, fields, commands, or fixtures.

### Complexity

Small test-only slice. It is local/offline, uses existing store/runtime test
fixtures, does not require service lifecycle commands, and does not require
product or architecture choices.

### Key Decisions

1. Implement S1 by editing tests only.
2. Add one DB-level matrix test in `tests/test_hermes_tavern_novel_db.py`.
3. Add one runtime `/rp project export [id]` matrix test, or extend the existing runtime export-order coverage with Plot Threads only if that keeps the diff smaller and clearer.
4. Keep assertions focused on cross-family ordering, representative content, optional-section omission, and the existing local MEDIA export contract.
5. Do not add helper abstractions unless repeated index assertions make the tests materially harder to read.
6. Treat any required source change as outside S1 and route it as a separate bug-fix phase.

## 2. Names And Flow

### 2.1 Noun Layer

Current:

- `src/hermes_tavern/db_novel.py` owns `export_project_markdown(project_id)`.
- Current export ordering is Summary, optional Project Brief, optional Outline, optional Style Guide, optional Style Samples, optional Locations, optional Organizations, optional Plot Threads, optional Characters, optional Relationships, Chapters, Canon, and Timeline.
- `src/hermes_tavern/runtime_novel.py` owns `/rp project export [id]` and writes Markdown under the Hermes home export path.
- Existing tests cover individual metadata families, help/docs literals, no-leak boundaries, and several export-order cases.

Change:

- Add regression tests only.
- Expected DB matrix test name: `test_export_project_markdown_orders_all_current_metadata_sections`.
- Expected runtime matrix test name: `test_project_export_file_includes_all_current_metadata_sections_in_order`.
- Expected omission test name: `test_export_project_markdown_omits_all_optional_project_metadata_sections_when_empty`.

### 2.2 Orchestration Layer

Test flow:

    TavernStore test setup
      -> create project + current metadata families
      -> export_project_markdown(project_id)
      -> assert section order and representative content

    TavernRuntime test setup
      -> set HERMES_HOME to tmp path
      -> create project + metadata families
      -> handle /rp project export <id>
      -> assert quoted MEDIA marker and local file path
      -> read Markdown file
      -> assert same cross-family section order

Flow constraints:

- Tests do not start services or make network/provider calls.
- Tests do not invoke generation or mutate prompt assembly.
- Tests use adult-fiction/RP-compatible neutral fictional examples only, with no prohibited safety examples.

### 2.3 Mount Points

| Mount | Purpose |
|---|---|
| `tests/test_hermes_tavern_novel_db.py` | Add DB-level Markdown export co-presence and optional-section omission regression coverage. |
| `tests/test_hermes_tavern_novel_runtime.py` | Add or minimally extend runtime file-export coverage so Plot Threads are covered with the current metadata export path and MEDIA marker. |

Non-mounts:

- `src/**`
- `README.md`
- `design/HERMES_TAVERN_DESIGN.md`
- `design/codestable/architecture/ARCHITECTURE.md`
- `run_agent.py`, `cli.py`, `gateway/run.py`
- `build/lib/**`
- `plugins/**` outside normal test imports
- `design/codestable/**` during S1 implementation, except controller-owned materialization/status updates before or after executor work

### 2.4 Slicing

1. S1 implementation: add test-only metadata export matrix coverage in the two novel test files and run focused verification. No source fixes are allowed in S1.
2. S2 acceptance/status: after S1 passes, create the acceptance artifact and update this feature checklist status. No architecture/root design writeback is expected because no product behavior changes.

### 2.5 Structure Health

No pre-feature micro-refactor.

The target test files are large, but the new assertions belong beside the
existing novel DB export and runtime project-export tests. Adding a separate
test helper module would be extra indirection for a small test-only hardening
slice. If the executor adds helpers, they should remain local to the touched test
file and serve only section-order assertions.

## 3. Acceptance Criteria

1. DB export matrix asserts the complete current optional metadata order:
   Summary -> Project Brief -> Outline -> Style Guide -> Style Samples -> Locations -> Organizations -> Plot Threads -> Characters -> Relationships -> Chapters.
2. DB export matrix asserts representative content from each current metadata family.
3. Empty-project omission coverage proves optional metadata sections are omitted when absent while existing required sections remain.
4. Runtime project export coverage writes a local Markdown file under the profile-safe Hermes home export path, preserves the quoted MEDIA marker, and asserts the same current metadata order including Plot Threads.
5. Focused tests pass for `tests/test_hermes_tavern_novel_db.py` and `tests/test_hermes_tavern_novel_runtime.py`.
6. Tavern plugin test glob passes.
7. Reverse-scope guard shows no source, README, architecture, root design, build artifact, protected core, prompt, provider, model-router, content-mode, generation, retrieval/vectorization, memory/summarization, media/TTS/image, importer, archive, graph, rename, automatic extraction, credential, cloud/collaboration, or safety-bypass files changed.
8. S1 does not create acceptance reports or architecture/root-design writebacks.

## 4. Verification Commands

S1 focused verification:

    PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    git diff --name-only -- run_agent.py cli.py gateway/run.py src README.md design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md build/lib
    git diff --check

S2 acceptance/status verification:

    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
    PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider
    python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-05-hermes-tavern-phase136-metadata-export-matrix/design.md --require doc_type --require status --require feature
    python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-05-hermes-tavern-phase136-metadata-export-matrix/checklist.yaml
    git diff --check
