---
doc_type: feature-design
status: approved
implementation_ready: true
feature: "2026-06-18-hermes-tavern-phase301-attention-status-sync-through-phase300"
date: "2026-06-18"
created: "2026-06-18"
updated: "2026-06-18"
owner: company-boost
summary: >
  Sync the mandatory CodeStable attention current-status line and focused static
  regression through accepted Phase 300 only, without changing runtime behavior.
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests]
---

# Phase 301: CodeStable Attention Status Sync Through Phase 300

## Gate

Phase 300 is accepted: `design/codestable/features/2026-06-18-hermes-tavern-phase300-attention-status-sync-through-phase299/acceptance.md` has `status: accepted`.

Current state:
- `design/codestable/attention.md` reports `All phases 1-299 accepted`.
- `tests/test_hermes_tavern_codestable_status.py` enforces Phase 299 current state.
- No Phase 301 directory existed before this company-boost worker materialized the design/checklist.

## Goal

Advance the recurring status-sync lane by exactly one phase: sync `design/codestable/attention.md` and the focused static regression through accepted Phase 300 only.

## Scope

Allowed files:
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`
- `design/codestable/features/2026-06-18-hermes-tavern-phase301-attention-status-sync-through-phase300/design.md`
- `design/codestable/features/2026-06-18-hermes-tavern-phase301-attention-status-sync-through-phase300/checklist.yaml`
- Optional worker/parent handoff closeout only: `design/codestable/features/2026-06-18-hermes-tavern-phase301-attention-status-sync-through-phase300/acceptance.md`

## Non-Goals

Do not modify runtime/source/plugin/provider/gateway/CLI behavior, `run_agent.py`, `cli.py`, `gateway/run.py`, plugin runtime/source files, credentials, root design, README, architecture, roadmap, requirements, compound docs, build outputs, assets, fixtures, schemas, provider routing, service lifecycle, commits, staging, pushes, or progress state.

Preserve Hermes-native plugin architecture and SillyTavern asset compatibility. Preserve adult-fiction/RP compatibility while forbidding minors/CSAM work and provider safety bypasses.

## Exact Status Contract

Change the `attention.md` current-status prefix:
- From: `Current status (2026-06-18): All phases 1-299 accepted`
- To: `Current status (2026-06-18): All phases 1-300 accepted`

Append exactly one new label:
- `Phase 300 attention status sync through Phase 299`

Preserve:
- `Phase 121-167`
- Every existing explicit label from `Phase 168` through `Phase 299`

Do not add:
- `Phase 301 attention/status sync` label to `attention.md`

Final suffix must be exactly:

`Phase 298 attention status sync through Phase 297, Phase 299 attention status sync through Phase 298, and Phase 300 attention status sync through Phase 299.`

## Focused Test Contract

Update `tests/test_hermes_tavern_codestable_status.py`:
- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-300 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-299 accepted"`
- `STALE_PHASE_MARKER = "1-299"`
- `STALE_PHASE_MARKER_EN_DASH = "1–299"`
- Preserve all current `REQUIRED_PHASE_LABELS` through Phase 299 and append `Phase 300 attention status sync through Phase 299`.
- `FINAL_STATUS_SUFFIX` equals the Phase 298/299/300 suffix above.
- Runtime aggregate range becomes `range(168, 301)`.
- Source self-check aggregate literal becomes `aggregate_range = "range(168, 301)"`.
- Stale aggregate guards include split-string rejection for `range(168, 300)` and retain older split stale ranges.
- Keep anchored `CURRENT_STATUS_PREFIX` assignment guard.
- Keep discovery-token guards split for `.glob(`, `.rglob(`, `iterdir(`, and `os.walk`.

## Structure Health

No micro-refactor. This is a bounded docs/static-test sync only.

## Verification

Run:
- `PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-18-hermes-tavern-phase301-attention-status-sync-through-phase300 --require doc_type --require status --require feature`
- `PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py`
- `PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o 'addopts=' -p no:cacheprovider`
- Static status/protected-path guard
- `PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o 'addopts='` if feasible, without disabling plugin autoload
- `git diff --check`

## Architect Review Checklist

- Phase 300 acceptance remains the gate for this slice.
- The dirty tree is limited to the allowed Phase 301 artifact files, `design/codestable/attention.md`, and `tests/test_hermes_tavern_codestable_status.py`.
- The attention current-status line uses `All phases 1-300 accepted`, preserves every prior short label, appends Phase 300 once, and does not add a Phase 301 label.
- The focused status test uses anchored assignment counting, advances stale negatives and aggregate ranges, and keeps discovery-token literals split.
- Runtime/plugin/provider/gateway/source files and credentials are unchanged.
- Checklist/acceptance statuses remain parent-verification-aware; no commit, push, staging, service lifecycle command, or progress-state update is performed.
