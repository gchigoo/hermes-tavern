---
doc_type: feature-acceptance
feature: 2026-06-04-hermes-tavern-phase124-project-style-guide
status: accepted
verified_at: "2026-06-04"
summary: >
  Project Style Guide v1 contract is implemented through S5 docs/writeback and
  architectural root design updates. Executor verification produced a scope-safe
  documentation-ready state, and controller-level verification accepted the
  feature after rerunning targeted and full regression gates.
tags:
  - novel
  - project
  - style-guide
  - prompt
  - acceptance
---

## 1. Interface Contract

- DB contract (`src/hermes_tavern/db_novel.py`)
  - Added `novel_project_style_guides(project_id UNIQUE, style_text, timestamps)` with
    `set/get/clear/get_project_style_guide_for_session` helpers.
  - Missing-project validation remains `ValueError("Project not found")`.
  - `clear_project_style_guide` is idempotent.
- Command surface (`src/hermes_tavern/runtime_novel.py`)
  - `/rp project style [project-id]` inspect path with active-project fallback.
  - `/rp project style set [project-id] <text>` with explicit clear/update flows.
  - `/rp project style clear [project-id]`.
- Prompt/export integration (`src/hermes_tavern/runtime_prompt_modules.py`, `src/hermes_tavern/db_novel.py`)
  - Linked-session module `system/project_style:<project title>` injected before canon/preset
    when style text exists and linked-session scope resolves.
  - Empty/whitespace style and sqlite3 failures skip this module only.
- Export/docs contract (`src/hermes_tavern/db_novel.py`)
  - `export_project_markdown()` emits `## Style Guide` after `## Summary` and before
    `## Chapters` for non-empty style text.

## 2. Behavior and Decisions

- Project style guide is project-scoped, linked-session visible metadata for novel projects.
- No protected-core, provider routing, credential, cloud, collaboration, or safety-bypass behavior changed.
- Command parsing uses explicit `set/clear` subcommands to reduce ambiguity.
- Scope constraints from previous slices remain:
  - no project archive ZIP/import or novel import,
  - no outline editing,
  - no character or relationship state,
  - no write continue/rewrite/expand/compress,
  - no provider credential persistence or safety bypass paths.

## 3. Acceptance Scenario Evidence

- Targeted runtime and project-command scope covered by phase-124 executor implementation.
- Project-style debug-prompt and export tests in `tests/test_hermes_tavern_novel_runtime.py`,
  `tests/test_hermes_tavern_novel_db.py`, `tests/test_hermes_tavern_commands.py`,
  and `tests/test_hermes_tavern_readme_docs.py` cover set/inspect/clear, scope errors,
  sqlite fallback, prompt ordering, and markdown placement.

## 4. Architecture and Root Design Merge

- Updated `design/codestable/architecture/ARCHITECTURE.md`:
  - Added Phase 124 Project Style Guide v1 to capability summary.
  - Added `novel_project_style_guides` to DB schema.
  - Added `/rp project style` forms to current command surface.
  - Added prompt pipeline module entry for project-style module.
- Updated `design/HERMES_TAVERN_DESIGN.md`:
  - `style_guide` moved from deferred project metadata to current behavior.
  - Added `/rp project style` command forms.
  - Documented markdown `## Style Guide` placement in project export.
  - Project/novel archive/import, outline editing, relationship/character state,
    write rewrite/expand/compress, and other original deferred scope remain deferred.

## 5. Requirement and Roadmap Disposition

- Requirement document is not defined for this feature beyond `design.md`; requirement
  backfill remains not applicable.
- Roadmap metadata is not declared in the feature design frontmatter; roadmap
  backfill not applicable.

## 6. Attention Candidates

- No new persistent environment/tooling candidate identified.

## 7. Legacy and Deferred Scope (Preserved)

- cloud / collaboration / backend account workflows deferred,
- provider credential persistence deferred,
- provider safety bypass deferred,
- minors/underage handling deferred,
- project archive ZIP / novel import deferred,
- character state and relationship state deferred,
- outline and write continue/rewrite/expand/compress deferred.

## 8. Executor Verification

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py` → passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py -q -o 'addopts='` → passed; 181 passed in 5.73s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` → failed; 808 passed, 8 failed in 29.93s (image provider jobs fail in executor environment).
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase124-project-style-guide/design.md --require doc_type --require status` → passed; 1 passed, 0 failed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-04-hermes-tavern-phase124-project-style-guide/checklist.yaml` → passed; 1 passed, 0 failed.
- `git diff --check` → passed.
- Scope guard checks (`git diff --name-only -- run_agent.py cli.py gateway/run.py`, forbidden-term grep against source/tests/README) → no hits.

## 9. Controller Verification (Accepted)

- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/runtime_prompt_modules.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py` → passed.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_runtime.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py -q -o 'addopts='` → passed; 181 passed in 6.94s.
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` → passed; 816 passed in 31.64s.
- CodeStable validators for design, checklist, and this acceptance report all passed.
- `git diff --check` passed.
- Protected-core guard reported no `run_agent.py`, `cli.py`, or `gateway/run.py` diffs.
- Controller diff allowlist contained only the four S5 docs/status files.

## 10. Residuals

- S5 acceptance writeback is complete from executor perspective.
- Feature is accepted after controller verification.
- The executor sandbox's full regression failure was not reproduced by controller full-suite verification.

