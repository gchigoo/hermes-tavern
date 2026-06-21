---
doc_type: feature-acceptance
status: accepted
feature: "2026-06-18-hermes-tavern-phase309-attention-status-sync-through-phase308"
date: "2026-06-21"
accepted_by: parent-controller
parent_verification_completed: true
summary: >
  Parent-controller verified Phase 309 attention/status sync through accepted
  Phase 308. All gates passed; no runtime/provider/plugin/asset behavior changed.
---

# Phase 309 Acceptance: Attention Status Sync Through Phase 308

## Interface / Schema Contract

No runtime interface or schema changed. This is a docs/test-only status-sync phase.

## Behavior / Scope

- `design/codestable/attention.md`: Current-status prefix advanced from `All phases 1-307 accepted` to `All phases 1-308 accepted`. Phase 308 label (`Phase 308 attention status sync through Phase 307`) appended exactly once. All prior labels preserved.
- `tests/test_hermes_tavern_codestable_status.py`: CURRENT_STATUS_PREFIX, STALE_STATUS_PREFIX, STALE_PHASE_MARKER, REQUIRED_PHASE_LABELS, FINAL_STATUS_SUFFIX, phase_range (`range(168, 309)`), aggregate_range, and split stale aggregate guards updated. Only one anchored CURRENT_STATUS_PREFIX assignment. No contiguous discovery calls.

## Export Placement

N/A — no exports changed.

## Reverse-Scope / No-Leak Boundaries

- No runtime/source/plugin/provider/gateway/CLI files touched.
- No README, architecture, root-design, roadmap, requirements, or compound docs changed.
- No dependencies, credentials, configuration, or service lifecycle behavior altered.
- Prior phase feature directories untouched.

## Architecture / Root-Design Writeback

Not required — this is a recurring status-sync phase that records Phase 308 acceptance in the CodeStable attention document. No new capability, command, or design element was introduced.

## Requirement / Roadmap Conclusion

Phase 309 gate: Phase 308 accepted at `design/codestable/features/2026-06-18-hermes-tavern-phase308-attention-status-sync-through-phase307/acceptance.md`. Gate satisfied — Phase 308 acceptance confirmed before this sync.

## Verification Evidence (Parent-Controller)

| Gate | Result |
|------|--------|
| YAML validation (design.md + checklist.yaml) | PASS — 2 files valid |
| py_compile (status test) | PASS |
| Focused status pytest (1 test) | PASS |
| Python static status/protected-path guard | PASS — prefix, suffix, labels, range, stale markers, assignment anchor, discovery tokens, and allowed/prohibited files all verified |
| Full pytest (1215 tests) | PASS |
| git diff --check + git diff --cached --check | PASS |

## Attention Candidates

None — this is a recurring maintenance sync.

## Residual Deferred Work

Phase 310 (sync through Phase 309) is the natural next recurring slice, gated on Phase 309 acceptance.
