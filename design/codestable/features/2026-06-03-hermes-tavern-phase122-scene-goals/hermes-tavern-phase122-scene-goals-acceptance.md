---
doc_type: feature-acceptance
feature: 2026-06-03-hermes-tavern-phase122-scene-goals
status: accepted
verified_at: "2026-06-04"
---

# Phase 122: Scene Goals v1 — Acceptance Report

> 关联方案 doc: `design/codestable/features/2026-06-03-hermes-tavern-phase122-scene-goals/design.md`
> 验收范围: S1–S5 completed; C1–C3 passed by controller verification.

## 1. Interface Contract

- **DB contract**: `src/hermes_tavern/db_novel.py` owns `novel_scene_goals` plus `set_scene_goal()`, `get_scene_goal()`, `clear_scene_goal()`, and `get_scene_goal_for_session()`.
- **Command contract**: `/rp scene goal <scene-id> [text]` sets or inspects a goal, and `/rp scene goal clear <scene-id>` clears it.
- **Prompt contract**: linked sessions with a non-empty goal receive `system/scene_goal:<scene title>` with content `Scene goal: <goal text>` before author-note modules.
- **Export contract**: `/rp project export` writes a `Goal: <text>` line directly under the matching scene heading when a scene goal exists.

## 2. Behavior and Decisions

- Setting a goal is idempotent: repeated writes replace the current goal for the same scene.
- Empty set text is rejected; explicit `clear` is required to remove a goal.
- Missing scenes return bounded user-facing messages rather than leaking internals.
- SQLite errors during prompt lookup skip only the scene-goal module and keep prompt debug usable.
- Scope isolation is preserved: only the session linked through `novel_scenes.session_id` receives the scene-goal module.
- Export visibility is Markdown-only and does not introduce project/novel import, ZIP/JSON archive export, or new storage formats.

## 3. Acceptance Scenario Evidence

- **Scenarios 1–3 (set / inspect / clear)**: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py -q -o 'addopts='` → passed; 31 passed in 1.08s.
- **Scenario 4 (linked debug prompt includes goal module)**: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_runtime.py -k scene_goal -q -o 'addopts='` → passed; 12 passed, 19 deselected in 0.46s.
- **Scenario 5 (unlinked session excludes goal)**: covered by the same `scene_goal` focused runtime tests → passed.
- **Scenario 6 (Markdown export includes goal)**: `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts='` → passed; 107 passed in 5.36s.
- **Scenarios 7–10 (usage, missing scene, blank text, sqlite skip)**: covered by novel runtime tests and `scene_goal` focused selection above → passed.
- **Full regression gate**: `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` → passed; 768 passed in 30.14s.

Reverse-scope evidence:
- `git diff --check` → passed.
- Protected/source/test/README status guards → passed; no `run_agent.py`, `cli.py`, `gateway/run.py`, `src/`, `tests/`, `plugins/`, or `README.md` changes.
- Controller diff-aware added-docs scan → passed; no non-deferred prohibited feature markers were added.

## 4. Terminology Consistency

- `Scene Goal` remains the user-facing concept from the design.
- `novel_scene_goals` is used only for the DB table / storage contract.
- `scene_goal:<scene title>` is used only for prompt module identity.
- Deferred concepts remain explicitly deferred: outline editing, write continue/rewrite/expand/compress, POV/tense controls, project archive export, canon check/conflict, relationship state, and character state.

## 5. Architecture Merge

Updated `design/codestable/architecture/ARCHITECTURE.md`:
- Phase 122 added to the capability summary.
- Prompt pipeline now lists `scene_goal` between canon/persona and author-note modules.
- `/rp scene goal <scene-id> [text]` and `/rp scene goal clear <scene-id>` are included in the current command surface.
- `novel_scene_goals` is included in the current DB schema snapshot.
- `db_novel.py`, `runtime_novel.py`, and `runtime_prompt_modules.py` descriptions mention scene-goal responsibilities.

Updated `design/HERMES_TAVERN_DESIGN.md`:
- Scene goals moved out of the deferred writing-command list.
- Scene goal commands are listed beside project/chapter/scene commands.
- Scene goals are documented as scene metadata.
- Markdown export visibility is documented as `Goal: <text>` under the scene heading.
- Project/novel import and archive ZIP remain deferred.

## 6. Requirement Writeback

No standalone requirement document exists for this feature (`design/codestable/requirements.gitkeep` only), and the feature design has no `requirement` frontmatter. The product-level capability record was therefore updated in `design/HERMES_TAVERN_DESIGN.md` and the current architecture snapshot instead.

## 7. Roadmap Writeback

No roadmap writeback is required: the feature design has no `roadmap` / `roadmap_item` frontmatter, and this CodeStable root currently has only `design/codestable/roadmap.gitkeep`.

## 8. Attention Candidates

No new `attention.md` candidate was identified. The existing startup constraints (plugin-only architecture, no protected core edits, no credential persistence, adult-fiction boundary) already covered this slice.

## 9. Residuals

- Phase 122 is accepted for Scene Goals v1.
- Remaining original-vision writing features stay deferred and should be handled as future CodeStable features: outline editing, write continue/rewrite/expand/compress, POV/tense controls, project archive export, canon check/conflict, relationship state, and character state.
