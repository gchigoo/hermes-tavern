---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase158-relationship-json-export"
status: accepted
date: "2026-06-07"
summary: >
  Phase 158 S1 implemented via Codex executor (gpt-5.3-codex-spark).
  Controller verified all gates: 1144 full tests pass, no prohibited
  files changed, diff clean. S2 acceptance and architecture writeback
  completed by controller.
---

# Phase 158 S2 Acceptance: Relationship State JSON Export

## Verification Results

| Gate | Expected | Actual |
|------|----------|--------|
| py_compile (4 files) | passes | passed |
| Novel runtime + README tests | passes | 277 passed in 11.34s |
| Full Tavern tests | passes | 1144 passed in 51.14s |
| Protected files diff | empty | empty |
| git diff --check | passes | clean |
| YAML validation (design.md) | passes | passed |
| YAML validation (checklist.yaml) | passes | passed |

## Files Changed

| File | Changes |
|------|---------|
| `src/hermes_tavern/runtime_novel.py` | +35 lines: relationship_export() function + export branch in relationship_command() + updated _RELATIONSHIP_USAGE |
| `src/hermes_tavern/commands.py` | +1 line: /rp relationship export <relationship-id> help |
| `README.md` | +1 line: relationship export in Core commands table |
| `tests/test_hermes_tavern_novel_runtime.py` | +120 lines: 7 focused relationship export tests + existing test updates |

## Implementation Summary

- `relationship_export()` resolves relationship state by integer ID via `runtime.store.get_relationship_state()`
- Writes UTF-8 JSON to `<hermes_home>/plugins/hermes-tavern/exports/relationships/relationship_<id>.json`
- Returns `file:` + quoted `MEDIA:"<path>"`
- Rejects not-found with "No relationship state found: <id>"
- Rejects non-positive/missing IDs with _RELATIONSHIP_USAGE
- No schema, prompt, provider, generation, credential, content-mode, or safety changes
- db_novel.py unchanged (get_relationship_state already exists)

## Architecture Writeback

Updated ARCHITECTURE.md:
- Added Phase 158 entry under command surface listing
- Updated phase summary header to "121–158 complete"
- Updated command surface header to "through Phase 158"
- Added Phase 158 relationship export boundary constraint
- Updated relationship command family to include `/rp relationship export <relationship-id>`
