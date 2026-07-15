---
doc_type: feature-design
feature: 2026-07-15-hermes-tavern-phase494-attention-status-sync-through-phase493
status: approved
implementation_ready: true
summary: Advance the mandatory attention/static status contract through accepted Phase 493.
tags: [hermes-tavern, codestable, attention, status-sync, docs, static-test, phase494]
---

# Phase 494 attention status sync through Phase 493

## Scope

Advance only the unique current-status line in `design/codestable/attention.md` and its focused static regression to `All phases 1-494 accepted`, preserving historical labels and appending the Phase 494 label once.

## Boundaries

No runtime, plugin, gateway, provider, prompt, credential, database, package, CI, README, or core-Hermes changes. `run_agent.py`, `cli.py`, and `gateway/run.py` remain untouched.

## Implementation

Update the exact attention status marker and focused status-test constants, labels, ranges, suffix, and stale guards. The executor must not modify this design or the checklist, create acceptance evidence, or set final lifecycle statuses.

## Verification

Validate the artifacts, compile the focused test to `/tmp`, run focused Tavern and full suites, then run strict scope and whitespace guards.

## Acceptance

Acceptance remains parent-controller owned after independent verification.
