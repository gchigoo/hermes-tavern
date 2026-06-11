---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-11-hermes-tavern-phase169-project-json-export-surface-parity"
date: "2026-06-11"
summary: "Phase 169 command-surface parity for project JSON export is implemented, documented, and verified."
owner: codestable-cron
---

# Phase 169 Acceptance: Project JSON Export Surface Parity

## Scope

Phase 169 is a docs/help-test parity slice for the already-implemented Phase 167
project JSON export command:

```text
/rp project export json [project-id]
```

It intentionally changes no runtime command handling, JSON payload generation,
export file layout, schema, provider/model routing, prompt compiler behavior,
generation, archive/ZIP behavior, retrieval/vectorization, credentials,
content mode, or safety/adult-fiction boundaries.

## Codex Two-Stage Evidence

- Architect pass: `/tmp/hermes-tavern-architect-phase169.jsonl`
  - Decision: `PROCEED_WITH_PHASE169`
  - Required artifact normalization: design/checklist set to approved and
    implementation-ready before executor.
- Executor pass: `/tmp/hermes-tavern-executor-phase169.jsonl`
  - Implemented S1 in the allowed docs/test files.
  - Reported targeted tests passing with 104 passed.
- Controller correction: moved the architecture command literal next to the
  project command-surface entry and added the same literal to the second root
  design writing-command block so both documented command surfaces are in sync.

## Implementation Summary

Changed files:

- `design/HERMES_TAVERN_DESIGN.md`
  - Added `/rp project export json [project-id]` in the project Commands block.
  - Added `/rp project export json [project-id]` in the writing-command surface.
- `design/codestable/architecture/ARCHITECTURE.md`
  - Added the project JSON export literal to the current `/rp` command surface.
  - Bumped architecture current markers from Phase 168 to Phase 169.
  - Added a Phase 169 capability summary noting that this is command-surface
    parity only.
- `tests/test_hermes_tavern_commands.py`
  - Added exact `_build_help_text()` assertion for the project JSON export
    command literal.
- `design/codestable/features/2026-06-11-hermes-tavern-phase169-project-json-export-surface-parity/design.md`
  - Normalized frontmatter to `status: approved` and
    `implementation_ready: true` from the architect artifact.
- `design/codestable/features/2026-06-11-hermes-tavern-phase169-project-json-export-surface-parity/checklist.yaml`
  - Marked S1/S2 and checks complete with controller-run evidence.

## Verification Summary

| Gate | Result |
|------|--------|
| Codex architect smoke + phase architect pass | PASS |
| Codex executor smoke + S1 executor pass | PASS |
| CodeStable YAML validators | PASS |
| `py_compile` on changed tests | PASS |
| Targeted command/readme tests | PASS — 104 passed |
| Exact command literal grep | PASS — source help, README, root design (two blocks), architecture, command/readme tests |
| Full pytest suite | PASS — 1203 passed |
| `git diff --check` | PASS |
| Reverse-scope guard | PASS — no runtime/source/export/schema/provider/prompt/generation/safety files changed |

## Controller-Run Commands

```bash
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase169-project-json-export-surface-parity/design.md --require doc_type --require status --require feature
python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-06-11-hermes-tavern-phase169-project-json-export-surface-parity/checklist.yaml --yaml-only --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py -q -o 'addopts=' -p no:cacheprovider
rg -n "/rp project export json \\[project-id\\]" README.md src/hermes_tavern/commands.py design/HERMES_TAVERN_DESIGN.md design/codestable/architecture/ARCHITECTURE.md tests/test_hermes_tavern_commands.py tests/test_hermes_tavern_readme_docs.py
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider
git diff --check
```

## Acceptance Checks

- Interface/command contract: PASS — the exact command literal now appears in
  source help, README, both root-design command-surface blocks, architecture,
  and regression tests.
- Behavior/non-goals: PASS — no runtime or payload behavior changed; this slice
  is documentation and help-test parity only.
- Architecture writeback: PASS — architecture current markers now include Phase
  169 and document the parity-only boundary.
- Requirement writeback: not required; this is not a new user-facing runtime
  capability, only parity documentation for Phase 167.
- Roadmap writeback: not applicable; no roadmap item is associated with this
  feature.
- `attention.md`: no new recurring setup/workflow note discovered.

## Residual Risk / Next Step

No known residual implementation risk. A future safe slice can continue with
another bounded command-surface/doc parity or local metadata/export hardening
phase selected by the next architect pass.
