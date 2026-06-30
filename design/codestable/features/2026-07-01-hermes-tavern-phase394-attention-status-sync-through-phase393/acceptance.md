---
doc_type: feature-acceptance
feature: 2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393
status: accepted
accepted_at: "2026-07-01"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
summary: "Phase 394 attention/status sync through Phase 393 accepted after parent verification."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase394, standard-lane]
---

# Phase 394 attention/status sync acceptance

## Result

Accepted. Phase 394 advances the CodeStable startup attention status from all phases 1-393 accepted to all phases 1-394 accepted and appends `Phase 394 attention status sync through Phase 393` while preserving the historical Phase 121-167 aggregate and every explicit Phase 168 through Phase 393 label.

## Scope

This was a docs/static-test/status-only slice. Changed files are limited to:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/design.md`
- `design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/checklist.yaml`
- `design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/acceptance.md`

No runtime/source/plugin/provider/gateway/CLI/config/dependency/root-design/README/architecture/roadmap/requirements/compound/build/cache files changed. Hermes-native plugin architecture and SillyTavern asset compatibility remain unchanged. No provider-safety bypass, adult-minor/CSAM behavior, credentials, or service lifecycle work was introduced.

## Controller Verification

Parent/controller reran and passed:

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/design.md --require doc_type --require feature --require title --require status --require implementation_ready --require date --require owner --require lane --require bounded_phase --require tags`
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-01-hermes-tavern-phase394-attention-status-sync-through-phase393/checklist.yaml --yaml-only`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static Phase 394 status/scope/final-newline/trailing-whitespace guard over changed and untracked files
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts=' -p no:cacheprovider` (1215 passed)
- `git diff --check`

The read-only Architect review returned PASS for the S1 dirty tree at `/tmp/hermes-tavern-architect-review-phase394-20260701-0142.jsonl`. Parent created this acceptance artifact only after the controller gates passed.

## Status Contract

The accepted status line now starts with `Current status (2026-06-18): All phases 1-394 accepted`, includes `Phase 394 attention status sync through Phase 393` exactly once, and ends with `Phase 392 attention status sync through Phase 391, Phase 393 attention status sync through Phase 392, and Phase 394 attention status sync through Phase 393.`

The focused status regression now guards the Phase 394 contract, including the Phase 394 current prefix, Phase 393 stale markers, `range(168, 395)` live aggregate, split stale `range(168, 394)` guard, anchored assignment-count checks, section placement, and no-discovery-token protections.
