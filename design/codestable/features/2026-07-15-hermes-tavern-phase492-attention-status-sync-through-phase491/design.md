---
doc_type: feature-design
feature: 2026-07-15-hermes-tavern-phase492-attention-status-sync-through-phase491
status: approved
implementation_ready: true
summary: Advance the mandatory attention/static status contract through accepted Phase 491.
tags: [hermes-tavern, codestable, attention, status-sync, docs, static-test, phase492]
---

# Phase 492 attention status sync through Phase 491

## Scope

Advance only the unique current-status line in `design/codestable/attention.md` and its focused static regression to `All phases 1-492 accepted`, preserving historical labels and appending the Phase 492 label once.

## Boundaries

No runtime, plugin, gateway, provider, prompt, credential, database, package, CI, README, or core-Hermes changes. `run_agent.py`, `cli.py`, and `gateway/run.py` remain untouched.

## Implementation

Update the exact attention status marker and the focused status test constants, labels, ranges, suffix, and stale guards as specified by the read-only Architect artifact.

## Verification

Validate the design/checklist, compile the focused test to `/tmp`, run focused Tavern and full suites, then run scope and whitespace guards.

## Acceptance

Acceptance remains parent-controller owned after independent verification.
