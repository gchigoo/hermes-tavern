---
doc_type: feature-design
status: approved
feature: "2026-06-14-hermes-tavern-phase221-attention-status-sync-through-phase220"
date: "2026-06-14"
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 220, without changing runtime/source behavior
  or protected product documentation.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
created: "2026-06-14"
updated: "2026-06-14"
owner: codestable-cron
implementation_ready: true
---

# Phase 221: CodeStable Attention Status Sync Through Phase 220

## Read-Only Precheck

Phase 220 is accepted: checklist `status: accepted`, `workflow_status: completed`, and `phase220-acceptance.md` has `status: accepted`.

`design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py` still stop at `Current status (2026-06-13): All phases 1-219 accepted`. The next bounded gap is therefore metadata-only startup status sync through Phase 220.

## Scope

Docs/test/status-only. Executor S1 may edit only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Controller S2 may edit only:

- `design/codestable/features/2026-06-14-hermes-tavern-phase221-attention-status-sync-through-phase220/design.md`
- `design/codestable/features/2026-06-14-hermes-tavern-phase221-attention-status-sync-through-phase220/checklist.yaml`
- `design/codestable/features/2026-06-14-hermes-tavern-phase221-attention-status-sync-through-phase220/phase221-acceptance.md`

Update the single attention current-status bullet so it starts with:

`Current status (2026-06-14): All phases 1-220 accepted`

Append only:

`Phase 220 attention status sync through Phase 219`

The final suffix must be:

`Phase 218 attention status sync through Phase 217, Phase 219 attention status sync through Phase 218, and Phase 220 attention status sync through Phase 219.`

Update the focused static regression so:

- `CURRENT_STATUS_PREFIX` is `Current status (2026-06-14): All phases 1-220 accepted`
- `STALE_STATUS_PREFIX` is `Current status (2026-06-13): All phases 1-219 accepted`
- stale standalone markers `1-219` and `1–219` are rejected
- valid internal `Phase 121-167` remains allowed
- `REQUIRED_PHASE_LABELS` includes Phase 168 through Phase 220
- aggregate assertion is `range(168, 221)`
- no glob/rglob/iterdir/os.walk/generated discovery is introduced

## Non-Goals

Do not change runtime, source, plugin, provider/model routing, prompt/generation, import/export, schema, root-design, architecture, reference, README, roadmap, requirement, compound, build, Hermes core, adult-fiction/RP compatibility, minors/underage handling, provider safety, SillyTavern asset compatibility, or Hermes-native plugin architecture.

S1 must not mark final accepted statuses and must not create `phase221-acceptance.md`. S2 is controller-only acceptance closeout.

## Verification

Run focused syntax/static checks for `tests/test_hermes_tavern_codestable_status.py`, the focused pytest test, artifact YAML validation, changed-path allowlist guard, protected-path guard, and `git diff --check`.
