---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-07-hermes-tavern-phase165-scene-beat-json-export"
date: "2026-06-07"
---

# Phase 165 Acceptance: Scene Beat JSON Export

## Verification Summary

| Gate | Result |
|------|--------|
| py_compile (runtime_novel.py, commands.py, tests) | PASS |
| Targeted tests (novel_runtime + readme_docs) | 316 passed |
| Full Tavern tests (all test_hermes_tavern_*.py) | 1183 passed |
| Protected files diff (S1) | empty |
| git diff --check (S1) | clean |

## Implementation Summary

Codex executor (gpt-5.3-codex-spark, standalone CLI v0.137.0) implemented Phase 165 S1:
- Added `scene_beat_export()` function in `src/hermes_tavern/runtime_novel.py`
- Added `export` branch to `scene_beat()` dispatcher (after `delete` case)
- Updated `_SCENE_USAGE` to include `/rp scene beat export <beat-id>`
- Updated commands.py help_lines, README Core commands table
- Added focused tests in `test_hermes_tavern_novel_runtime.py` (export by ID, not-found, non-positive ID, missing args, path containment, MEDIA output, no mutation)
- Updated readme_docs tests

No protected files modified. No schema/prompt/provider/generation changes.
Payload key uses `beat_id` — consistent with design spec.

## Architecture Writeback

- ARCHITECTURE.md: Updated — `/rp scene beat export <beat-id>` added to command reference, Phase 165 export boundary documented, phase listing updated.
- HERMES_TAVERN_DESIGN.md: Phase 165 export line added after scene beat metadata section.

## Next Steps

Remaining metadata entities with inspect commands but no JSON export:
- Revision notes (Phase 139)

Remaining S2 acceptance writeback for Phase 164 (default binding export).
