---
doc_type: feature-acceptance
feature: "2026-06-06-hermes-tavern-phase138-scene-beat-metadata"
status: accepted
date: "2026-06-06"
summary: >-
  Phase 138 is accepted as Scene Beat Metadata v1. It adds local,
  scene-scoped beat rows managed by /rp scene beat add/list/inspect/update/delete
  and optional owning-scene Markdown export visibility only. Controller
  verification confirms scene beats remain metadata-only/inert with no
  prompt/debug/context-budget, active-session, provider/model routing,
  content-mode, credential, retrieval/vectorization, generation, media, archive,
  graph, automatic extraction, or safety behavior changes.
tags: [novel, scene-beats, metadata, export, acceptance]
---

# Phase 138 Scene Beat Metadata v1 Acceptance

> Phase: S2 verify/accept/write current docs
> Controller verification date: 2026-06-06
> Design: `design/codestable/features/2026-06-06-hermes-tavern-phase138-scene-beat-metadata/design.md`
> Checklist: `design/codestable/features/2026-06-06-hermes-tavern-phase138-scene-beat-metadata/checklist.yaml`

## 1. Scope and design contract

Phase 138 is accepted as a local scene-scoped metadata feature. S1 implemented
`novel_scene_beats` and `/rp scene beat ...`; S2 closed acceptance/status and
project-level writeback only.

Accepted S1 implementation surface:

- `src/hermes_tavern/db_novel.py`
- `src/hermes_tavern/runtime_novel.py`
- `src/hermes_tavern/commands.py`
- `README.md`
- focused DB/runtime/command/README docs tests

Accepted S2 status/writeback surface:

- this acceptance report
- `checklist.yaml` status/evidence updates
- `design/codestable/architecture/ARCHITECTURE.md`
- `design/HERMES_TAVERN_DESIGN.md`

The feature remains metadata-only/inert and scene-scoped. It does not add
beat generation, ordering workflows, prompt modules, active-session behavior,
provider/model routing, content-mode behavior, retrieval/vectorization,
generation, media, archive import/export, graph behavior, automatic extraction,
or safety-bypass behavior.

## 2. Interface/schema contract

Accepted schema and persistence contract:

- `novel_scene_beats(id, scene_id, label, beat_text, created_at, updated_at)`
  exists as a local SQLite table.
- `scene_id` references an existing `novel_scenes(id)` row and is indexed by
  `idx_novel_scene_beats_scene ON novel_scene_beats(scene_id, id)`.
- `create_scene_beat(scene_id, label, beat_text)` creates a row after trimming
  and rejecting blank labels or blank beat text.
- `list_scene_beats(scene_id)` validates the owning scene and returns rows in
  deterministic `id ASC` order.
- `get_scene_beat(beat_id)`, `update_scene_beat(beat_id, beat_text)`, and
  `delete_scene_beat(beat_id)` provide bounded inspect/update/delete behavior.
- Labels are immutable in v1; update changes `beat_text` only.
- Missing scenes and missing beats are handled with bounded command output rather
  than tracebacks.

Evidence:

- `tests/test_hermes_tavern_novel_db.py` covers migration/index presence, CRUD,
  blank input validation, missing owner behavior, ordering, export inclusion,
  export omission, and cross-scene scoping.
- `tests/test_hermes_tavern_novel_runtime.py` covers runtime command UX,
  help visibility, missing/blank behavior, and no-leak prompt/context behavior.

## 3. Command and export behavior

Accepted command surface:

```text
/rp scene beat add <scene-id> <label> <beat...>
/rp scene beat list <scene-id>
/rp scene beat inspect <beat-id>
/rp scene beat update <beat-id> <beat...>
/rp scene beat delete <beat-id>
```

Accepted export behavior:

- `/rp project export [id]` emits scene beats only under the owning scene.
- Exported rows render as `- <label>: <beat_text>` under a `Scene beats:` block.
- The block is omitted for scenes with no beats.
- Cross-scene leakage is covered by a regression test.
- Scene beats are local Markdown export metadata only; no import/archive format
  or ST asset exporter behavior changed.

## 4. Acceptance criteria

- [x] **AC1** — migration creates `novel_scene_beats` with `scene_id`, `label`,
  `beat_text`, timestamps, and `idx_novel_scene_beats_scene`.
  - Evidence: DB migration/index tests and architecture schema writeback.
- [x] **AC2** — store helpers create, list, inspect, update, and delete scene
  beat rows with deterministic `id ASC` ordering.
  - Evidence: focused DB helper tests.
- [x] **AC3** — store helpers reject missing scenes, blank labels, and blank beat
  text with bounded behavior.
  - Evidence: focused DB/runtime missing/blank tests.
- [x] **AC4** — `/rp scene beat add/list/inspect/update/delete` commands exist
  in help output and return compact local metadata messages.
  - Evidence: runtime command tests plus command-table/help tests.
- [x] **AC5** — README Core commands and command/docs tests include the scene
  beat literals.
  - Evidence: `tests/test_hermes_tavern_readme_docs.py` and README command line.
- [x] **AC6** — `/rp project export [id]` emits scene beats only under the owning
  scene and omits beat blocks when none exist.
  - Evidence: export inclusion/omission/cross-scene tests.
- [x] **AC7** — beat marker text does not appear in `/rp debug prompt` or
  `/rp debug context`.
  - Evidence: active linked-session no-leak runtime test.
- [x] **AC8** — reverse-scope checks show no protected core, `runtime.py`,
  prompt/debug/context-budget, provider/model/content/generation,
  retrieval/vectorization, media, importer, plugin shim, build, archive, graph,
  automatic extraction, or safety-bypass changes.
  - Evidence: S2 protected diff guard empty; S1 protected guard is recorded in
    the checklist verification ledger.
- [x] **AC9** — architecture/root-design writeback reflects Phase 138 as current
  and removes stale beats-deferred wording.
  - Evidence: `ARCHITECTURE.md` now current through Phase 138; root design
    lists scene beats in §6.7/§13/§17 and stale Phase 121–137/"beats deferred"
    scans are clean outside historical feature-design text.

## 5. Checklist mapping

- [x] **C1 Metadata schema** — `novel_scene_beats` table/index and helper
  behavior accepted.
- [x] **C2 Command surface** — `/rp scene beat ...` command/help/docs visibility
  accepted.
- [x] **C3 Export visibility** — owning-scene export inclusion/omission/scoping
  accepted.
- [x] **C4 No prompt/provider side effects** — no-leak tests and reverse-scope
  guards accepted.
- [x] **C5 S2 docs/status writeback** — acceptance report, checklist,
  architecture, and root design finalized after controller verification.

## 6. Architecture and root-design writeback

Updated `design/codestable/architecture/ARCHITECTURE.md`:

- `Last updated` moved to `2026-06-06`.
- Phase list now includes Phase 138 Scene Beat Metadata v1.
- `/rp` command surface and DB schema headings are current through Phase 138.
- Command list includes the five `/rp scene beat ...` forms.
- Schema section includes `novel_scene_beats` and `idx_novel_scene_beats_scene`.
- Metadata exclusion and known-constraint sections explicitly list scene beats as
  command/export-visible only and excluded from prompt/debug/context-budget,
  vectorization/retrieval, provider/model routing, content mode, credentials,
  generation, media/TTS/image, archive, ST importer/exporter, graph, and
  safety-bypass behavior.

Updated `design/HERMES_TAVERN_DESIGN.md`:

- §6.7 lists Scene Beat Metadata v1 as current local scene-scoped metadata.
- §6.7 and §13.2 command lists include `/rp scene beat ...` literals.
- §13.1 model list includes scene beats; old "beats remain deferred" wording was
  removed while keeping volume/arc, location-map/geocode derivatives, revision
  notes, relationship graph/rename, and automatic extraction deferred.
- §17.1/§17.2 phase range is current through Phase 121–138.
- §17.2 documents `Scene beats:` export rows under owning scenes after `Goal:`
  and before narration controls/session content.

No requirement or roadmap backfill was needed: Phase 138 was not rooted in a
roadmap item, and the root design/architecture docs are the current project-level
ability records for this metadata-only slice.

## 7. Controller verification evidence

Controller reran all acceptance gates after Codex executor drafted S2 docs/status
and after controller patching/root-design finalization:

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile ...` for the Phase 138 source
  and focused test evidence files — passed with no output.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
  — `301 passed in 11.54s`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
  — `992 passed in 43.25s`.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
  — `992 passed in 51.42s`.
- CodeStable frontmatter/YAML validators for design, acceptance, and checklist —
  all passed (`1 passed, 0 failed` each).
- S2 protected reverse-scope guard for `src`, `tests`, `README.md`, core,
  gateway, plugin, and build paths — empty output.
- Stale-wording guard for Phase 137 headings, Phase 121–137 root-design text,
  old beats-deferred root-design wording, and the pre-final acceptance typo —
  empty output.
- `git diff --check` — passed with no output.

## 8. Attention candidates

No new project-level attention candidates were identified. The existing
CodeStable attention rules (no core Hermes file edits from Tavern, no
`~/.hermes` hard-coding, no credential persistence, use focused pytest commands)
were sufficient.

## 9. Residual/deferred work

Still deferred and intentionally not implemented in Phase 138:

- generated beats, beat rewrite/expand/compress/scoring, and automatic beat
  extraction;
- beat reordering/label-renaming workflow;
- prompt module injection, context-budget effects, retrieval/vectorization,
  provider/model routing, content-mode behavior, credentials, generation, media,
  archive import/export, ST asset importer/exporter, graph behavior, automatic
  extraction, and safety behavior;
- volume/arc, location map/geocode derivatives, revision notes, relationship
  graph/rename, project archive ZIP/import, and broader novel import/export
  workflows.
