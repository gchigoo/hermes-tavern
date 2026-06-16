---
doc_type: feature-design
status: approved
feature: "2026-06-16-hermes-tavern-phase276-attention-status-sync-through-phase275"
date: "2026-06-16"
created: "2026-06-16"
updated: "2026-06-16"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 275, without changing runtime/source behavior,
  Hermes-native plugin architecture, provider safety behavior, adult-fiction/RP
  compatibility, or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 276: CodeStable Attention Status Sync Through Phase 275

## Read-Only Architect Precheck

- Architect JSONL: `/tmp/company-boost-hermes-tavern-architect-phase276.jsonl`.
- `design/codestable/attention.md` currently reports `Current status (2026-06-16): All phases 1-274 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards labels through Phase 274, stale terminal `1-273` markers, final suffix through Phase 274, and `range(168, 275)`.
- Phase 275 is accepted as a docs/test/status-only sync through Phase 274 (`status: accepted`, `workflow_status: completed`, with `acceptance.md`).
- No Phase 276 feature directory existed before this artifact.
- This slice is exactly one bounded docs/test/status-only sync and does not require service lifecycle commands.

## Scope

S1 may change only these no-commit lane files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-16-hermes-tavern-phase276-attention-status-sync-through-phase275/design.md`
- `design/codestable/features/2026-06-16-hermes-tavern-phase276-attention-status-sync-through-phase275/checklist.yaml`

S1 must not create or edit `acceptance.md`, must not perform final S2 closeout, and must not commit or push. Parent/controller verification owns final S1 status writeback and any later S2 closeout.

## Exact S1 Contract

- Current prefix becomes: `Current status (2026-06-16): All phases 1-275 accepted`
- Reject stale prefix: `Current status (2026-06-16): All phases 1-274 accepted`
- Reject stale standalone markers: `1-274` and `1–274`
- Preserve valid internal marker: `Phase 121-167`
- Preserve all existing Phase 168-274 short labels.
- Append new terminal label exactly: `Phase 275 attention status sync through Phase 274`
- Final suffix exactly: `Phase 273 attention status sync through Phase 272, Phase 274 attention status sync through Phase 273, and Phase 275 attention status sync through Phase 274.`
- Do not add Phase 276 to the attention status line.

## Test Contract

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-16): All phases 1-275 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-16): All phases 1-274 accepted"`
- `STALE_PHASE_MARKER = "1-274"`
- `STALE_PHASE_MARKER_EN_DASH = "1–274"`
- `REQUIRED_PHASE_LABELS` includes all existing labels and `Phase 275 attention status sync through Phase 274`.
- `FINAL_STATUS_SUFFIX` is the exact suffix above.
- `phase_range` uses `range(168, 276)`.
- Source assertion requires literal `range(168, 276)` and rejects stale `range(168, 275)` via split-string construction.
- Exactly one `CURRENT_STATUS_PREFIX` assignment.
- No `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` discovery tokens.

## Non-Goals

No runtime/source/provider/plugin behavior changes. Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, provider routing, prompt behavior, import/export behavior, schema behavior, SillyTavern assets, Hermes-native plugin architecture, provider safety behavior, adult-fiction/RP compatibility, or minors/underage handling.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-16-hermes-tavern-phase276-attention-status-sync-through-phase275 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- Static marker guard over `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`
- `git diff --check`

## Acceptance Contract

S1 is ready for parent/controller S1 status writeback when the single current-status bullet reports all phases `1-275` accepted, preserves `Phase 121-167` and all Phase 168-274 labels, appends exactly the Phase 275 label, ends with the exact suffix through Phase 275, rejects stale `1-274` / `1–274`, and the focused static regression remains explicit and passes. S1 must leave `acceptance.md` and final S2 closeout to a later parent/controller closeout slice.
