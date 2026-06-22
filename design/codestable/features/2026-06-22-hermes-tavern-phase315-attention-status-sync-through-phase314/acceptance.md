---
doc_type: feature-acceptance
status: draft
feature: "2026-06-22-hermes-tavern-phase315-attention-status-sync-through-phase314"
date: "2026-06-22"
owner: company-boost
parent_verification_completed: false
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase315]
summary: "Draft Phase 315 acceptance: attention status sync through Phase 314, pending parent verification."
---

# Phase 315 Acceptance Report (Draft)

## Gate

Phase 314 is accepted at `design/codestable/features/2026-06-22-hermes-tavern-phase314-attention-status-sync-through-phase313/acceptance.md`.

## Scope

Phase 315 syncs CodeStable attention current-status and focused static regression through accepted Phase 314 only.

### Changed Files

- `design/codestable/attention.md` — advance current-status from `All phases 1-314 accepted` to `All phases 1-315 accepted`; append `Phase 315 attention status sync through Phase 314` label exactly once; update suffix.
- `tests/test_hermes_tavern_codestable_status.py` — update `CURRENT_STATUS_PREFIX` to 1-315, `STALE_STATUS_PREFIX` to 1-314, stale markers to 1-314/1–314, append Phase 315 to `REQUIRED_PHASE_LABELS`, update `FINAL_STATUS_SUFFIX`, `phase_range` to `range(168, 316)`, `aggregate_range` to `"range(168, 316)"`, add split stale aggregate guard for `range(168, 315)`, and preserve existing guards for 314 through 281.
- `design/codestable/features/2026-06-22-hermes-tavern-phase315-attention-status-sync-through-phase314/` — new feature directory with `design.md`, `checklist.yaml`, and this draft `acceptance.md`.

### Unchanged

No runtime/source/plugin/provider/gateway/CLI files changed. No root design, README, architecture, roadmap, requirements, compound, build, asset, fixture, dependency, configuration, network, provider, model, or credential changes.

## Verification

Parent verification is still required. Worker-local verification commands for this draft handoff:

| Gate | Status |
|------|--------|
| YAML validation for Phase 315 feature directory | Pending parent verification |
| Focused pytest status test | Pending parent verification |
| Full pytest suite | Pending parent verification |
| Static stale-marker guard | Pending parent verification |
| `git diff --check` / `git diff --cached --check` | Pending parent verification |

## Residual

Acceptance remains `status: draft` with `parent_verification_completed: false` until the parent controller reruns verification and finalizes the phase. Do not commit or push from this worker handoff.