---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase157-timeline-json-export"
status: accepted
date: "2026-06-07"
summary: >
  Phase 157 S1 implemented via Codex executor (gpt-5.3-codex-spark).
  Controller verified all gates: 1137 full tests pass, no prohibited
  files changed, diff clean. S2 acceptance and architecture writeback
  completed by controller.
---

# Phase 157 S2 Acceptance: Timeline JSON Export

## Verification Results

| Gate | Expected | Actual |
|------|----------|--------|
| py_compile (4 files) | passes | passed |
| Novel runtime + README tests | passes | 270 passed in 12.51s |
| Full Tavern tests | passes | 1137 passed in 49.93s |
| Protected files diff | empty | empty |
| git diff --check | passes | clean |
| YAML validation (design.md) | passes | passed |
| YAML validation (checklist.yaml) | passes | passed |

## Files Changed

| File | Changes |
|------|---------|
| `src/hermes_tavern/runtime_novel.py` | +38 lines: timeline_export() function + export branch in timeline_command() + updated _TIMELINE_USAGE |
| `src/hermes_tavern/commands.py` | +1 line: /rp timeline export <timeline-id> help |
| `README.md` | +1 line: timeline export in Core commands table |
| `tests/test_hermes_tavern_novel_runtime.py` | +152 lines: 7 focused timeline export tests |
| `tests/test_hermes_tavern_readme_docs.py` | +1 line: README assertion |

## Implementation Summary

- `timeline_export()` resolves timeline event by integer ID via `runtime.store.get_timeline_event()`
- Writes UTF-8 JSON to `<hermes_home>/plugins/hermes-tavern/exports/timeline/timeline_<id>.json`
- Returns `file:` + quoted `MEDIA:"<path>"`
- Rejects not-found with "No timeline event found: <id>"
- Rejects non-positive/missing IDs with _TIMELINE_USAGE
- No schema, prompt, provider, generation, credential, content-mode, or safety changes
- db_novel.py unchanged (get_timeline_event already exists)

## Architecture Writeback

Updated ARCHITECTURE.md:
- Added Phase 157 entry under command surface listing
- Updated phase summary header to "121–157 complete"
- Updated command surface header to "through Phase 157"
- Updated DB schema header
- Added Phase 157 timeline export boundary constraint
- Updated timeline command family to include `/rp timeline export <timeline-id>`
