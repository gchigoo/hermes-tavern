---
doc_type: feature-design
feature: 2026-07-24-hermes-tavern-phase517-attention-status-sync-through-phase516
status: approved
implementation_ready: true
bounded_phase: docs/static-test/status-only
parent_verification_status: verified
acceptance_state: accepted
summary: Approved S1 design for Phase 517 attention status sync through accepted Phase 516.
tags: [codestable, status-sync, docs, static-test]
---

# Phase 517 Attention Status Sync

## Scope

Advance only the canonical attention current-status record and its focused static contract from Phase 516 to Phase 517; Phase 517 has no runtime or plugin behavior change.

## Exact Contract

- Set `Current status (2026-06-18): All phases 1-517 accepted`.
- Append `Phase 517 attention status sync through Phase 516` exactly once after Phase 516.
- Preserve history, ordering, date, the Phase 121-167 aggregate, and the adult-fiction boundary text at its current location.
- Require 350 ordered labels, `range(168, 518)`, stale guards for Phases 516/515/514/513, the exact Phase 513-517 suffix, and no Phase 518 label.

## Constraints

Only attention, the focused status test, and this feature's design/checklist may change. Do not modify Hermes core, plugin runtime, gateway, provider, auth, cron, Radar, README, architecture, root design, or Phase 516 artifacts.

## Lifecycle

This slice has no acceptance artifact. During executor work the checklist remains non-final. The parent controller finalizes the checklist only after independently rerunning every declared verification gate; no controller evidence is recorded before that independent verification.

## Verification

- `python3 design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-07-24-hermes-tavern-phase517-attention-status-sync-through-phase516`
- `python3 design/codestable/tools/validate-yaml.py --file design/codestable/features/2026-07-24-hermes-tavern-phase517-attention-status-sync-through-phase516/2026-07-24-hermes-tavern-phase517-attention-status-sync-through-phase516-checklist.yaml --yaml-only`
- `python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- `git diff --check`
