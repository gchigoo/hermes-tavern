---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase156-canon-json-export"
status: accepted
date: "2026-06-07"
summary: >
  Phase 156 S1 implemented via Codex executor (gpt-5.3-codex-spark).
  Controller verified all gates: 1129 full tests pass, no prohibited
  files changed, diff clean. S2 acceptance and architecture writeback
  completed by controller.
---

# Phase 156 S2 Acceptance: Canon JSON Export

## Verification Results

| Gate | Expected | Actual |
|------|----------|--------|
| py_compile (4 files) | passes | passed |
| Novel runtime + README tests | passes | 262 passed in 10.54s |
| Full Tavern tests | passes | 1129 passed in 49.28s |
| Protected files diff | empty | empty |
| git diff --check | passes | clean |
| YAML validation (design.md) | passes | passed |
| YAML validation (checklist.yaml) | passes | passed |

## Files Changed

| File | Changes |
|------|---------|
| `src/hermes_tavern/runtime_novel.py` | +37 lines: canon_export() function + export branch in canon_command() + updated _CANON_USAGE |
| `src/hermes_tavern/commands.py` | +1 line: /rp canon export <canon-id> help |
| `README.md` | +1 line: canon export in Core commands table |
| `tests/test_hermes_tavern_novel_runtime.py` | +125 lines: 7 focused canon export tests |
| `tests/test_hermes_tavern_readme_docs.py` | +1 line: README assertion |

## Implementation Summary

- `canon_export()` resolves canon by integer ID via `runtime.store.get_canon()`
- Writes UTF-8 JSON to `<hermes_home>/plugins/hermes-tavern/exports/canon/canon_<id>.json`
- Returns `file:` + quoted `MEDIA:"<path>"`
- Rejects not-found with "No canon fact found: <id>"
- Rejects non-positive/missing IDs with _CANON_USAGE
- No schema, prompt, provider, generation, credential, content-mode, or safety changes
- db_novel.py unchanged (get_canon already exists)

## Architecture Writeback

Updated ARCHITECTURE.md:
- Added Phase 156 entry under command surface listing
- Updated canon command family to include `/rp canon export <canon-id>`
