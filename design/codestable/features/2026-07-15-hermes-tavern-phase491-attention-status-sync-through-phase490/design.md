---
doc_type: feature-design
feature: 2026-07-15-hermes-tavern-phase491-attention-status-sync-through-phase490
status: approved
implementation_ready: true
summary: Advance mandatory attention status through accepted Phase 490 with a focused static regression.
tags: [hermes-tavern, codestable, attention, status-sync, docs, static-test, phase491]
---

# Phase 491 attention status sync through Phase 490

## Scope

Advance only the unique current-status line in `design/codestable/attention.md` and its focused static regression. Status becomes `All phases 1-491 accepted`, preserving ordered labels and appending the Phase 491 sync label exactly once.

## Boundaries

No runtime, plugin, gateway, provider, prompt, credential, database, README, CI, package, or script changes. `run_agent.py`, `cli.py`, and `gateway/run.py` remain untouched. Acceptance is parent-owned.

## Verification

Run the CodeStable validators, compile the focused test to `/tmp`, focused pytest, full pytest, exact-scope/static guards, and `git diff --check` before parent acceptance.
