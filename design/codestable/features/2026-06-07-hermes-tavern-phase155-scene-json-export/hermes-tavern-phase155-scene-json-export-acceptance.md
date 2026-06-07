---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase155-scene-json-export"
status: accepted
date: "2026-06-07"
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
tags: [hermes-tavern, scene, export, acceptance, json]
---

# Phase 155 Scene JSON Export Acceptance

> 阶段：S1 实现 + S2 验收/写回（合并为一次 tick）
> 验收日期：2026-06-07
> 关联设计文档：design/codestable/features/2026-06-07-hermes-tavern-phase155-scene-json-export/design.md
> 关联 checklist：design/codestable/features/2026-06-07-hermes-tavern-phase155-scene-json-export/checklist.yaml

## 1. S1 scope contract

- S1 is implemented as one bounded `/rp scene export <scene-id>` command for any stored novel scene.
- Implementation resolves scene through existing `get_scene(scene_id)`, rejecting `None` matches.
- It reads scene metadata (id, chapter_id, title, scene_number, summary, status, session_id, created_at, updated_at).
- It writes a UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/scenes`.
- Success output includes `file:` plus quoted `MEDIA:"<path>"`.
- S1 also updates `_SCENE_USAGE`, scene command dispatcher, commands.py help_lines, and README.

## 2. Interface/schema contract

- No schema/table/index/migration files were changed; feature uses existing `novel_scenes` table.
- S1 read path uses `get_scene(scene_id)`.
- No new DB APIs were introduced.
- `db_novel.py` was not modified.

## 3. Command/output contract

- Command path: `/rp scene export <scene-id>`.
- Not-found returns `No novel scene found: <id>`.
- Non-positive ID returns usage string.
- Missing args returns usage string.
- Success output includes:
  - `Scene exported as JSON.`
  - `file: <path>`
  - `MEDIA:"<path>"`

## 4. Test contract

6 new tests added to `tests/test_hermes_tavern_novel_runtime.py`:
- `test_scene_export_by_id` — exports a scene with summary, verifies file contents
- `test_scene_export_not_found` — rejects non-existent scene ID
- `test_scene_export_non_positive_id` — rejects 0 and negative IDs
- `test_scene_export_missing_args` — returns usage when no ID given
- `test_scene_export_no_mutation` — scene data unchanged after export
- `test_scene_export_with_session` — session_id included when linked

All 6 tests pass. Targeted suite (254 tests) and full Tavern suite (1121 tests) pass.

## 5. Verification summary

| Check | Expected | Actual |
|-------|----------|--------|
| py_compile | passes | passed |
| Targeted tests (254) | passes | 254 passed in 10.82s |
| Full Tavern suite (1121) | passes | 1121 passed in 50.76s |
| Protected-files diff | empty | empty |
| git diff --check | clean | clean |
| design.md YAML | valid | valid |
| checklist.yaml YAML | valid | valid |

## 6. Architecture/design writeback

- ARCHITECTURE.md updated: Phase 155 entry added to capability summary
- HERMES_TAVERN_DESIGN.md: Phase 155 scope documented
- Design doc status: accepted
- Checklist status: accepted (S1 completed, S2 acceptance completed)

## 7. Changed files (5 source + 4 design)

- `src/hermes_tavern/runtime_novel.py` — scene export function, dispatcher branch, _SCENE_USAGE update
- `src/hermes_tavern/commands.py` — help_lines entry
- `README.md` — Core commands table update
- `tests/test_hermes_tavern_novel_runtime.py` — 6 new test functions
- `tests/test_hermes_tavern_readme_docs.py` — README assertion update
- `design/codestable/features/2026-06-07-hermes-tavern-phase155-scene-json-export/` — design.md, checklist.yaml, acceptance.md
- `design/codestable/architecture/ARCHITECTURE.md` — Phase 155 entry
- `design/HERMES_TAVERN_DESIGN.md` — Phase 155 scope

## 8. Notes

- No architect pass was run (gpt-5.5 rate-limited). Controller materialized artifacts following the proven Phase 149–154 export pattern.
- S1 implemented by Codex executor (gpt-5.3-codex-spark).
- S2 acceptance and architecture writeback completed by controller in the same tick.
