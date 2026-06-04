---
doc_type: feature-acceptance
feature: "2026-06-04-hermes-tavern-phase127-project-brief"
status: accepted
date: "2026-06-04"
summary: >
  Phase 127 Project Brief v1 is accepted: local novel project type and premise
  metadata persist in novel_project_briefs, are visible through /rp project
  brief, /rp project info, and Markdown export, and controller verification plus
  architecture/root-design writeback passed while prompt assembly, provider
  routing, content mode, generation, credentials, protected core files, and
  deferred project metadata remain unchanged.
tags: [novel, project, metadata, export, acceptance]
---

# Phase 127: Project Brief v1 Acceptance

> 阶段：阶段 3（验收闭环）
> 验收日期：2026-06-04
> 关联方案：design/codestable/features/2026-06-04-hermes-tavern-phase127-project-brief/design.md

## 1. Interface Contract Check

- `novel_project_briefs` side table exists and is the backing table.
- Required schema literal:
```sql
novel_project_briefs(id, project_id, project_type, premise_text, created_at, updated_at)
CREATE INDEX idx_novel_project_briefs_project ON novel_project_briefs(project_id)
```
- Required project command literals appear in docs and code surface:
  - `/rp project brief [project-id]`
  - `/rp project brief inspect [project-id]`
  - `/rp project brief type set <project-id> <novel|serial|rp|worldbuilding|other>`
  - `/rp project brief type clear <project-id>`
  - `/rp project brief premise set <project-id> <text>`
  - `/rp project brief premise clear <project-id>`
- `project info` exposes both fields when present:
  - `/rp project info <id>`
- Export contract records brief metadata block:
  - Markdown export emits `## Project Brief` **after** `## Summary` only when `project_type` or `premise_text` is present
  - Labels use `Type:` and `Premise:`

## 2. Behavior And Decision Check

- The S3 acceptance/report slice captures only docs/writeback, not implementation.
- `type` and `premise` are treated as **Project Brief metadata**, not prompt or generation controls.
- DB write/delete behavior for brief fields must remain local and bounded to novel project rows.
- No provider/model routing/generation/content-mode/prompt-injection changes are claimed in this phase.

## 3. Acceptance Scenario Check

- [x] S3-C1: checklist precondition / scope boundaries.
  - Evidence: Phase 127 was the only in-progress checklist, and the final diff is limited to the four allowed docs/status files.
- [x] S3-C2: persistence contract for type/premise set/clear/get behavior.
  - Evidence: controller reran the focused novel DB/runtime/docs test set and the full test suite.
- [x] S3-C3: project brief command usage and bounded failures.
  - Evidence: controller reran `tests/test_hermes_tavern_novel_runtime.py`, `tests/test_hermes_tavern_commands.py`, and `tests/test_hermes_tavern_readme_docs.py` in the focused gate.
- [x] S3-C4: `/rp project info` and Markdown export visibility behavior.
  - Evidence: controller reran the novel DB/runtime tests that cover info/export visibility and omission when no brief exists.
- [x] S3-C5: no prompt/provider/generation/provider safety regressions.
  - Evidence: no source/runtime/provider/prompt files changed in S3, and the full suite passed.

## 4. Terminology Consistency

- `novel_project_briefs` naming and `project_type`/`premise_text` fields are consistent between schema, acceptance, and architecture.
- `Project Brief` naming used consistently across command docs, capability summary, and architecture.

## 5. Architecture Writeback

- `design/codestable/architecture/ARCHITECTURE.md` update includes:
  - Phase 127 capability line for Project Brief v1
  - `/rp project brief ...` command surface literals
  - DB schema note for `novel_project_briefs`
  - Explicit note that Project Brief does not participate in `_session_prompt_modules`, model routing, provider, content mode, or generation pipeline

## 6. Requirement Writeback

- No requirement doc target changed in this S3 slice.
- The current capability is captured in architecture/root-design writeback instead.

## 7. Roadmap Writeback

- No roadmap entry is modified in this slice.
- Keep roadmap status unchanged.

## 8. Attention Candidates

- None for this slice. The existing CodeStable attention boundaries already cover protected core files, credentials, local paths, and adult-fiction safety constraints.

## 9. Deferred Boundaries And Residuals

- Keep deferred: `outline`, `canon_policy`, `content_mode`, default card/preset/lorebook IDs, future metadata/sub-objects.
- Keep deferred/prohibited: prompt injection, provider behavior, generation behavior, credentials behavior, provider routing, cloud/collab, minors/underage paths, protected core edits.
- No adult-content/RP compatibility bypass added for this feature.

## 10. Controller Verification

- `codex --profile architect exec --json --color never --disable image_generation --sandbox read-only --cd /Users/steven/Projects/hermes-tavern <Phase 127 S3 artifact prompt>`
  - Result: passed; `/tmp/hermes-tavern-architect-phase127-s3.jsonl` ended with `RESULT: ARCHITECT_ARTIFACT` and selected S3 acceptance/writeback only.
- `codex --profile executor exec --json --color never --disable image_generation --sandbox workspace-write --cd /Users/steven/Projects/hermes-tavern <Phase 127 S3 docs/status prompt>`
  - Result: completed; `/tmp/hermes-tavern-executor-phase127-s3.jsonl` drafted the allowed docs/status files. One expected pre-read failed before the new acceptance file existed and patch-context misses were recovered; no Codex 429/rate-limit/exhaustion signal occurred.
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/db_novel.py src/hermes_tavern/runtime_novel.py src/hermes_tavern/commands.py tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py`
  - Result: passed (controller rerun).
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_novel_db.py tests/test_hermes_tavern_novel_runtime.py tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider`
  - Result: passed; 164 passed in 4.47s (controller rerun).
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider`
  - Result: passed; 855 passed in 33.82s (controller rerun).
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider`
  - Result: passed; 855 passed in 32.78s (controller rerun).
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase127-project-brief/design.md --require doc_type --require status --require feature`
  - Result: passed; 1 passed, 0 failed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-04-hermes-tavern-phase127-project-brief/hermes-tavern-phase127-project-brief-acceptance.md --require doc_type --require status --require feature`
  - Result: passed; 1 passed, 0 failed.
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --yaml-only --file design/codestable/features/2026-06-04-hermes-tavern-phase127-project-brief/checklist.yaml`
  - Result: passed; 1 passed, 0 failed.
- `git diff --check`
  - Result: passed.
- `git diff --name-only -- run_agent.py cli.py gateway/run.py`
  - Result: passed; no protected core file diffs.
- Controller diff allowlist / reverse-scope review
  - Result: passed; S3 changed only Phase 127 docs/status files, architecture, and root design. No source/runtime/test/README/provider/prompt/protected-core files changed.
