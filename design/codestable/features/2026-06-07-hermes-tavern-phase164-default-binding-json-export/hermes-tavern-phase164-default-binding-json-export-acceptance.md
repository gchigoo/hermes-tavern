---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-07-hermes-tavern-phase164-default-binding-json-export"
date: "2026-06-07"
---

# Phase 164 Acceptance: Default Binding JSON Export

## Verification Summary

| Gate | Result |
|------|--------|
| py_compile (runtime_novel.py, commands.py, tests) | PASS |
| Targeted tests (novel_runtime + readme_docs) | 316 passed |
| Full Tavern tests (all test_hermes_tavern_*.py, novel subset) | 316/316 passed |
| Protected files diff (S1) | empty |
| git diff --check (S1) | clean |

## Implementation Summary

Codex executor (gpt-5.3-codex-spark, standalone CLI v0.137.0) implemented Phase 164 S1:
- Added `binding_export()` function in `src/hermes_tavern/runtime_novel.py`
- Added `export` branch to `binding_command()` dispatcher (after `clear` case)
- Updated `BINDING_USAGE` to include `/rp binding export <binding-id>`
- Updated commands.py help_lines, README Core commands table
- Added focused tests in `test_hermes_tavern_novel_runtime.py` (export by ID, not-found, non-positive ID, missing args, path containment, MEDIA output, no mutation)
- Updated readme_docs tests

No protected files modified. No schema/prompt/provider/generation changes.
Payload key uses `binding_id` — consistent with design spec.

## Architecture Writeback (S2)

- ARCHITECTURE.md: Updated — `/rp binding export <binding-id>` added to command reference, Phase 164 export boundary documented, phase listing updated.
- HERMES_TAVERN_DESIGN.md: Phase 164 export description added after default binding metadata section.

## Next Steps

Remaining metadata entities with inspect commands but no JSON export:
- Revision notes (Phase 139)
