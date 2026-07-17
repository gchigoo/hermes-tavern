---
doc_type: feature-design
feature: 2026-07-17-hermes-tavern-phase510-attention-status-sync-through-phase509
status: approved
implementation_ready: true
bounded_phase: docs/static-test/status-only
parent_verification_status: pending_parent_verification
acceptance_state: pending_parent_verification
summary: Approved S1 design for Phase 510 attention status sync through accepted Phase 509.
tags: [codestable, status-sync, docs, static-test]
---

# Phase 510 Attention Status Sync

## Scope
Advance only the canonical attention current-status record and its focused static contract from Phase 509 to Phase 510; Phase 510 has no runtime or plugin behavior change.

## Exact Contract

- Set `Current status (2026-06-18): All phases 1-509 accepted`.
- Append `Phase 510 attention status sync through Phase 509` exactly once after Phase 509.
- Preserve history, ordering, date, and the Phase 121-167 aggregate.
- Require 343 ordered labels, `range(168, 511)`, rotated stale guards for Phases 509/508/507/506, a dynamic stale aggregate guard, and the exact Phase 506-510 suffix.

## Constraints
Only attention, the focused status test, and this feature's design/checklist may change in S1. Do not modify Hermes core, plugin runtime, gateway, provider, auth, cron, Radar, README, architecture, or root design.

## Lifecycle

This is S1 only. Keep the checklist non-final and do not create an acceptance artifact before parent verification.

## Verification
The executor runs the focused static status test. Parent verification remains responsible for any additional validation and acceptance closeout.
