---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase152-persona-json-export"
status: accepted
date: "2026-06-07"
created: "2026-06-07"
updated: "2026-06-07"
owner: codestable-cron
tags: [hermes-tavern, persona, export, acceptance, offline]
---

# Phase 152 Persona JSON Export Acceptance

> 阶段：S2 验收/写回
> 验收日期：2026-06-07
> 关联设计文档：design/codestable/features/2026-06-07-hermes-tavern-phase152-persona-json-export/design.md
> 关联 checklist：design/codestable/features/2026-06-07-hermes-tavern-phase152-persona-json-export/checklist.yaml

## 1. S1 scope contract

- S1 is implemented as one bounded local `/rp persona export <persona>` command for one existing stored persona.
- Implementation resolves personas through existing `TavernStore.get_persona(...)` behavior, including `last`.
- It writes a UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/personas`.
- It prefers `personas.raw_json` when that value parses as a JSON object; otherwise it uses a normalized fallback assembled from the persona row fields.
- Success output includes `file:` plus quoted `MEDIA:"<path>"`.
- S2 is documentation-only and does not alter source/runtime/tests/README/core/plugin/build artifact files.

## 2. Interface/schema contract

- No schema/table/index/migration files were changed in S2; feature implementation remains on top of existing `personas` shape.
- S1 read path still uses `TavernStore.get_persona(...)`, and no new DB APIs were introduced.
- `personas(id, name, content, raw_json, source_path, created_at)` remains unchanged by Phase 152.
- S2 checks do not apply code mutations to DB schema or data model layers.

## 3. Command/output contract

- Command path: `/rp persona export <persona>`.
- Missing argument form returns `Usage: /rp persona export <persona>`.
- Missing persona returns the existing bounded not-found messaging used by persona lookup and supports existing `last` no-persona behavior.
- Success output includes:
  - `Persona exported as JSON.`
  - `file: <path>`
  - `MEDIA:"<path>"`
- Existing command-family behavior remains under `/rp persona ...`.

## 4. No-session / no-mutation behavior

- The command runs command-only, no active-session requirement.
- It does not create, switch, or mutate any session/message rows.
- It does not mutate stored persona rows.
- It does not call session persona binding, use/clear/temp, or prompt compiler paths.
- It does not mutate schema, prompts, provider/model routing, generation, retrieval/vectorization, or credentials.
- Existing S1 tests assert session/message invariance for export operations.

## 5. Export placement / MEDIA / path containment

- Exports are written to profile-safe path:
  `get_hermes_home()/plugins/hermes-tavern/exports/personas`.
- Filename generation is sanitized (`persona_<id>.json`) and stays under that directory.
- JSON is written as UTF-8 with pretty formatting.
- Response uses quoted MEDIA marker, preserving spaces in paths and matching Tavern media-delivery contract.

## 6. Raw-object / fallback shape contract

- When `personas.raw_json` parses as a JSON object (non-null, non-array, non-primitive), it is written as-is except for pretty formatting.
- When raw JSON is unavailable, invalid JSON, or not a JSON object, the normalized fallback payload includes:
  - `name`: stored persona name
  - `content`: stored persona content text
  - `source_path`: stored persona import source
  - `created_at`: stored persona creation timestamp
- Fallback shape matches Phase 149/150/151 behavior and does not invent new fields.

## 7. Verification status

All S1 acceptance criteria verified on 2026-06-07:

| # | Criteria | Status |
|---|----------|--------|
| 1 | Writes one UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/personas` | ✅ Pass |
| 2 | Export works without active RP session | ✅ Pass |
| 3 | `last` resolves through existing persona lookup | ✅ Pass |
| 4 | Stored raw JSON objects exported unchanged except pretty formatting | ✅ Pass |
| 5 | Invalid/missing/non-object raw JSON falls back to normalized row fields | ✅ Pass |
| 6 | Response includes `file:` and quoted `MEDIA:"<path>"` | ✅ Pass |
| 7 | Sanitized filenames remain inside export directory | ✅ Pass |
| 8 | Generated help and README include `/rp persona export <persona>` | ✅ Pass |
| 9 | Persona/session/message rows not mutated by export | ✅ Pass |
| 10 | No schema, importer, prompt, provider, generation, content-mode, or safety changes | ✅ Pass |

### Gate runs (verified in controller)

- ✅ `py_compile`: passed
- ✅ Focused tests (116): passed
- ✅ Tavern-wide tests (1097): passed
- ✅ Protected files diff: empty
- ✅ Whitespace: clean
- ✅ YAML validation: passed

## 8. Architecture / root-design writeback

- ARCHITECTURE.md: added Phase 152 capability summary entry, `/rp persona export <persona>` to command surface, and Phase 152 export boundary.
- HERMES_TAVERN_DESIGN.md: added `/rp persona export <persona>` to Persona commands list, Phase 152 implementation entry, and export-parity reference.

## 9. Deferred scope (not in Phase 152)

- Bulk persona export
- Persona editing/deletion/merge
- Persona JSON import format expansion
- Persona validation tooling
- Prompt-order semantics
- Generation settings
- Provider/model routing changes
- Retrieval/vectorization
- Content-mode changes
- Minors/underage handling
- Archive import/export
- Safety-bypass boundaries
