---
doc_type: feature-design
feature: 2026-07-17-hermes-tavern-phase509-attention-status-sync-through-phase508
status: approved
implementation_ready: true
bounded_phase: docs/static-test/status-only
summary: Approved S1 design for Phase 509 attention status sync through accepted Phase 508.
tags: [codestable, status-sync, docs, static-test]
---

# Phase 509 Attention Status Sync

## Scope
Advance only the canonical attention current-status record and its focused static contract from Phase 508 to Phase 509; Phase 509 has no runtime or plugin behavior change.

## Exact Contract

- Set `Current status (2026-06-18): All phases 1-509 accepted`.
- Append `Phase 509 attention status sync through Phase 508` exactly once after Phase 508.
- Preserve history, ordering, date, and the Phase 121-167 aggregate.
- Require 342 ordered labels, `range(168, 510)`, rotated stale guards for Phases 508/507/506/505, a dynamic stale aggregate guard, and the exact Phase 505-509 suffix.

## Constraints
Only attention, the focused status test, and this feature's design/checklist may change in S1. Do not modify Hermes core, plugin runtime, gateway, provider, auth, cron, Radar, README, architecture, or root design.

## Lifecycle

This is S1 only. Keep the checklist non-final and do not create an acceptance artifact before parent verification.

## Verification
Validate artifacts, compile the status test, run focused and full pytest, then verify exact lifecycle scope and whitespace before acceptance closeout.
