---
doc_type: feature-design
feature: 2026-06-24-hermes-tavern-phase343-attention-status-sync-through-phase342
status: approved
implementation_ready: true
date: "2026-06-24"
owner: standard_lane
lane: standard/personal
bounded_phase: "docs/static-test/status-only"
summary: "Implementation-ready Phase 343 attention/status sync through accepted Phase 342."
tags: [hermes-tavern, codestable, attention, status-sync, docs, tests, phase343]
---

# Phase 343: Attention Status Sync Through Phase 342

## Background / Current Status

Phase 342 is the latest accepted phase. Its acceptance report exists at `design/codestable/features/2026-06-24-hermes-tavern-phase342-attention-status-sync-through-phase341/acceptance.md` with `status: accepted`, and it explicitly identifies Phase 343 attention/status sync through Phase 342 as the next safe recurring slice.

Current live status artifacts are at the Phase 342 contract:

- `design/codestable/attention.md` reports `Current status (2026-06-18): All phases 1-342 accepted`.
- The terminal status label is `Phase 342 attention status sync through Phase 341`.
- `tests/test_hermes_tavern_codestable_status.py` uses `CURRENT_STATUS_PREFIX` for `1-342`, `phase_range = range(168, 343)`, and `aggregate_range = "range(168, 343)"`.
- No Phase 343 feature directory is present.

Inspection note: a focused pytest probe was blocked before collection by the read-only sandbox having no usable temporary directory. This is sandbox noise, not an observed test assertion failure; file inspection is sufficient for this planning slice.

## Goals

- Create the Phase 343 feature design/checklist artifacts.
- Advance `design/codestable/attention.md` exactly one status tick from 1-342 to 1-343.
- Add terminal label `Phase 343 attention status sync through Phase 342`.
- Update `tests/test_hermes_tavern_codestable_status.py` so the static regression guards the Phase 343 live status contract.
- Preserve all historical labels, including `Phase 121-167` and explicit Phase 168 through Phase 342 labels.

## Non-Goals

- No runtime, source, plugin, provider, gateway, CLI, dependency, config, root README, root design, architecture, roadmap, requirements, or compound changes.
- No Hermes-native plugin architecture changes.
- No SillyTavern asset compatibility changes.
- No adult-fiction/RP behavior changes.
- No minors-related work and no provider safety bypass.
- No service lifecycle commands.
- No dependency installation.
- No commits, staging, or pushes.
- Executor S1 must not create or finalize `acceptance.md`.

## Exact Allowed Files

Executor S1 may touch exactly these files:

- `design/codestable/features/2026-06-24-hermes-tavern-phase343-attention-status-sync-through-phase342/design.md`
- `design/codestable/features/2026-06-24-hermes-tavern-phase343-attention-status-sync-through-phase342/checklist.yaml`
- `design/codestable/attention.md`
- `tests/test_hermes_tavern_codestable_status.py`

Controller S2 may additionally create only after verification:

- `design/codestable/features/2026-06-24-hermes-tavern-phase343-attention-status-sync-through-phase342/acceptance.md`

## Prohibited Files / Areas

All files not listed above are prohibited for executor S1, including:

- `plugins/`
- `hermes/`
- `runtime/`
- provider, gateway, CLI, config, and dependency files
- root docs and root design docs
- `design/codestable/architecture/`
- `design/codestable/roadmap/`
- `design/codestable/requirements/`
- `design/codestable/compound/`
- any generated cache, build, or service lifecycle artifact

## Implementation Steps

1. Materialize this Phase 343 `design.md` and matching `checklist.yaml` under `design/codestable/features/2026-06-24-hermes-tavern-phase343-attention-status-sync-through-phase342/`.
2. Update the single current status line in `design/codestable/attention.md`:
   - from `Current status (2026-06-18): All phases 1-342 accepted`
   - to `Current status (2026-06-18): All phases 1-343 accepted`
   - preserve all existing labels and append `Phase 343 attention status sync through Phase 342`.
   - update the final conjunction so the suffix ends with `Phase 341 attention status sync through Phase 340, Phase 342 attention status sync through Phase 341, and Phase 343 attention status sync through Phase 342.`
3. Update `tests/test_hermes_tavern_codestable_status.py`:
   - `CURRENT_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-343 accepted"`
   - `STALE_STATUS_PREFIX = "Current status (2026-06-18): All phases 1-342 accepted"`
   - `STALE_PHASE_MARKER = "1-342"`
   - `STALE_PHASE_MARKER_EN_DASH = "1–342"`
   - add `Phase 343 attention status sync through Phase 342` to `REQUIRED_PHASE_LABELS`.
   - update `FINAL_STATUS_SUFFIX` to the Phase 341 / Phase 342 / Phase 343 suffix.
   - update `phase_range = range(168, 344)`.
   - update `aggregate_range = "range(168, 344)"`.
   - add a split stale aggregate guard for `range(168, 343)` without leaving that contiguous stale literal in the test source.
   - preserve existing stale aggregate guards, the single-assignment guard, and no-discovery-token guards.
4. Do not create `acceptance.md` in S1.
5. Run verification commands when the environment permits; report sandbox temp/cache failures as sandbox noise.

## Review Checklist

- Phase 342 acceptance exists and is `accepted`.
- No Phase 343 artifact already exists before S1.
- Only the four S1 allowed files changed.
- `attention.md` has exactly one current status line.
- `attention.md` starts with `All phases 1-343 accepted`.
- `attention.md` contains `Phase 343 attention status sync through Phase 342` exactly once.
- `attention.md` preserves `Phase 121-167` and every explicit Phase 168 through Phase 342 label.
- The status test constants, labels, suffix, phase range, and aggregate range match the Phase 343 contract.
- The stale `range(168, 343)` aggregate is guarded only via split string construction.
- Runtime/source/plugin/provider/gateway/CLI/dependency/config/root-doc areas are untouched.
- No acceptance report is created during executor S1.

## Verification Commands

```bash
PYTHONDONTWRITEBYTECODE=1 python design/codestable/tools/validate-yaml.py --dir design/codestable/features/2026-06-24-hermes-tavern-phase343-attention-status-sync-through-phase342 --require doc_type --require status --require feature
PYTHONDONTWRITEBYTECODE=1 python -m py_compile tests/test_hermes_tavern_codestable_status.py
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest tests/test_hermes_tavern_codestable_status.py -q -o addopts= -p no:cacheprovider
git diff --check
```

Optional broader check when feasible:

```bash
PYTHONDONTWRITEBYTECODE=1 python -m pytest -q -o addopts= -p no:cacheprovider
```
