---
doc_type: feature-design
feature: 2026-07-14-hermes-tavern-phase490-attention-status-sync-through-phase489
status: approved
implementation_ready: true
summary: Advance mandatory attention status through accepted Phase 489 with a focused static regression.
tags: [hermes-tavern, codestable, attention, status-sync, docs, static-test, phase490]
---

# Phase 490 attention status sync through Phase 489

## Scope

Advance only the unique current-status line in `design/codestable/attention.md` and the existing focused static regression. Status becomes `All phases 1-490 accepted`, preserving ordered existing labels and appending the Phase 490 sync label exactly once.

## Boundaries

No runtime, plugin, gateway, provider, prompt, credential, database, README, CI, package, or script changes. `run_agent.py`, `cli.py`, and `gateway/run.py` remain untouched. Acceptance is parent-owned.

## Verification

Run the CodeStable validator, compile the focused test to `/tmp`, focused pytest, full pytest, exact-scope/static guards, and `git diff --check` before parent acceptance. Rollback is a revert of this feature directory plus the two allowed status files.