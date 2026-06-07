---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-07-hermes-tavern-phase162-plot-thread-json-export"
date: "2026-06-07"
---

# Phase 162 Acceptance: Plot Thread JSON Export

## Verification Summary

| Gate | Result |
|------|--------|
| py_compile (runtime_novel.py, commands.py, tests) | PASS |
| Targeted tests (novel_runtime + readme_docs) | 303 passed |
| Full Tavern tests (all test_hermes_tavern_*.py, excl. async) | 1170 passed |
| Protected files diff | empty |
| git diff --check | clean |

## Implementation Summary

Codex executor (gpt-5.3-codex-spark, standalone CLI v0.137.0) implemented Phase 162 S1:
- Added `plot_thread_export()` function in `src/hermes_tavern/runtime_novel.py`
- Added `export` branch to `plot_command()` dispatcher (after `delete` case)
- Updated `_PLOT_THREAD_USAGE` to include export
- Updated commands.py help_lines, README Core commands table
- Added focused tests in `test_hermes_tavern_novel_runtime.py` (export, not-found, non-positive ID, missing args, path containment, no mutation)
- Updated readme_docs tests

No protected files modified. No schema/prompt/provider/generation changes.

Payload key uses `plot_thread_id` — consistent with established convention (`organization_id`, `location_id`, etc.).

## Architecture Writeback

- ARCHITECTURE.md: Updated — `/rp plot thread export <plot-thread-id>` added to command reference and Phase 162 export boundary documented.
- HERMES_TAVERN_DESIGN.md: Phase 162 line item added.

## Next Steps

Remaining metadata entities with inspect commands but no JSON export:
- Style samples (135), default bindings (137), scene beats (138), revision notes (139).

Next candidate: Phase 163 style sample JSON export.
