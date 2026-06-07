---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-08-hermes-tavern-phase166-revision-note-json-export"
date: "2026-06-08"
summary: "Phase 166 S1 implementation and S2 acceptance complete. Revision note JSON export by ID implemented and verified."
owner: codestable-cron
---

# Phase 166 Acceptance: Revision Note JSON Export

## S1 Implementation (Codex Executor)

Executor profile (gpt-5.3-codex-spark, standalone CLI v0.137.0) successfully
implemented the bounded revision note JSON export command. Files changed:

- `src/hermes_tavern/runtime_novel.py`: +44 lines (export function + dispatcher branch)
- `src/hermes_tavern/commands.py`: +1 line (help line)
- `README.md`: +1 line (command table)
- `tests/test_hermes_tavern_novel_runtime.py`: +128 lines (focused tests)

## S2 Acceptance (Controller)

### Gates

| Gate | Result |
|------|--------|
| py_compile (runtime_novel, commands, tests) | PASS |
| Targeted tests (novel_runtime + readme_docs) | 323 PASS |
| Full Tavern test suite | 1190 PASS |
| Prohibited files diff | EMPTY |
| git diff --check | CLEAN |
| No `from hermes_constants` import issue | CONFIRMED |
| Payload key = `note_id` (not generic `id`) | CONFIRMED |

### Architecture/Root Design Writeback

- `ARCHITECTURE.md`: Updated phase list (1–166), phase description added, command
  surface updated with `/rp project revision export <note-id>`.
- `HERMES_TAVERN_DESIGN.md`: Phase 166 description added, revision notes command
  family updated to include `/export`.

### Checklist Status

All checks passed:
- C1 (Command surface): PASS — `/rp project revision export` visible in command table, runtime help, README, and tests.
- C2 (Export payload and file output): PASS — Valid JSON with note metadata, file: and MEDIA output, rejects not-found/malformed IDs.
- C3 (No prompt/provider side effects): PASS — No prohibited file changes, no prompt/debug/context contamination.
- C4 (Existing commands unchanged): PASS — add/list/inspect/update/delete behavior identical.
