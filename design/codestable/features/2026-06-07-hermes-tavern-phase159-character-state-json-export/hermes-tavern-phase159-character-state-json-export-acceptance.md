---
doc_type: feature-acceptance
feature: "2026-06-07-hermes-tavern-phase159-character-state-json-export"
status: accepted
date: "2026-06-07"
summary: >
  Phase 159 S1 implemented via Codex executor (gpt-5.3-codex-spark).
  Controller verified all gates: 1152 full tests pass, no prohibited
  files changed, diff clean. S2 acceptance and architecture writeback
  completed by controller.
---

# Phase 159 S2 Acceptance: Character State JSON Export

## Verification Results

| Gate | Expected | Actual |
|------|----------|--------|
| py_compile (4 files) | passes | passed |
| Novel runtime + README tests | passes | 285 passed in 12.82s |
| Full Tavern tests | passes | 1152 passed in 52.68s |
| Protected files diff | empty | empty |
| git diff --check | passes | clean |
| YAML validation (design.md) | passes | passed |
| YAML validation (checklist.yaml) | passes | passed |

## Files Changed

| File | Changes |
|------|---------|
| `src/hermes_tavern/runtime_novel.py` | +35 lines: character_state_export() function + export branch in character_command() + updated _CHARACTER_USAGE |
| `src/hermes_tavern/commands.py` | +1 line: /rp character state export <character-state-id> help |
| `README.md` | +1 line: character state export in Core commands table |
| `tests/test_hermes_tavern_novel_runtime.py` | +156 lines: focused character-state export tests |

## Implementation Summary

- `character_state_export()` resolves character state by integer ID via `runtime.store.get_character_state()`
- Writes UTF-8 JSON to `<hermes_home>/plugins/hermes-tavern/exports/character-states/character_state_<id>.json`
- Returns `file:` + quoted `MEDIA:"<path>"`
- Rejects not-found with "No character state found: <id>"
- Rejects non-positive/missing IDs with _CHARACTER_USAGE
- No schema, prompt, provider, generation, credential, content-mode, or safety changes
- db_novel.py unchanged (get_character_state already exists)

## Architecture Writeback

Updated ARCHITECTURE.md:
- Added Phase 159 entry under command surface listing
- Updated phase summary header to "121–159 complete"
- Updated command surface header to "through Phase 159"
- Added Phase 159 character-state export boundary constraint
- Updated character command family to include `/rp character state export <character-state-id>`
