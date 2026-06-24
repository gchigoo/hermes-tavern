---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase346-attention-status-sync-through-phase345
status: approved
implementation_ready: true
date: "2026-06-24"
owner: company_boost_lane
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready Phase 346 attention/status sync through accepted Phase 345."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase346]
---

# Phase 346: Attention Status Sync Through Phase 345

## Background / Current Status

Phase 345 is the latest accepted phase. Its acceptance report exists at `design/codestable/features/2026-06-24-hermes-tavern-phase345-attention-status-sync-through-phase344/acceptance.md` with `status: accepted`, and the current live CodeStable startup/status contract is synced through Phase 345:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-345 accepted`.
- The current terminal label is `Phase 345 attention status sync through Phase 344`.
- `tests/test_hermes_tavern_codestable_status.py` uses `CURRENT_STATUS_PREFIX` for `1-345`, `phase_range = range(168, 346)`, and `aggregate_range = "range(168, 346)"`.
- No Phase 346 feature directory existed before this slice was selected.

The read-only architect pass selected a non-final S1 status-sync handoff for Phase 346 rather than an S2 closeout.

## Goals

- Create the Phase 346 feature design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-345 to 1-346.
- Add terminal label `Phase 346 attention status sync through Phase 345`.
- Update `tests/test_hermes_tavern_codestable_status.py` so the static regression guards the Phase 346 live status contract.
- Preserve all historical labels exactly as literal text from the current files, including `Phase 121-167` and every explicit Phase 168 through Phase 345 label.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, dependency, config, root README, root design, architecture, roadmap, requirements, or compound changes.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No adult-fiction/RP behavior changes.
- No minors-related work and no provider safety bypass.
- No service lifecycle commands.
- No dependency installation.
- No commits, staging, or pushes.
- Do not create or finalize `acceptance.md` in this S1 slice.
- Do not create Phase 347.

## Exact Allowed Files

Executor S1 may touch exactly these files:

- `design/codestable/features/2026-06-24-hermes-tavern-phase346-attention-status-sync-through-phase345/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase346-attention-status-sync-through-phase345/checklist.yaml`
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

## Prohibited Files / Areas

All files not listed above are prohibited for executor S1, including:

- `plugins/`
- `hermes/`
- runtime/source/provider/gateway/CLI/config/dependency files
- root docs and root design docs
- `design/codestable/architecture/`
- `design/codestable/roadmap/`
- `design/codestable/requirements/`
- `design/codestable/compound/`
- generated cache, build, or service lifecycle artifacts

## Exact Status Line Change

Update the single current status line in `design/codestable/attention.md` line 47:

- from prefix `Current status (2026-06-18): All phases 1-345 accepted`
- to prefix `Current status (2026-06-18): All phases 1-346 accepted`

Preserve all existing labels exactly, append `Phase 346 attention status sync through Phase 345` exactly once, and replace the terminal suffix:

- from `Phase 343 attention status sync through Phase 342, Phase 344 attention status sync through Phase 343, and Phase 345 attention status sync through Phase 344.`
- to `Phase 344 attention status sync through Phase 343, Phase 345 attention status sync through Phase 344, and Phase 346 attention status sync through Phase 345.`

## Test Contract Changes

Update `tests/test_hermes_tavern_codestable_status.py`:

- `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-346 accepted"`
- `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-345 accepted"`
- `STALE_PHASE_MARKER = "1-345"`
- `STALE_PHASE_MARKER_EN_DASH = "1–345"`
- Add `"Phase 346 attention status sync through Phase 345"` to `REQUIRED_PHASE_LABELS` exactly once, after Phase 345.
- `FINAL_STATUS_SUFFIX = "Phase 344 attention status sync through Phase 343, Phase 345 attention status sync through Phase 344, and Phase 346 attention status sync through Phase 345."`
- `phase_range = range(168, 347)`
- `aggregate_range = "range(168, 347)"`
- Add split stale aggregate guard for `range(168, 346)` without leaving that contiguous stale literal in source:
  `stale_aggregate_range_346 = "".join(["range(168, ", "34", "6", ")"])`
- Include `stale_aggregate_range_346` in the stale aggregate tuple.
- Preserve existing stale aggregate guards, the single-assignment guard, and no-discovery-token guards.

## Tests / Verification

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-24-hermes-tavern-phase346-attention-status-sync-through-phase345 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider
git diff --check
```

Optional broader check when feasible:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider
```

## Executor Prompt

Implement only Phase 346 S1 for `2026-06-24-hermes-tavern-phase346-attention-status-sync-through-phase345`. Touch exactly the four allowed files listed in this design. Preserve all prior phase labels by copying literal text from current files; do not formula-generate labels. Update attention and the focused status test from Phase 345 to Phase 346, add the split stale aggregate guard for `range(168, 346)`, move only the terminal conjunction, keep checklist statuses non-final with parent verification required, and do not create `acceptance.md` or Phase 347. Run the listed verification commands and report real results. Do not commit, stage, or push.
