---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase154-chapter-json-export"
status: accepted
date: "2026-06-07"
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
tags: [hermes-tavern, chapter, export, acceptance, json]
---

# Phase 154 Chapter JSON Export Acceptance

> 阶段：S1 实现 + S2 验收/写回
> 验收日期：2026-06-07
> 关联设计文档：design/codestable/features/2026-06-07-hermes-tavern-phase154-chapter-json-export/design.md
> 关联 checklist：design/codestable/features/2026-06-07-hermes-tavern-phase154-chapter-json-export/checklist.yaml

## 1. S1 scope contract

- S1 is implemented as one bounded `/rp chapter export <chapter-id>` command for any stored novel chapter.
- Implementation resolves chapter through existing `get_chapter(chapter_id)`, rejecting `None` matches.
- It reads chapter metadata (title, chapter_number, summary, status, project_id) and associated scenes via `list_scenes(chapter_id)`.
- It writes a UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/chapters`.
- Success output includes `file:` plus quoted `MEDIA:"<path>"`.
- S2 is documentation-only and does not alter source/runtime/tests/README/core/plugin/build artifact files.

## 2. Interface/schema contract

- No schema/table/index/migration files were changed; feature uses existing `novel_chapters` and `novel_scenes` tables.
- S1 read path uses `get_chapter(chapter_id)`, `list_scenes(chapter_id)`, `get_chapter_summary(chapter_id)`.
- No new DB APIs were introduced.

## 3. Command/output contract

- Command path: `/rp chapter export <chapter-id>`.
- Not-found returns `No novel chapter found: <id>`.
- Success output includes:
  - `Chapter exported as JSON.`
  - `file: <path>`
  - `MEDIA:"<path>"`

## 4. Export payload contract

- JSON payload:
  - `hermes_tavern_export: true`
  - `exported_at`, `chapter_id`, `project_id`, `title`, `chapter_number`, `status`, `summary`
  - `scenes` array with `scene_id`, `title`, `scene_number`, `summary`, `status`, `session_id`
- Empty scenes array for chapters with zero scenes.
- Summary is empty string when not set.

## 5. Export placement / MEDIA / path containment

- Exports are written to profile-safe path:
  `get_hermes_home()/plugins/hermes-tavern/exports/chapters`.
- Filename: `chapter_<id>.json`.
- JSON is written as UTF-8 with pretty formatting.
- Response uses quoted MEDIA marker.

## 6. No-mutation behavior

- The command does not create, mutate, or delete any chapter/scene rows.
- It does not change chapter/scene lifecycle or schema.
- It does not mutate prompts, provider/model routing, generation, retrieval/vectorization, or credentials.

## 7. Verification status

All S1 acceptance criteria verified on 2026-06-07:

| # | Criteria | Status |
|---|----------|--------|
| 1 | Writes one UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/chapters` | ✅ Pass |
| 2 | Resolves chapter by integer ID; rejects not-found | ✅ Pass |
| 3 | Exports chapters with scenes, including scene metadata | ✅ Pass |
| 4 | Exports chapters with zero scenes (empty scenes array) | ✅ Pass |
| 5 | Includes chapter summary text when available | ✅ Pass |
| 6 | Response includes `file:` and quoted `MEDIA:"<path>"` | ✅ Pass |
| 7 | Sanitized filenames remain inside export directory | ✅ Pass |
| 8 | Generated help and README include `/rp chapter export <chapter-id>` | ✅ Pass |
| 9 | Chapter/scene rows not mutated by export | ✅ Pass |
| 10 | No schema, prompt, provider/model, generation, or safety changes | ✅ Pass |

### Gate runs (verified in controller)

- ✅ `py_compile`: passed
- ✅ Focused tests (248): passed
- ✅ Tavern-wide tests (1115): passed
- ✅ Protected files diff: empty
- ✅ Whitespace: clean
- ✅ YAML validation: passed

## 8. Architecture / root-design writeback

- ARCHITECTURE.md: added Phase 154 capability summary entry and `/rp chapter export <chapter-id>` to command surface.
- HERMES_TAVERN_DESIGN.md: added `/rp chapter export <chapter-id>` to chapter commands and Phase 154 implementation entry.

## 9. Deferred scope (not in Phase 154)

- Bulk chapter export
- Chapter import/merge
- Chapter editing tooling
- Cross-chapter analysis
- Prompt-order semantics
- Generation settings
- Provider/model routing changes
- Retrieval/vectorization
- Content-mode changes
- Minors/underage handling
- Archive import/export
- Safety-bypass boundaries
