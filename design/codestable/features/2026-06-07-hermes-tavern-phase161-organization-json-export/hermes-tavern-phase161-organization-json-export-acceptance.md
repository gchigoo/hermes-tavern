---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-07-hermes-tavern-phase161-organization-json-export"
date: "2026-06-07"
---

# Phase 161 Acceptance: Organization JSON Export

## Verification Summary

| Gate | Result |
|------|--------|
| py_compile (runtime_novel.py, commands.py, tests) | PASS |
| Targeted tests (novel_runtime + readme_docs) | 301 passed |
| Full Tavern tests (all test_hermes_tavern_*.py, excl. async) | 1003 passed |
| Protected files diff | empty |
| git diff --check | clean |

## Implementation Summary

Codex executor (gpt-5.3-codex-spark, standalone CLI v0.137.0) implemented Phase 161 S1:
- Added `organization_export()` function in `src/hermes_tavern/runtime_novel.py`
- Added `export` branch to `organization_command()` dispatcher
- Updated `_ORGANIZATION_USAGE` to include export
- Updated commands.py help_lines, README Core commands table
- Added 8 focused tests in `test_hermes_tavern_novel_runtime.py`
- Controller fixed payload key: `"id"` → `"organization_id"` (pattern consistency)

No protected files modified. No schema/prompt/provider/generation changes.

## Architecture Writeback

- ARCHITECTURE.md: Updated — `/rp organization export <organization-id>` added to command reference and Phase 161 export boundary documented.
- HERMES_TAVERN_DESIGN.md: Updated — `/rp organization export <organization-id>` added to organization command list.

## Next Steps

Remaining metadata entities with inspect commands but no JSON export:
- Plot threads (134), style samples (135), default bindings (137), scene beats (138), revision notes (139).

Next candidate: Phase 162 plot thread JSON export.
