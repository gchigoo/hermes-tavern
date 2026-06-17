---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-17-hermes-tavern-phase285-attention-status-sync-through-phase284"
date: "2026-06-17"
created: "2026-06-17"
updated: "2026-06-17"
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 284 only, without changing runtime/source
  behavior, Hermes-native plugin architecture, provider safety behavior, gateway
  behavior, provider settings, credentials, root design, or SillyTavern assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 285: CodeStable Attention Status Sync Through Phase 284

## Exact S1 Contract

- `design/codestable/attention.md` current status starts with
  `Current status (2026-06-17): All phases 1-284 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` updates:
  - `CURRENT_STATUS_PREFIX = "Current status (2026-06-17): All phases 1-284 accepted"`
  - `STALE_STATUS_PREFIX = "Current status (2026-06-16): All phases 1-283 accepted"`
  - `STALE_PHASE_MARKER = "1-283"`
  - `STALE_PHASE_MARKER_EN_DASH = "1–283"`
- Preserve valid internal range `Phase 121-167`.
- Preserve all prior short labels already present in the current-status line.
- Append exactly `Phase 284 attention status sync through Phase 283`.
- Do not append a Phase 285 short label to `attention.md`; this slice syncs through accepted Phase 284 only.
- The current-status bullet ends with:
  `Phase 282 attention status sync through Phase 281, Phase 283 attention status sync through Phase 282, and Phase 284 attention status sync through Phase 283.`
- Reject stale terminal accepted markers/prefixes for `1-283` and `1–283`.
- `phase_range = range(168, 285)` in focused regression.
- Reject stale `range(168, 284)` plus older terminal ranges `range(168, 283)`, `range(168, 282)`, and `range(168, 281)` via split-string construction.
- Exactly one `CURRENT_STATUS_PREFIX` assignment remains in the focused test.
- The focused test source contains no discovery tokens: `.glob(`, `.rglob(`, `iterdir(`, or `os.walk`.

## Scope

Allowed files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-17-hermes-tavern-phase285-attention-status-sync-through-phase284/design.md`
- `design/codestable/features/2026-06-17-hermes-tavern-phase285-attention-status-sync-through-phase284/checklist.yaml`
- `design/codestable/features/2026-06-17-hermes-tavern-phase285-attention-status-sync-through-phase284/acceptance.md` only for controller-owned closeout

## Prohibited Files / Actions

- No runtime, source, provider, plugin, gateway, root-design, schema, credential, prompt, import/export behavior, or SillyTavern asset edits.
- Do not modify `plugins/`, provider code/config, `gateway/run.py`, `cli.py`, `run_agent.py`, `HERMES_TAVERN_DESIGN.md`, runtime DB paths, fixtures/assets, or service configuration.
- Preserve Hermes-native plugin architecture and SillyTavern asset compatibility.
- Preserve adult-fiction/RP-compatible boundaries; do not add or alter anything involving minors, CSAM, safety bypasses, provider-safety bypasses, or content policy weakening.
- Do not run service lifecycle commands, start/stop/restart gateway services, launch servers, or perform broad rewrites.
- Do not commit or push from executor.

## Acceptance Criteria

- Attention status advances only from accepted Phase 283 to accepted Phase 284.
- Focused status regression passes and enforces all literals in the Exact S1 Contract.
- Current-status line keeps `Phase 121-167`, all prior short labels, and the exact terminal suffix.
- Stale prefixes, stale markers, stale range endpoints, duplicate prefix assignments, and discovery tokens are rejected.
- Only allowed files changed; no runtime/source/provider/plugin/gateway/root-design/service/assets behavior changed.
