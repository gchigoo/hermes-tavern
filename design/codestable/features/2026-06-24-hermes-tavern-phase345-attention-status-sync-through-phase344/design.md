---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase345-attention-status-sync-through-phase344
status: approved
implementation_ready: true
date: "2026-06-24"
owner: company_boost_lane
lane: company-boost
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready Phase 345 attention/status sync through accepted Phase 344."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase345]
---

# Phase 345: Attention Status Sync Through Phase 344

## Background / Current Status

Phase 344 is the latest accepted phase. Its acceptance report exists at `design/codestable/features/2026-06-24-hermes-tavern-phase344-attention-status-sync-through-phase343/acceptance.md` with `status: accepted`, and the current live CodeStable startup/status contract is synced through Phase 344:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-344 accepted`.
- The current terminal label is `Phase 344 attention status sync through Phase 343`.
- `tests/test_hermes_tavern_codestable_status.py` uses `CURRENT_STATUS_PREFIX` for `1-344`, `phase_range = range(168, 345)`, and `aggregate_range = "range(168, 345)"`.
- No Phase 345 feature directory existed before this slice was selected.

The read-only architect pass selected a non-final S1 status-sync handoff for Phase 345 rather than an S2 closeout.

## Goals

- Create the Phase 345 feature design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-344 to 1-345.
- Add terminal label `Phase 345 attention status sync through Phase 344`.
- Update `tests/test_hermes_tavern_codestable_status.py` so the static regression guards the Phase 345 live status contract.
- Preserve all historical labels exactly as literal text from the current files, including `Phase 121-167` and every explicit Phase 168 through Phase 344 label.

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
- Do not create Phase 346.

## Exact Allowed Files

Executor S1 may touch exactly these files:

- `design/codestable/features/2026-06-24-hermes-tavern-phase345-attention-status-sync-through-phase344/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase345-attention-status-sync-through-phase344/checklist.yaml`
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

## Implementation Steps

1. Keep this Phase 345 `design.md` and matching `checklist.yaml` under `design/codestable/features/2026-06-24-hermes-tavern-phase345-attention-status-sync-through-phase344/`.
2. Update the single current status line in `design/codestable/attention.md`:
   - from `Current status (2026-06-18): All phases 1-344 accepted`
   - to `Current status (2026-06-18): All phases 1-345 accepted`
   - preserve all existing labels exactly and append `Phase 345 attention status sync through Phase 344`.
   - update the final conjunction so the suffix ends with `Phase 343 attention status sync through Phase 342, Phase 344 attention status sync through Phase 343, and Phase 345 attention status sync through Phase 344.`
3. Update `tests/test_hermes_tavern_codestable_status.py`:
   - `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-345 accepted"`
   - `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-344 accepted"`
   - `STALE_PHASE_MARKER = "1-344"`
   - `STALE_PHASE_MARKER_EN_DASH = "1–344"`
   - add `Phase 345 attention status sync through Phase 344` to `REQUIRED_PHASE_LABELS` exactly once.
   - update `FINAL_STATUS_SUFFIX` to the Phase 343 / Phase 344 / Phase 345 suffix above.
   - update `phase_range = range(168, 346)`.
   - update `aggregate_range = "range(168, 346)"`.
   - add a split stale aggregate guard for `range(168, 345)` without leaving that contiguous stale literal in the test source.
   - preserve existing stale aggregate guards, the single-assignment guard, and no-discovery-token guards.
4. Do not create `acceptance.md` in this S1 slice.
5. Run verification commands when the environment permits and report real results.

## Tests / Verification

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-24-hermes-tavern-phase345-attention-status-sync-through-phase344 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider
git diff --check
```

Optional broader check when feasible:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider
```

## Risks

- Regenerating or shortening historical phase labels instead of preserving exact current text.
- Leaving `and Phase 344...` in place instead of moving the terminal conjunction to Phase 345.
- Leaving a contiguous stale `range(168, 345)` literal in the test source while also trying to guard it.
- Accidentally creating `acceptance.md`, Phase 346, or runtime/source changes during an S1-only handoff.

## Executor Prompt

Implement only Phase 345 S1 for `2026-06-24-hermes-tavern-phase345-attention-status-sync-through-phase344`. Touch exactly the four allowed files listed in this design. Preserve all prior phase labels by copying literal text from current files; do not formula-generate labels. Update attention and the focused status test from Phase 344 to Phase 345, add the split stale aggregate guard for `range(168, 345)`, move only the terminal conjunction, keep checklist statuses non-final with parent verification required, and do not create `acceptance.md` or Phase 346. Run the listed verification commands and report results.
