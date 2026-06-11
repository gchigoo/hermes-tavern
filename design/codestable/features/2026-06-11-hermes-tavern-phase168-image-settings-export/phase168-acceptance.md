---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-11-hermes-tavern-phase168-image-settings-export"
date: "2026-06-11"
summary: "Phase 168 S1 implementation and S2 acceptance/writeback complete. Image settings JSON export is implemented, documented, and verified."
owner: codestable-cron
---

# Phase 168 Acceptance: Image Settings JSON Export

## S1 Implementation

Codex executor implemented the bounded `/rp image settings export` command in the previous slice. The accepted behavior is:

- Command surface: `/rp image settings [set <key> <value>|clear <key|all>|export]`.
- Runtime behavior: resolves the active session, reads active settings with `get_image_settings`, normalizes them with `normalize_image_settings`, and writes one UTF-8 JSON file under `get_hermes_home()/plugins/hermes-tavern/exports/settings`.
- Output contract: returns `Image settings exported.` plus a quoted `MEDIA:"<path>"` attachment marker.
- Visibility: command help and README Core commands expose `/rp image settings export`.
- Tests: focused image tests cover JSON file creation, normalized keys, quoted MEDIA output, no-active-session behavior, and preservation of existing inspect/set/clear behavior.

## S2 Acceptance (Controller)

### Gates

| Gate | Result |
|------|--------|
| `validate-yaml.py` on design/checklist/acceptance | PASS |
| `py_compile` on changed runtime/help/test files | PASS |
| Focused image + README + command tests | 130 passed |
| Full Tavern test suite | 1203 passed |
| Reverse-scope guard | PASS — only Phase 168 CodeStable docs, `ARCHITECTURE.md`, and `HERMES_TAVERN_DESIGN.md` changed |
| Stale status/wording guard | PASS — no pending/in_progress/draft markers remain in current Phase 168 docs |
| `git diff --check` | PASS |

### Controller-run commands

```bash
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase168-image-settings-export/design.md --require doc_type --require status --require feature
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase168-image-settings-export/phase168-acceptance.md --require doc_type --require status --require feature
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase168-image-settings-export/checklist.yaml --yaml-only --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile src/hermes_tavern/runtime_images.py src/hermes_tavern/commands.py tests/test_hermes_tavern_images.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_images.py tests/test_hermes_tavern_readme_docs.py tests/test_hermes_tavern_commands.py -q -o 'addopts=' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_*.py -q -o 'addopts=' -p no:cacheprovider
/opt/homebrew/bin/git diff --check
```

## Behavior Evidence

- JSON export behavior is covered by `tests/test_hermes_tavern_images.py`.
- README/command visibility is covered by `tests/test_hermes_tavern_readme_docs.py` and `tests/test_hermes_tavern_commands.py`.
- Existing image settings inspect/set/clear behavior remains covered by focused image tests.
- No source/runtime/test files changed during S2; S2 is documentation and status writeback only.

## Architecture and Root-Design Writeback

- `design/codestable/architecture/ARCHITECTURE.md` now records Phase 168 as current, includes the `/rp image settings ... export` command surface, and documents the Phase 168 image settings export boundary.
- `design/HERMES_TAVERN_DESIGN.md` §15.2 now includes the image settings command form and a current-behavior note for active-session image settings export.
- `design/codestable/features/2026-06-11-hermes-tavern-phase168-image-settings-export/design.md` frontmatter was normalized from the prior controller-materialized draft state to `status: approved` after controller verification.
- `checklist.yaml` S2 and C6–C12 are finalized with controller-run evidence.

## Scope Boundaries

Phase 168 remains local/offline and limited to active-session image settings export:

- no image settings schema migration;
- no provider/model routing changes;
- no image generation behavior changes;
- no prompt/debug/context-budget behavior changes;
- no retrieval/vectorization behavior;
- no content-mode/minors/underage/safety-bypass behavior;
- no plugin/core/gateway behavior changes.

## Requirement / Roadmap / Attention

- Requirement backfill: not required; this is a narrow command/export parity feature under existing media/export capabilities.
- Roadmap writeback: not applicable; no roadmap item is associated with this feature.
- `attention.md`: no new recurring setup/workflow note discovered.

## Residual Risk

No known residual implementation risk. Future work, if desired, should be separate CodeStable phases for other media export surfaces (for example image safety/style/model-profile export) rather than widening Phase 168.
