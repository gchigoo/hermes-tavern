---
doc_type: feature-design
status: approved
feature: "2026-06-16-hermes-tavern-phase278-attention-status-sync-through-phase277"
date: "2026-06-16"
created: "2026-06-16"
updated: "2026-06-16"
implementation_ready: true
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 277, without changing runtime/source behavior,
  Hermes-native plugin architecture, provider safety behavior, adult-fiction/RP
  compatibility, or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 278: CodeStable Attention Status Sync Through Phase 277

## Read-Only Architect Precheck

- Architect JSONL: `/tmp/hermes-tavern-architect-phase278.jsonl`.
- `design/codestable/attention.md` currently reports `Current status (2026-06-16): All phases 1-276 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards labels through Phase 276, stale terminal `1-275` markers, final suffix through Phase 276, and `range(168, 277)`.
- Phase 277 is accepted as a docs/test/status-only sync through Phase 276 (`status: accepted`, `workflow_status: completed`, with `acceptance.md`).
- No Phase 278 feature directory existed at architect read time.
- This slice is exactly one bounded docs/test/status-only sync and does not require service lifecycle commands.

## Scope

S1 may change only these no-commit lane files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-16-hermes-tavern-phase278-attention-status-sync-through-phase277/design.md`
- `design/codestable/features/2026-06-16-hermes-tavern-phase278-attention-status-sync-through-phase277/checklist.yaml`

S1 must not create or edit `acceptance.md`, must not perform final S2 closeout, and must not commit or push. Parent/controller owns any later S2 closeout and final accepted status.

## Exact S1 Contract

- Current prefix becomes: `Current status (2026-06-16): All phases 1-277 accepted`
- Reject stale prefix: `Current status (2026-06-16): All phases 1-276 accepted`
- Reject stale standalone markers: `1-276` and `1–276`
- Preserve valid internal marker: `Phase 121-167`
- Preserve all existing Phase 168-276 short labels.
- Append new terminal label exactly: `Phase 277 attention status sync through Phase 276`
- Final suffix exactly: `Phase 275 attention status sync through Phase 274, Phase 276 attention status sync through Phase 275, and Phase 277 attention status sync through Phase 276.`
- Do not add Phase 278 to the attention status line.

## Test Contract

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-16): All phases 1-277 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-16): All phases 1-276 accepted"`
- `STALE_PHASE_MARKER = "1-276"`
- `STALE_PHASE_MARKER_EN_DASH = "1–276"`
- `REQUIRED_PHASE_LABELS` includes all existing labels and `Phase 277 attention status sync through Phase 276`.
- `FINAL_STATUS_SUFFIX` is the exact suffix above.
- `phase_range` uses `range(168, 278)`.
- Source assertion requires literal `range(168, 278)` and rejects stale direct `range(168, 277)` via split-string construction.
- Exactly one `CURRENT_STATUS_PREFIX` assignment.
- No `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` discovery tokens.

## Non-Goals

No runtime/source/provider/plugin behavior changes. Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, provider routing, prompt behavior, import/export behavior, schema behavior, SillyTavern assets, Hermes-native plugin architecture, provider safety behavior, adult-fiction/RP compatibility, or minors/underage handling.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-16-hermes-tavern-phase278-attention-status-sync-through-phase277 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- Static marker guard over `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`
- `git diff --check`

## Acceptance Contract

S1 is ready for parent/controller S2 closeout when the single current-status bullet reports all phases `1-277` accepted, preserves `Phase 121-167` and all Phase 168-276 labels, appends exactly the Phase 277 label, ends with the exact suffix through Phase 277, rejects stale `1-276` / `1–276`, and the focused static regression remains explicit and passes. S1 must leave `acceptance.md` and final accepted status to a later parent/controller closeout slice.
