---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-07-hermes-tavern-phase160-location-json-export"
date: "2026-06-07"
---

# Phase 160 Acceptance: Location JSON Export

## Verification Summary

| Gate | Result |
|------|--------|
| py_compile (runtime_novel.py, commands.py, tests) | PASS |
| Targeted tests (novel_runtime + readme_docs) | 292 passed |
| Full Tavern tests (all test_hermes_tavern_*.py) | 1159 passed |
| Protected files diff | empty |
| git diff --check | clean |

## Implementation Summary

Codex executor (gpt-5.3-codex-spark, standalone CLI v0.137.0) implemented Phase 160 S1:
- Added `location_export()` function in `src/hermes_tavern/runtime_novel.py`
- Added `export` branch to `location_command()` dispatcher
- Updated `_LOCATION_USAGE` to include export
- Updated commands.py help_lines, README Core commands table
- Added 6 focused tests in `test_hermes_tavern_novel_runtime.py`
- Added README assertion in `test_hermes_tavern_readme_docs.py`

No protected files modified. No schema/prompt/provider/generation changes.

## Architecture Writeback

- ARCHITECTURE.md: Updated — `/rp location export <location-id>` added to command reference (line 384) and Phase 160 export boundary documented (lines 729–734).
- HERMES_TAVERN_DESIGN.md: Updated — `/rp location export <location-id>` added to location command list (line 1230).

## Next Steps

Remaining metadata entities with inspect commands but no JSON export:
- Organizations (133), plot threads (134), style samples (135), default bindings (137),
  scene beats (138), revision notes (139).

Next candidate: Phase 161 organization JSON export.
