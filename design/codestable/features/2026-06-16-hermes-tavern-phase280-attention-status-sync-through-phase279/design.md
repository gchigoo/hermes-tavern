---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-16-hermes-tavern-phase280-attention-status-sync-through-phase279"
date: "2026-06-16"
created: "2026-06-16"
updated: "2026-06-16"
owner: codestable-cron
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 279, without changing runtime/source
  behavior, Hermes-native plugin architecture, provider safety behavior,
  adult-fiction/RP compatibility, or SillyTavern-compatible assets.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 280: CodeStable Attention Status Sync Through Phase 279

## Read-Only Architect Precheck

- Architect JSONL: `/tmp/company-boost-1781590524-hermes-tavern-architect.jsonl`.
- `design/codestable/attention.md` currently reports `Current status (2026-06-16): All phases 1-278 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` currently guards labels through Phase 278, stale terminal `1-277` markers, final suffix through Phase 278, and `range(168, 279)`.
- `design/codestable/features/2026-06-16-hermes-tavern-phase279-attention-status-sync-through-phase278` is accepted through Phase 278 and carries an accepted S2 closeout.
- This slice is exactly one bounded docs/test/status sync and does not require service lifecycle commands.

## Scope

S1 may change only these no-commit lane files:

- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-16-hermes-tavern-phase280-attention-status-sync-through-phase279/design.md`
- `design/codestable/features/2026-06-16-hermes-tavern-phase280-attention-status-sync-through-phase279/checklist.yaml`

S1 must not create or edit `acceptance.md`, must not perform final S2 closeout, and must not commit or push.
Parent/controller owns any later S2 closeout and final accepted status.

## Exact S1 Contract

- Current prefix becomes: `Current status (2026-06-16): All phases 1-279 accepted`.
- Reject stale prefix: `Current status (2026-06-16): All phases 1-278 accepted`.
- Reject stale standalone markers: `1-278` and `1–278`.
- Preserve valid internal marker: `Phase 121-167`.
- Preserve all existing Phase 168-278 short labels.
- Append new terminal label exactly: `Phase 279 attention status sync through Phase 278`.
- Final suffix exactly: `Phase 277 attention status sync through Phase 276, Phase 278 attention status sync through Phase 277, and Phase 279 attention status sync through Phase 278.`
- Do not add Phase 280 to the attention status line.

## Test Contract

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-16): All phases 1-279 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-16): All phases 1-278 accepted"`
- `STALE_PHASE_MARKER = "1-278"`
- `STALE_PHASE_MARKER_EN_DASH = "1–278"`
- `REQUIRED_PHASE_LABELS` includes all existing labels and `Phase 279 attention status sync through Phase 278`.
- `FINAL_STATUS_SUFFIX` is the exact suffix above.
- `phase_range` uses `range(168, 280)`.
- Source assertion requires literal `range(168, 280)` and rejects stale direct `range(168, 278)` / `range(168, 279)` via split-string construction.
- Exactly one `CURRENT_STATUS_PREFIX` assignment.
- No `.glob(`, `.rglob(`, `iterdir(`, or `os.walk` discovery tokens.

## Non-Goals

No runtime/source/provider/plugin behavior changes. Do not modify `run_agent.py`, `cli.py`, `gateway/run.py`, provider routing, prompt behavior, import/export behavior, schema behavior, SillyTavern assets, Hermes-native plugin architecture, provider safety behavior, adult-fiction/RP compatibility, minors/underage handling, credentials, or provider safety behavior.

## Verification Commands

- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-16-hermes-tavern-phase280-attention-status-sync-through-phase279 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider -s`
- Static marker guard over `design/codestable/attention.md` and `tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q`
- `git diff --check`
- `git status --short`

## Acceptance Contract

S1 is ready for parent/controller S2 closeout when the single current-status bullet reports all phases `1-279` accepted, preserves `Phase 121-167` and all Phase 168-278 labels, appends exactly the Phase 279 label, ends with the exact suffix through Phase 279, rejects stale `1-278` / `1–278`, and the focused static regression remains explicit and passes.
