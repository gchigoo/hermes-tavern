---
doc_type: feature-design
feature: hermes-tavern-phase496-attention-status-sync-through-phase495
status: approved
created: 2026-07-15
tags: [codestable, attention, status-sync]
implementation_ready: true
---

# Phase 496 attention status sync through Phase 495

## Goal

Synchronize the live CodeStable attention status and its focused static regression through already accepted Phase 495. This is docs/test-only; it creates no runtime, command, schema, provider, or plugin behavior.

## Scope

S1 may modify only `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`. The terminal marker becomes `All phases 1-496 accepted` and retains all existing accepted labels while appending `Phase 496 attention status sync through Phase 495` exactly once.

## Boundaries

Do not modify earlier phase artifacts, core Hermes files, runtime/plugin source, command/help docs, root design, architecture, dependencies, CI, provider safety, credentials, auth, gateway, cron, account, or Radar behavior.

## Verification

Run focused status tests, the complete pytest suite, exact scope checks, artifact YAML validation, and whitespace checks.
