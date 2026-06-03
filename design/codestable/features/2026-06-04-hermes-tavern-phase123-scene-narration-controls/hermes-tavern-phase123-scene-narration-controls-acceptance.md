---
doc_type: feature-acceptance
feature: 2026-06-04-hermes-tavern-phase123-scene-narration-controls
status: accepted
verified_at: "2026-06-04"
summary: >
  Scene Narration Controls v1 accepted after controller verification and
  architecture/root-design writeback. Scene metadata now persists POV/tense,
  exposes a tight narration command surface, injects linked-scene guidance into
  prompt composition, and renders narration blocks in Markdown exports.
tags:
  - novel
  - scene
  - narration
  - pov
  - tense
  - hermes-tavern
---

## 1) Interface Contract

- DB surface (`src/hermes_tavern/db_novel.py`)
  - `NovelDBMixin` now owns `novel_scene_narration_controls` persistence and
    helpers for set/get/clear and linked-session lookup.
  - Error contracts include `ValueError("Scene not found")` and
    `ValueError("Invalid tense")`.

- Command surface (`src/hermes_tavern/commands.py`, `src/hermes_tavern/runtime_novel.py`)
  - `/rp scene narration <scene-id>` for inspect and clear/POV/tense set forms.
  - `/rp help` exposes only these four narration commands.

- Prompt/export integration (`src/hermes_tavern/runtime_prompt_modules.py`, `src/hermes_tavern/db_novel.py`)
  - Linked-session prompt module `scene_narration:<scene title>` (system,
    before_user).
  - Markdown export prints narration controls under each scene heading after goal and
    before fallback message text.

## 2) Behavior and Decisions

- DB contract:
  - Scene narration data is optional per scene.
  - `set_scene_narration_controls` accepts partial updates and persists
    only non-empty fields.
  - Blank updates clear individual fields; blank POV + blank tense removes row.
  - `scene_id` linkage requires existing parent scene.

- Command behavior:
  - `inspect` displays current non-empty POV and tense labels.
  - `clear` and `pov/tense` commands are narrow and deterministic.
  - `tense` accepts only `past` and `present` at write time.
  - Missing scene and malformed tense map to user-visible error messages.

- Runtime + export behavior:
  - Prompt injection is active only for sessions linked to the active scene and
    when controls are non-empty.
  - `scene_narration` and `scene_goal` modules are inserted in that order before
    note/prefill context.
  - SQLite lookup failures skip narration module only, preserving other prompt
    modules.

- Architecture and docs decision:
  - POV/tense controls are now core scope for Phase 123 scene metadata and command
    contracts.
  - No new storage backends, import formats, or provider/network behavior added.

## 3) Acceptance scenario evidence

- Database contract evidence:
  - `tests/test_hermes_tavern_novel_db.py` covers migration, set/get/update,
    clear/partial-clear, missing scene, and invalid tense guard cases.

- Command contract evidence:
  - `tests/test_hermes_tavern_novel_runtime.py` and
    `tests/test_hermes_tavern_commands.py` cover inspect/clear/POV/tense paths,
    malformed arguments, missing scene translation, and no-controls inspect.

- Prompt/export evidence:
  - `tests/test_hermes_tavern_novel_runtime.py` covers linked-session
    narration module inclusion/exclusion and ordering.
  - `tests/test_hermes_tavern_novel_db.py` and docs tests cover
    markdown narration block placement and label stability.

## 4) Architecture and root design merge

- `design/codestable/architecture/ARCHITECTURE.md` updated for:
  - snapshot date `2026-06-04`,
  - Phase 123 capability summary,
  - command-surface inclusion of `/rp scene narration` forms,
  - prompt pipeline and schema entries for
    `novel_scene_narration_controls`,
  - module index / known constraints notes.

- `design/HERMES_TAVERN_DESIGN.md` updated for:
  - Scene metadata now includes POV and tense,
  - current command syntax includes `/rp scene narration <scene-id>` inspect plus
    clear/POV/tense forms,
  - markdown export semantics for scene narration controls,
  - explicit move of narration controls from deferred vision list to current scope.

## 5) Requirement and roadmap disposition

- `design/codestable/requirements.gitkeep` exists only; there is no per-feature
  requirements doc with a `requirement` frontmatter target for this feature.
- No `roadmap` / `roadmap_item` metadata exists in the feature design doc,
  so roadmap backfill is not applicable.

## 6) Attention candidates

- No recurring environment/tooling pitfall discovered in this slice that should be
  promoted into `.codestable/attention.md` yet.
- Candidate (optional for next slice): track a stable controller verification
  command bundle for end-to-end Phase S5 handoff.

## 7) Legacy and deferred scope (preserved)

- Preserved deferred from original vision / prior phases:
  - deferred outline editing,
  - deferred write continue/rewrite/expand/compress,
  - deferred project archive ZIP/import,
  - deferred character state,
  - deferred relationship state,
  - deferred canon check/correlation,
  - deferred cloud / collaboration flows,
  - no provider credential work,
  - no minors/underage handling,
  - no provider safety bypass paths.

## 8) Controller verification (passed)

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py` → passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py -q -o 'addopts='` → passed; 163 passed in 6.28s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` → passed; 798 passed in 30.73s.
- `validate-yaml.py` checks for design, acceptance report, and checklist → passed; 1 passed, 0 failed for each target.
- `git diff --check` → passed.
- Protected-core and source/test/README status guards → passed; no `run_agent.py`, `cli.py`, `gateway/run.py`, `src/`, `tests/`, `plugins/`, or `README.md` changes.
- Controller diff-aware prohibited-scope scan over added docs lines → passed; only explicit deferred/no/prohibited-scope mentions of out-of-scope capabilities were added.
