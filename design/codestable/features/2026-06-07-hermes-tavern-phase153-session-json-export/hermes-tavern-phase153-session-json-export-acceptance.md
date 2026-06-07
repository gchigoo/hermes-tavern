---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase153-session-json-export"
status: accepted
date: "2026-06-07"
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
tags: [hermes-tavern, session, export, acceptance, offline, json]
---

# Phase 153 Session JSON Export Acceptance

> 阶段：S1 实现 + S2 验收/写回
> 验收日期：2026-06-07
> 关联设计文档：design/codestable/features/2026-06-07-hermes-tavern-phase153-session-json-export/design.md
> 关联 checklist：design/codestable/features/2026-06-07-hermes-tavern-phase153-session-json-export/checklist.yaml

## 1. S1 scope contract

- S1 is implemented as one bounded `/rp session export <id>` command for any stored session.
- Implementation resolves sessions through existing `list_sessions_by_id_prefix_for_scope(...)`, rejecting 0 and >1 matches.
- It reads all messages via paginated `get_messages_page(...)` loops.
- It writes a UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/sessions`.
- It matches the existing st-json export format from `runtime_lifecycle.export()` for payload consistency.
- Success output includes `file:` plus quoted `MEDIA:"<path>"`.
- S2 is documentation-only and does not alter source/runtime/tests/README/core/plugin/build artifact files.

## 2. Interface/schema contract

- No schema/table/index/migration files were changed; feature uses existing `sessions` and `messages` tables.
- S1 read path uses `list_sessions_by_id_prefix_for_scope(...)`, `get_messages_page(...)`, `get_card(...)`, `get_preset(...)`, `get_lorebook(...)`.
- No new DB APIs were introduced.

## 3. Command/output contract

- Command path: `/rp session export <id>`.
- Missing argument form returns `Usage: /rp session export <id>`.
- Not-found returns `Session not found: <id>`.
- Ambiguous prefix returns `Multiple sessions match <id>: [id1], [id2]. Use a longer session id.`
- Success output includes:
  - `Session exported as JSON.`
  - `file: <path>`
  - `MEDIA:"<path>"`

## 4. Export payload contract

- JSON payload matches existing st-json shape from `runtime_lifecycle.export()`:
  - `hermes_tavern_export: true`
  - `exported_at`, `session_title`, `card_name`, `content_mode`, `preset_name`, `lorebook_name`
  - `message_count`, `messages` array
  - Card data included when available
  - Swipe metadata included from `metadata_json` when present

## 5. Export placement / MEDIA / path containment

- Exports are written to profile-safe path:
  `get_hermes_home()/plugins/hermes-tavern/exports/sessions`.
- Filename sanitization: `session_<alnum-id-prefix>.json`.
- JSON is written as UTF-8 with pretty formatting.
- Response uses quoted MEDIA marker.

## 6. No-mutation behavior

- The command does not create, switch, or mutate any session/message rows.
- It does not change session lifecycle (start/end/pause/resume/switch/archive/clone).
- It does not mutate schema, prompts, provider/model routing, generation, retrieval/vectorization, or credentials.

## 7. Verification status

All S1 acceptance criteria verified on 2026-06-07:

| # | Criteria | Status |
|---|----------|--------|
| 1 | Writes one UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/sessions` | ✅ Pass |
| 2 | Resolves session by ID prefix; rejects ambiguous (>1) and not-found (0) | ✅ Pass |
| 3 | Exports all session messages including swipe metadata | ✅ Pass |
| 4 | Exports sessions with zero messages (empty messages array) | ✅ Pass |
| 5 | Includes card/preset/lorebook name resolution | ✅ Pass |
| 6 | Response includes `file:` and quoted `MEDIA:"<path>"` | ✅ Pass |
| 7 | Sanitized filenames remain inside export directory | ✅ Pass |
| 8 | Generated help and README include `/rp session export <id>` | ✅ Pass |
| 9 | Session/message rows not mutated by export | ✅ Pass |
| 10 | No schema, prompt, provider/model, generation, or safety changes | ✅ Pass |

### Gate runs (verified in controller)

- ✅ `py_compile`: passed
- ✅ Focused tests (120): passed
- ✅ Tavern-wide tests (1108): passed
- ✅ Protected files diff: empty
- ✅ `hermes_constants` import check: clean (uses `hermes_tavern.hermes_home`)
- ✅ Whitespace: clean
- ✅ YAML validation: passed

## 8. Architecture / root-design writeback

- ARCHITECTURE.md: added Phase 153 capability summary entry and `/rp session export <id>` to command surface.
- HERMES_TAVERN_DESIGN.md: added `/rp session export <id>` to Session commands list and Phase 153 implementation entry.

## 9. Deferred scope (not in Phase 153)

- Bulk session export
- Session import/merge
- Session message search
- Session editing/deletion tooling
- Prompt-order semantics
- Generation settings
- Provider/model routing changes
- Retrieval/vectorization
- Content-mode changes
- Minors/underage handling
- Archive import/export
- Safety-bypass boundaries
