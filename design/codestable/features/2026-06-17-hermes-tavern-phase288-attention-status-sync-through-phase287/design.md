---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-17-hermes-tavern-phase288-attention-status-sync-through-phase287"
date: "2026-06-17"
created: "2026-06-17"
updated: "2026-06-17"
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 287 only, without changing runtime/source
  behavior, Hermes-native plugin architecture, provider safety behavior, gateway
  behavior, provider settings, credentials, root design, README, architecture,
  roadmap, requirements, compound docs, build output, or SillyTavern assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 288: CodeStable Attention Status Sync Through Phase 287

## Exact S1 Contract

- `design/codestable/attention.md` current status starts with
  `Current status (2026-06-17): All phases 1-287 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` updates:
  - `CURRENT_STATUS_PREFIX = "Current status (2026-06-17): All phases 1-287 accepted"`
  - `STALE_STATUS_PREFIX = "Current status (2026-06-17): All phases 1-286 accepted"`
  - `STALE_PHASE_MARKER = "1-286"`
  - `STALE_PHASE_MARKER_EN_DASH = "1–286"`
- Preserve valid internal range `Phase 121-167`.
- Preserve all prior short labels already present in the current-status line.
- Append exactly `Phase 287 attention status sync through Phase 286`.
- Do not append a Phase 288 short label to `attention.md`; this slice syncs through accepted Phase 287 only.
- The current-status bullet ends with:
  `Phase 285 attention status sync through Phase 284, Phase 286 attention status sync through Phase 285, and Phase 287 attention status sync through Phase 286.`
- Reject stale terminal accepted markers/prefixes for `1-286` and `1–286`.
- `phase_range = range(168, 288)` in focused regression.
- Reject stale `range(168, 287)` plus older terminal ranges `range(168, 286)`, `range(168, 285)`, `range(168, 284)`, `range(168, 283)`, `range(168, 282)`, and `range(168, 281)` via split-string construction.
- Exactly one `CURRENT_STATUS_PREFIX` assignment remains in the focused test.
- The focused test source contains no discovery tokens: `.glob(`, `.rglob(`, `iterdir(`, or `os.walk`.

## Scope

Allowed files only:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-17-hermes-tavern-phase288-attention-status-sync-through-phase287/design.md`
- `design/codestable/features/2026-06-17-hermes-tavern-phase288-attention-status-sync-through-phase287/checklist.yaml`
- `design/codestable/features/2026-06-17-hermes-tavern-phase288-attention-status-sync-through-phase287/acceptance.md`

## Prohibited Files / Actions

No runtime/source/plugin/provider/gateway/root-design/README/architecture/roadmap/requirements/compound/build edits. Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, `plugins/`, provider code/config, `HERMES_TAVERN_DESIGN.md`, `design/HERMES_TAVERN_DESIGN.md`, assets, schemas, credentials, prompts, service configuration, or Tavern behavior. No service lifecycle commands. No commit/push. No Phase 289.

## Acceptance Criteria

- Attention status advances only from accepted Phase 286 to accepted Phase 287.
- Focused regression enforces all Phase 288 contract literals.
- `Phase 121-167` remains valid and untouched.
- All Phase 168-287 labels are present; no Phase 288 label is added.
- Final suffix is exactly `Phase 285 attention status sync through Phase 284, Phase 286 attention status sync through Phase 285, and Phase 287 attention status sync through Phase 286.`
- Stale prefixes, stale markers, stale range endpoints, duplicate prefix assignments, and discovery tokens are rejected.
- Only allowed files change.
- No runtime/source/plugin/provider/gateway/root-design/README/architecture/roadmap/requirements/compound/build/service/assets behavior changes.
- Parent verification is required.

## Verification Commands

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-17-hermes-tavern-phase288-attention-status-sync-through-phase287 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='
git diff --check
```

## Required Phase Labels

The focused regression must preserve every existing label from Phase 168 through Phase 286 and add exactly:

- `Phase 287 attention status sync through Phase 286`

It must also keep the focused assertion for valid internal range `Phase 121-167`.
