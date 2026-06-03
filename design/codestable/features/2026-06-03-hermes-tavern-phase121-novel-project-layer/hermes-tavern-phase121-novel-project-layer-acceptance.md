---
doc_type: feature-acceptance
feature: 2026-06-03-hermes-tavern-phase121-novel-project-layer
status: accepted
verified_at: "2026-06-03"
---

## 1) Interface Contract

- DB schema and mixin wiring:
  - `src/hermes_tavern/db.py` and `src/hermes_tavern/db_novel.py` for `TavernStore` and `NovelDBMixin` construction.
  - `src/hermes_tavern/db_novel.py` for `novel_projects`, `novel_chapters`, `novel_scenes`, `novel_canon`, `novel_timeline` migrations and CRUD.
- CRUD/export + handlers:
  - `src/hermes_tavern/db_novel.py` for all novel CRUD and `export_project_markdown`.
  - `src/hermes_tavern/runtime_novel.py` for `/rp project|chapter|scene|canon|timeline` command families.
- Command registration and dispatch:
  - `src/hermes_tavern/runtime.py` command table and dispatch methods.
- Canon injection and session-context bridge:
  - `src/hermes_tavern/runtime_prompt_modules.py` (`session_canon_modules`).
- Session context display:
  - `src/hermes_tavern/runtime_sessions.py` (`session_info`).

### Command contract drift correction (applied)

Phase 121 feature surface is id-oriented in implementation, and docs are now aligned to:
- `project create/list/info/set/export`
- `chapter create/list`
- `scene create/list/start`
- `canon add/list/group`
- `timeline add/list`

`novel_scenes.session_id` is `TEXT` in the current schema.

`scene start` is implemented as `/rp scene start <scene-id>` and reuses existing `/rp start` session semantics by delegating to `runtime_lifecycle.start`.

## 2) Behavior and Decisions

### 2.1 DB schema and storage

- Novel data remains in the same `tavern.sqlite3` DB; no extra DB file is introduced.
- `novel_scenes.session_id` is persisted as `TEXT` and may be null.
- Scene linking is created through `/rp scene start <scene-id>` and persisted by `link_scene_session`.

### 2.2 Canon injection robustness

- Canon injection in `session_canon_modules()` now resolves chain through `session_id -> scene -> chapter -> project`.
- If project/canon lookups hit `sqlite3` DB errors at runtime, canon modules are skipped and RP continues.

### 2.3 Export behavior

- Export writes markdown to `get_hermes_home()/plugins/hermes-tavern/exports/project_{id}.md`.
- Export path is attached with quoted `MEDIA:"<path>"` marker.

## 3) Design §3 scenario evidence

### S1-S2

- `project create/list/info/set` behavior: `tests/test_hermes_tavern_novel_runtime.py:26-74`
- `runtime_novel.py` handlers and output formatting: `src/hermes_tavern/runtime_novel.py:98-236`

### S3

- `chapter create/list`: `tests/test_hermes_tavern_novel_runtime.py:76-134`, `src/hermes_tavern/runtime_novel.py:238-290`
- empty/default output semantics covered by tests: `tests/test_hermes_tavern_novel_runtime.py:178-206`

### S4-S5

- `scene create/list/start`: `tests/test_hermes_tavern_novel_runtime.py:208-312`
- session info context includes linked `project/chapter/scene`: `tests/test_hermes_tavern_novel_runtime.py:286-312`, `tests/test_hermes_tavern_novel_runtime.py:208-232`, `src/hermes_tavern/runtime_sessions.py`.

### S6-S7

- `canon add/list/group` and `timeline add/list`: `tests/test_hermes_tavern_novel_runtime.py:313-371`, `src/hermes_tavern/runtime_novel.py:292-520`

### S10-S17 export

- `export_project_markdown` composition and export path marker: `src/hermes_tavern/db_novel.py:160-390`, `src/hermes_tavern/runtime_novel.py:66-123`
- Empty project export fallback and session-linked scene export cases: `tests/test_hermes_tavern_novel_runtime.py:144-204`

### S12-S16

- Empty canon default: `tests/test_hermes_tavern_novel_db.py:133-147`, `src/hermes_tavern/db_novel.py:120-220`
- Empty canon does not inject prompt modules: `tests/test_hermes_tavern_novel_runtime.py:399-414`
- Unlinked scene listing text: `tests/test_hermes_tavern_novel_runtime.py:231-239`
- Missing project/scene errors: `tests/test_hermes_tavern_novel_runtime.py:86-95`, `tests/test_hermes_tavern_novel_runtime.py:289-296`

### 3.4 Canon DB-error skip guard

- Focused regression added for this slice: `tests/test_hermes_tavern_novel_runtime.py:416-440`
- Guard path: `src/hermes_tavern/runtime_prompt_modules.py`.

## 4) Reverse-scope verification

- No novel import command is advertised in `/rp help`: `tests/test_hermes_tavern_novel_runtime.py:419-422`
- No cloud sync/collaboration/timeline graphics/credential persistence paths introduced in this phase in the edited files.
- Existing session command surface remains unchanged (`/rp start`, `/rp end`, `/rp session`, `/rp switch`) and remains covered by dedicated runtime/session tests.

## 5) Controller verification (Phase 121 acceptance slice)

- Final acceptance status: **ACCEPTED**.
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/runtime_sessions.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts='` — passed; 91 passed in 4.60s.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-03-hermes-tavern-phase121-novel-project-layer/design.md --require doc_type --require status` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-03-hermes-tavern-phase121-novel-project-layer/hermes-tavern-phase121-novel-project-layer-acceptance.md --require doc_type --require status` — passed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-03-hermes-tavern-phase121-novel-project-layer/checklist.yaml` — passed.
- Reverse-scope scan for cloud/collaboration/import/timeline-graphics/credential/minor markers in novel runtime files — passed; no matches.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` — passed; 752 passed in 30.38s.
- `git diff --check` — passed.

## 6) Architecture / requirement / roadmap merge

- Architecture merge completed in `design/codestable/architecture/ARCHITECTURE.md`: Phase 121 capability summary, novel command families, novel schema tables, and canon prompt-module insertion are now present in the current snapshot.
- Root design merge completed in `design/HERMES_TAVERN_DESIGN.md`: §6.7 command syntax, §13 novel-engine scope, §17 export/import boundary, and §21 Phase 9 completion marker now match the implemented Phase 121 subset.
- Requirement backfill: no separate requirements directory exists in this CodeStable root; root design §2/§6.7/§13 now carries the current capability record for this project.
- Roadmap backfill: no roadmap item/frontmatter is attached to this feature; skipped.

## 7) Residuals / next-step candidates

- Design §2.5 suggested a reusable convention: `TavernStore` domain-specific CRUD should live in `db_{domain}.py`, with `db.py` retaining base connection/migration/session core. This is a good `cs-decide` candidate if the user wants the convention formalized later.
- Future root-design items remain out of scope for this accepted slice: outline/write/revision/canon-check/project import/relationship-state tooling.
