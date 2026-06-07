---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-08-hermes-tavern-phase167-project-json-export"
date: "2026-06-08"
summary: "Phase 167 S1 implementation and S2 acceptance complete. Project JSON bundle export implemented and verified."
owner: codestable-cron
---

# Phase 167 Acceptance: Project JSON Bundle Export

## S1 Implementation (Codex Executor)

Executor profile (gpt-5.3-codex-spark, standalone CLI v0.137.0) successfully
implemented the bounded project JSON bundle export command. Files changed:

- `src/hermes_tavern/runtime_novel.py`: +221 lines (project_export_json function + json subcommand branch)
- `src/hermes_tavern/commands.py`: +1 line (help line)
- `README.md`: +1 line (command table)
- `tests/test_hermes_tavern_novel_runtime.py`: +170 lines (focused tests)
- `tests/test_hermes_tavern_readme_docs.py`: +6 lines (explicit docs test)

## S2 Acceptance (Controller)

### Gates

| Gate | Result |
|------|--------|
| py_compile (runtime_novel, commands, tests) | PASS |
| Targeted tests (novel_runtime + readme_docs) | 329 PASS |
| Full Tavern test suite | 1196 PASS |
| Prohibited files diff | EMPTY |
| git diff --check | CLEAN |
| No `from hermes_constants` import issue | CONFIRMED |
| Payload keys use entity-specific IDs | CONFIRMED |

### Architecture/Root Design Writeback

- `ARCHITECTURE.md`: Updated phase list (1–167), phase description added, command
  surface updated with `/rp project export json <project-id>`.
- `HERMES_TAVERN_DESIGN.md`: Phase 167 description added, project export
  command family updated to include `/export json`.

### Checklist Status

All checks passed:
- C1 (Command surface): PASS — `/rp project export json` visible in command table, runtime help, README, and tests.
- C2 (Bundle export creates correct directory structure): PASS — Creates project directory with subdirectories per entity type, each with valid JSON files.
- C3 (Summary output): PASS — Summary lists entity types with correct counts, directory path, and quoted MEDIA marker.
- C4 (Edge cases): PASS — Empty project reports 0 exports, not-found returns error, malformed ID returns usage string.
- C5 (No prompt/provider side effects): PASS — No prohibited file changes, no prompt/debug/context contamination.
- C6 (Existing Markdown export unchanged): PASS — `/rp project export [id]` behavior identical.
